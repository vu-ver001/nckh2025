"""Reconcile completed detector output with the reviewed event manifest.

The detector run is intentionally kept separate from human event labelling.
This utility copies the completed run and recomputes event-level metrics using
the current manifest, so changing a label interval never reruns the detector.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def event_metrics(expected: list[dict], alerts: list[dict]) -> dict:
    detected = 0
    delays: list[float] = []
    for event in expected:
        hits = [
            alert["video_seconds"]
            for alert in alerts
            if alert["type"] == event["type"]
            and event["start"] <= alert["video_seconds"] <= event["end"]
        ]
        if hits:
            detected += 1
            delays.append(min(hits) - event["start"])
    false = [
        alert
        for alert in alerts
        if not any(
            event["type"] == alert["type"]
            and event["start"] <= alert["video_seconds"] <= event["end"]
            for event in expected
        )
    ]
    return {
        "expected_events": len(expected),
        "detected_events": detected,
        "missed_events": len(expected) - detected,
        "false_alerts": len(false),
        "latency_video_seconds": delays,
        "false_alert_details": false,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    labels = {clip["file"]: clip.get("events", []) for clip in manifest["clips"]}

    report = dict(source)
    report["evaluation_source"] = str(args.source.resolve())
    report["label_manifest"] = str(args.manifest.resolve())
    report["label_status"] = manifest.get("label_status", "unspecified")
    report["label_note"] = manifest.get("label_note", "")
    report["reconciliation"] = (
        "Detector alerts are copied from the completed run; event metrics are "
        "recomputed against the reviewed manifest without rerunning inference."
    )

    for clip in report.get("clips", []):
        expected = labels.get(clip["file"])
        if expected is None or clip.get("status") != "evaluated":
            continue
        clip.update(event_metrics(expected, clip.get("alerts", [])))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(args.output)


if __name__ == "__main__":
    main()
