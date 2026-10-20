import asyncio
import sys
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch, AsyncMock

import cv2
import numpy as np
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import fastapi_server as server


class APITests(unittest.TestCase):
    def test_configured_model_is_not_reported_as_loaded(self):
        metrics = server.AppState().metrics()
        self.assertEqual(metrics['model']['status'], 'not_loaded')
        self.assertIsNone(metrics['model']['loaded_phone'])
        self.assertIsNone(metrics['warning'])

    def test_model_failure_reports_actual_fallback_even_when_file_exists(self):
        state = server.AppState()
        state.model.update(status='fallback', detector='YOLO-World', error='Invalid checkpoint')
        metrics = state.metrics()
        self.assertIn('YOLO-World', metrics['warning'])
        self.assertIn('Invalid checkpoint', metrics['warning'])
        self.assertIsNone(metrics['model']['loaded_phone'])

    def test_loaded_model_is_in_status_response(self):
        server.state.model.update(status='loaded', detector='YOLO-World',
                                  loaded_phone=server.YOLO_PHONE_CONFIRM_MODEL)
        with TestClient(server.app) as client:
            metrics = client.get('/status').json()
            self.assertEqual(metrics['model']['status'], 'loaded')
            self.assertEqual(metrics['model']['loaded_phone'], server.YOLO_PHONE_CONFIRM_MODEL)
            self.assertIsNone(metrics['warning'])

    def test_slow_websocket_does_not_block_healthy_client(self):
        async def scenario():
            manager = server.ConnectionManager()
            slow, healthy = Mock(), Mock()
            slow.accept = healthy.accept = AsyncMock()
            blocked = asyncio.Event()
            slow.send_json = AsyncMock(side_effect=lambda message: None)
            async def stall(message):
                await blocked.wait()
            slow.send_json.side_effect = stall
            healthy.send_json = AsyncMock()
            await manager.connect(slow)
            await manager.connect(healthy)
            with patch.object(server, 'WS_SEND_TIMEOUT', .02):
                await asyncio.wait_for(manager.broadcast({'type': 'PHONE_DETECTED'}), .5)
            healthy.send_json.assert_awaited_once()
            self.assertNotIn(slow, manager.connections)
            self.assertIn(healthy, manager.connections)
        asyncio.run(scenario())

    def setUp(self):
        self.state_patch = patch.object(server, 'state', server.AppState())
        self.state_patch.start()

    def tearDown(self):
        server.state.stop_event.set()
        if server.state.worker:
            server.state.worker.join(5)
        self.state_patch.stop()

    def test_startup_status_and_websocket(self):
        with TestClient(server.app) as client:
            self.assertTrue(server.state.loop.is_running())
            self.assertEqual(client.get('/status').json()['status'], 'stopped')
            with client.websocket_connect('/ws/alerts') as ws:
                metrics = ws.receive_json()
                self.assertTrue(metrics['heartbeat'])
                self.assertFalse(metrics['running'])
                self.assertEqual(metrics['fps'], 0)
                message = {'type': 'PHONE_DETECTED', 'timestamp': time.time(), 'score': 12}
                asyncio.run_coroutine_threadsafe(server.manager.broadcast(message), server.state.loop).result(3)
                self.assertEqual(ws.receive_json(), message)

    def test_concurrent_start_has_one_worker(self):
        entered = threading.Event()
        def worker():
            entered.set()
            server.state.stop_event.wait(3)
        with patch.object(server, 'detection_thread', side_effect=worker) as target:
            callers = [threading.Thread(target=server.ensure_started) for _ in range(8)]
            for caller in callers:
                caller.start()
            for caller in callers:
                caller.join()
            self.assertTrue(entered.wait(1))
            self.assertEqual(target.call_count, 1)
            server.state.stop_event.set()
            with self.assertRaises(server.HTTPException):
                # A still-running worker cannot be replaced during stop.
                with patch.object(server.state.worker, 'is_alive', return_value=True):
                    server.ensure_started()

    def test_camera_failure_is_visible_and_releases_capture(self):
        cap = Mock()
        cap.isOpened.return_value = False
        with patch.object(server.cv2, 'VideoCapture', return_value=cap), TestClient(server.app) as client:
            client.post('/start')
            server.state.worker.join(3)
            status = client.get('/status').json()
            self.assertFalse(status['running'])
            self.assertEqual(status['status'], 'error')
            self.assertTrue(status['error'])
            cap.release.assert_called()

    def test_model_failure_is_visible_and_releases_capture(self):
        cap = Mock()
        cap.isOpened.return_value = True
        with patch.object(server.cv2, 'VideoCapture', return_value=cap), \
             patch.object(server, 'create_components', side_effect=RuntimeError('Missing pose model')):
            server.detection_thread()
        self.assertEqual(server.state.error, 'Missing pose model')
        self.assertFalse(server.state.running)
        cap.release.assert_called_once()

    def test_video_to_alert_snapshot_and_cleanup(self):
        # Real OpenCV decoding/encoding and FusionEngine; model output is controlled.
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            video = str(temp / 'input.avi')
            writer = cv2.VideoWriter(video, cv2.VideoWriter_fourcc(*'MJPG'), 10, (640, 480))
            self.assertTrue(writer.isOpened())
            for _ in range(12):
                writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
            writer.release()
            detector, analyzer, logger = Mock(), Mock(), Mock()
            detector.detect.return_value = [dict(label='cell phone', confidence=0.9,
                bbox=(10, 10, 60, 100), is_cheat=True)]
            analyzer.analyze.return_value = {}
            analyzer.draw.side_effect = lambda frame, analysis: frame
            with patch.object(server, 'VIDEO_SOURCE', video), \
                 patch.object(server, 'SNAPSHOT_DIR', temp), \
                 patch.object(server, 'create_components', return_value=(detector, analyzer)), \
                 patch.object(server, 'AlertLogger', return_value=logger), \
                 TestClient(server.app) as client:
                with client.websocket_connect('/ws/alerts') as ws:
                    self.assertTrue(ws.receive_json()['heartbeat'])
                    client.post('/start')
                    message = ws.receive_json()
                    while message.get('heartbeat'):
                        message = ws.receive_json()
                    self.assertEqual(message['type'], 'PHONE_DETECTED')
                    self.assertIsNotNone(message['image'])
                    server.state.worker.join(5)
                    self.assertFalse(server.state.worker.is_alive())
                    self.assertEqual(client.get('/status').json()['status'], 'stopped')
            self.assertEqual(detector.detect.call_count, 12)  # 10 FPS input, 10 Hz detection
            logger.log.assert_called_once()
            logger.close.assert_called_once()
            analyzer.close.assert_called_once()
            self.assertEqual(len(list(temp.glob('PHONE_DETECTED_*.jpg'))), 1)
            self.assertIsNone(server.state.latest_jpeg)

    def test_snapshot_route_and_no_camera_autostart(self):
        with TestClient(server.app) as client:
            self.assertEqual(client.get('/snapshots/does-not-exist.jpg').status_code, 404)
            self.assertEqual(client.get('/video_feed').content, b'')
            self.assertIsNone(server.state.worker)

    def test_demo_video_catalog_and_source_selection(self):
        with TestClient(server.app) as client:
            catalog = client.get('/demo/videos')
            self.assertEqual(catalog.status_code, 200)
            catalog_body = catalog.json()
            videos = catalog_body['videos']
            self.assertEqual(len(videos), 6)
            self.assertEqual(videos[0]['filename'], '01_binh_thuong.mp4.mp4')
            self.assertEqual(catalog_body['camera']['kind'], 'camera')
            self.assertEqual(catalog_body['camera']['index'], 0)

            selected = client.post('/source', json={'filename': videos[4]['filename']})
            self.assertEqual(selected.status_code, 200)
            self.assertEqual(selected.json()['source']['name'], videos[4]['filename'])
            self.assertEqual(selected.json()['status'], 'stopped')

            invalid = client.post('/source', json={'filename': '..\\models\\phone_v3_colab\\weights\\best.pt'})
            self.assertEqual(invalid.status_code, 400)

    def test_webcam_source_selection(self):
        with TestClient(server.app) as client:
            selected = client.post('/source', json={'kind': 'camera', 'index': 0})
            self.assertEqual(selected.status_code, 200)
            body = selected.json()
            self.assertEqual(body['source']['kind'], 'camera')
            self.assertEqual(body['source']['index'], 0)
            self.assertEqual(body['source']['name'], 'Webcam 0')
            self.assertEqual(body['status'], 'stopped')

            invalid = client.post('/source', json={'kind': 'camera', 'index': -1})
            self.assertEqual(invalid.status_code, 422)


if __name__ == '__main__':
    unittest.main()
