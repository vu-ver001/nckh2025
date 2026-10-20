"""Explicit pose backend selection; failures do not silently change algorithms."""
import os


def create_pose_analyzer():
    backend = os.environ.get('EXAMGUARD_POSE_BACKEND', 'mediapipe').lower()
    if backend == 'yolo':
        from mediapipe_analyzer import MediaPipeAnalyzer
        return MediaPipeAnalyzer()
    if backend == 'mediapipe':
        from mediapipe_tasks_analyzer import MediaPipeTasksAnalyzer
        return MediaPipeTasksAnalyzer()
    raise ValueError(f'Unknown pose backend: {backend}')
