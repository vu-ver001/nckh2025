"""Create a poster-style chart from the phone_v3_colab validation artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ERROR_ANALYSIS = ROOT / "artifacts" / "research" / "error-analysis" / "summary.json"
COMPARISON = ROOT / "artifacts" / "phone-colab-comparison.json"
OUTPUT_DIR = ROOT / "outputs"
PNG = OUTPUT_DIR / "phone_v3_detection_recall_chart.png"
SVG = OUTPUT_DIR / "phone_v3_detection_recall_chart.svg"
PDF = OUTPUT_DIR / "phone_v3_detection_recall_chart.pdf"
CSV = OUTPUT_DIR / "phone_v3_detection_recall_chart.csv"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def load_data() -> list[dict[str, object]]:
    size_report = json.loads(ERROR_ANALYSIS.read_text(encoding="utf-8"))
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    colab_key = next(
        key for key in comparison["models"] if "phone_v3_colab" in key
    )
    overall = comparison["models"][colab_key]

    rows = []
    for label, item in size_report["by_size"].items():
        rows.append(
            {
                "label": label,
                "detected": int(item["detected"]),
                "missed": int(item["missed"]),
                "total": int(item["gt"]),
                "recall": float(item["recall"]),
            }
        )

    total = int(overall["tp"] + overall["fn"])
    rows.append(
        {
            "label": "Tổng validation",
            "detected": int(overall["tp"]),
            "missed": int(overall["fn"]),
            "total": total,
            "recall": float(overall["recall"]),
        }
    )
    return rows


def write_csv(rows: list[dict[str, object]]) -> None:
    with CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["label", "detected", "missed", "total", "recall", "miss_rate"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "miss_rate": 1 - float(row["recall"])})


def draw(rows: list[dict[str, object]]) -> None:
    labels = [str(row["label"]) for row in rows]
    detected = np.array([float(row["recall"]) * 100 for row in rows])
    missed = 100 - detected
    counts = [(int(row["detected"]), int(row["total"])) for row in rows]

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.unicode_minus": False,
            "figure.dpi": 160,
            "savefig.dpi": 300,
        }
    )
    fig = plt.figure(figsize=(14, 8.5), facecolor="#f8fcff")
    fig.subplots_adjust(0, 0, 1, 1)

    # Light panel matching the supplied poster-style reference.
    panel = FancyBboxPatch(
        (0.012, 0.012),
        0.976,
        0.976,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        transform=fig.transFigure,
        facecolor="#f8fcff",
        edgecolor="#b9e2f0",
        linewidth=2.0,
        zorder=-10,
    )
    fig.add_artist(panel)

    # Header.
    icon = FancyBboxPatch(
        (0.045, 0.858),
        0.065,
        0.095,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        transform=fig.transFigure,
        facecolor="#0e6caa",
        edgecolor="none",
    )
    fig.add_artist(icon)
    fig.text(0.0775, 0.898, "↗", ha="center", va="center", fontsize=31,
             color="white", fontweight="bold")
    fig.text(0.13, 0.916, "KẾT QUẢ CHÍNH", ha="left", va="center",
             fontsize=23, color="#123b65", fontweight="bold")
    fig.text(0.365, 0.916, "(đo trên dữ liệu mô hình)", ha="left", va="center",
             fontsize=16, color="#365a73", style="italic")

    bullet_lines = [
        f"Phát hiện đúng {counts[-1][0]}/{counts[-1][1]} điện thoại trên tập validation.",
        f"Recall tăng từ {pct(float(rows[0]['recall']))} (điện thoại nhỏ) lên {pct(float(rows[2]['recall']))} (điện thoại lớn).",
        f"Tổng recall {pct(float(rows[-1]['recall']))}; tỷ lệ bỏ sót {pct(1 - float(rows[-1]['recall']))}.",
    ]
    y_values = [0.818, 0.765, 0.712]
    for y, line in zip(y_values, bullet_lines):
        fig.text(0.060, y, "✓", ha="center", va="center", fontsize=18,
                 color="#10a879", fontweight="bold")
        fig.text(0.085, y, line, ha="left", va="center", fontsize=13.5,
                 color="#274559")

    ax = fig.add_axes([0.115, 0.205, 0.83, 0.39])
    x = np.arange(len(labels))
    width = 0.31
    bars_detected = ax.bar(x - width / 2, detected, width, label="Phát hiện đúng (Recall)",
                           color="#48a9e8", edgecolor="none", zorder=3)
    bars_missed = ax.bar(x + width / 2, missed, width, label="Bỏ sót",
                         color="#0e4c92", edgecolor="none", zorder=3)

    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_ylabel("Tỷ lệ (%)", fontsize=13, color="#1f3c52", labelpad=10)
    ax.set_xlabel("Nhóm kích thước điện thoại (diện tích bbox GT / diện tích ảnh)",
                  fontsize=12.5, color="#1f3c52", labelpad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(["Nhỏ\n<0,25%", "Vừa\n0,25–1%", "Lớn\n≥1%", "Tổng\nvalidation"],
                       fontsize=12, color="#1f3c52")
    ax.set_title("Khả năng phát hiện điện thoại theo kích thước vật thể",
                 fontsize=16, color="#16749b", fontweight="bold", pad=27)
    ax.grid(axis="y", color="#d4e5ee", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#648397")
    ax.spines["bottom"].set_color("#648397")
    ax.tick_params(axis="y", colors="#385466", labelsize=11)
    ax.tick_params(axis="x", length=0, pad=7)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.04), ncol=2,
              frameon=False, fontsize=12.5, handlelength=1.1, columnspacing=2.2)

    for bars, values in ((bars_detected, detected), (bars_missed, missed)):
        for index, (bar, value) in enumerate(zip(bars, values)):
            if bars is bars_detected:
                count_text = f"{counts[index][0]}/{counts[index][1]}"
            else:
                row = rows[index]
                count_text = f"{int(row['missed'])}/{int(row['total'])}"
            ax.text(bar.get_x() + bar.get_width() / 2, value + 2.3,
                    f"{value:.1f}%".replace(".", ",") + f"\n{count_text}",
                    ha="center", va="bottom", fontsize=10.5, color="#23475d",
                    fontweight="bold", linespacing=1.1)

    fig.text(0.115, 0.105,
             "phone_v3_colab · 214 ảnh validation · confidence 0,30 · IoU ghép nhãn 0,50",
             ha="left", va="center", fontsize=11.5, color="#31566a")
    fig.text(0.115, 0.068,
             "Bỏ sót = 1 − recall. Nhóm kích thước là phân tích chẩn đoán theo diện tích bbox nhãn / diện tích ảnh; chưa phải test độc lập phòng thi.",
             ha="left", va="center", fontsize=10.5, color="#607887")

    fig.savefig(PNG, facecolor=fig.get_facecolor(), bbox_inches=None)
    fig.savefig(SVG, facecolor=fig.get_facecolor(), bbox_inches=None)
    fig.savefig(PDF, facecolor=fig.get_facecolor(), bbox_inches=None)
    plt.close(fig)


def main() -> None:
    rows = load_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(rows)
    draw(rows)
    print(PNG)
    print(SVG)
    print(PDF)
    print(CSV)


if __name__ == "__main__":
    main()
