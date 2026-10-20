"""Export a research table and static figure from verified per-image evidence."""
import csv
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/research'


def main():
    source = (OUT / 'phone-comparison.json').read_bytes()
    comparison = json.loads(source)
    bootstrap = json.loads((OUT / 'phone-bootstrap.json').read_text())
    assert bootstrap['input_sha256'] == hashlib.sha256(source).hexdigest(), 'Bootstrap is from different comparison'
    rows = []
    for checkpoint, result in comparison['models'].items():
        for metric in ('precision', 'recall', 'f1'):
            ci = bootstrap['models'][checkpoint][metric]
            assert abs(ci['estimate'] - result[metric]) < 1e-12
            rows.append(dict(model=Path(checkpoint).parent.parent.name, metric=metric,
                estimate_percent=100*ci['estimate'], ci95_low_percent=100*ci['low'],
                ci95_high_percent=100*ci['high'], tp=result['tp'], fp=result['fp'], fn=result['fn']))
    with (OUT / 'phone-metrics.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.4), sharey=True)
    names = list(bootstrap['models'])
    for axis, metric in zip(axes, ('precision', 'recall', 'f1')):
        for i, checkpoint in enumerate(names):
            ci = bootstrap['models'][checkpoint][metric]
            low, high, value = 100*ci['low'], 100*ci['high'], 100*ci['estimate']
            axis.vlines(i, low, high, color=['#64748b', '#0d9488'][i % 2], linewidth=2)
            axis.scatter(i, value, color=['#64748b', '#0d9488'][i % 2], s=45, zorder=3)
            axis.text(i, high+3, f'{value:.1f}%', ha='center', fontsize=10)
        axis.set(title=metric.capitalize(), xticks=range(len(names)),
                 xticklabels=['v2', 'v3 Colab'], xlim=(-.5, len(names)-.5), ylim=(0, 85))
        axis.grid(axis='y', alpha=.2)
        axis.spines[['top', 'right']].set_visible(False)
    axes[0].set_ylabel('Score (%)')
    fig.suptitle('Phone detector comparison: 214 validation images', fontsize=14)
    fig.text(.5, .03, '95% paired image bootstrap intervals (2,000 resamples). Validation used for model selection; not an independent exam test.',
             ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .09, 1, .92))
    fig.savefig(OUT / 'phone-benchmark.png', dpi=180)
    fig.savefig(OUT / 'phone-benchmark.pdf')
    plt.close(fig)
    lines = ['# Kết quả so sánh detector điện thoại', '',
        '214 ảnh validation, 262 đối tượng phone; confidence 0,30, IoU matching 0,50, NMS IoU 0,45, imgsz 640, CPU.', '',
        '| Checkpoint | Chỉ số | Giá trị | Khoảng bootstrap 95% |', '|---|---|---:|---:|']
    for row in rows:
        lines.append(f"| {row['model']} | {row['metric']} | {row['estimate_percent']:.2f}% | {row['ci95_low_percent']:.2f}–{row['ci95_high_percent']:.2f}% |")
    lines += ['', '## Diễn giải có giới hạn', '',
        'Các con số so sánh hai checkpoint cụ thể trên cùng ảnh, không phải thí nghiệm kiểm soát để quy nguyên nhân cải thiện cho một thuật toán: dữ liệu, số epoch và batch của hai lượt khác nhau.',
        'Bootstrap lấy mẫu lại cả ảnh và giữ cặp kết quả hai model cùng nhau; 2.000 lần, seed 42, percentile 2,5/97,5. Thống kê là micro precision/recall/F1 từ tổng TP/FP/FN, không phải trung bình F1 từng ảnh. Trường hợp mẫu số 0 được quy ước bằng 0.',
        'Khoảng này chỉ phản ánh biến thiên có điều kiện trên tập ảnh đã có. Giả định ảnh độc lập chưa được kiểm chứng theo người/cảnh. Không đo bất định do lần train, lỗi nhãn, hoặc thay đổi miền phòng thi. Tập validation dùng chọn best checkpoint nên đây không phải ước lượng trên held-out test hoàn toàn độc lập.',
        'Phương pháp lấy mẫu ghép cặp và percentile tham khảo [tài liệu SciPy bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html). Đây là phân tích thăm dò; không phải kiểm định giả thuyết được đăng ký trước.', '',
        '## Tái lập', '',
        'Chạy từ thư mục dự án:', '```powershell',
        '.\\venv\\Scripts\\python.exe scripts/compare_phone_v3.py --models models/phone_v2/weights/best.pt models/phone_v3_colab/weights/best.pt --output artifacts/research/phone-comparison.json',
        '.\\venv\\Scripts\\python.exe scripts/bootstrap_phone_comparison.py --input artifacts/research/phone-comparison.json',
        '.\\venv\\Scripts\\python.exe scripts/report_phone_benchmark.py', '```', '',
        'phone-comparison.json lưu checksum ảnh/nhãn/checkpoint/mã đánh giá, phiên bản runtime, bbox dự đoán, nhãn và TP/FP/FN từng ảnh. phone-bootstrap.json gắn checksum đúng tệp kết quả. CSV/PNG/PDF được tạo từ hai tệp này; không chạy train.']
    (OUT / 'RESULTS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT / 'RESULTS.md')


if __name__ == '__main__':
    main()
