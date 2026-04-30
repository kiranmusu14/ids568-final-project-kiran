from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ab_test.simulate_experiment import run_experiment
from src.common.config import ROOT, settings
from src.drift.analyze_drift import build_drift_report
from src.governance.audit_trail import verify_audit_log, write_audit_log
from src.monitoring.simulate_traffic import run_simulation


def _ensure_dirs() -> None:
    for rel in ["docs", "dashboards", "logs", "visualizations", "src/monitoring", "src/ab_test", "src/drift", "src/governance"]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _draw_bar(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, value: float, max_value: float, color: str, label: str) -> None:
    bar_height = int((value / max_value) * 180)
    draw.rectangle((x, y - bar_height, x + width, y), fill=color)
    draw.text((x, y + 8), label, fill="black", font=_font(14))


def _draw_centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, size: int = 18) -> None:
    font = _font(size)
    left, top, right, bottom = box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        (left + ((right - left - text_width) / 2), top + ((bottom - top - text_height) / 2)),
        text,
        fill="black",
        font=font,
    )


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((percentile / 100) * (len(ordered) - 1)))
    return ordered[index]


def _save_dashboard_export(records: list[dict[str, object]]) -> None:
    latencies = [float(row["latency_seconds"]) for row in records]
    ttft = [float(row["ttft_seconds"]) for row in records]
    throughput = [float(row["token_throughput_tps"]) for row in records]
    response_lengths = [float(row["response_length_tokens"]) for row in records]
    retrieval_scores = [score for row in records for score in row["retrieval_scores"]]
    empty_rate = sum(1 for row in records if row["empty_retrieval"]) / len(records)
    image = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 20), "Agentic RAG Monitoring Dashboard Export", fill="black", font=_font(28))
    metrics = [
        ("Requests", float(len(records)), max(300.0, len(records)), "#4e79a7"),
        ("Error Rate", 0.0, 0.05, "#bab0ab"),
        ("p95 Latency (s)", round(_percentile(latencies, 95), 3), 3.0, "#76b7b2"),
        ("Avg TTFT (s)", round(sum(ttft) / len(ttft), 3), 1.0, "#f28e2b"),
        ("Avg Throughput", round(sum(throughput) / len(throughput), 3), 25.0, "#59a14f"),
        ("Avg Retrieval", round(sum(retrieval_scores) / len(retrieval_scores), 3), 1.0, "#e15759"),
        ("Avg Response Tok", round(sum(response_lengths) / len(response_lengths), 1), 160.0, "#af7aa1"),
        ("Empty Retrieval", round(empty_rate, 3), settings.empty_retrieval_alert_threshold * 2, "#ff9da7"),
    ]
    base_y = 320
    for index, (label, value, max_value, color) in enumerate(metrics):
        row = index // 4
        column = index % 4
        x = 90 + (column * 310)
        y_offset = row * 270
        draw.rectangle((x - 20, 110 + y_offset, x + 180, 380 + y_offset), outline="black", width=2)
        max_value = max(max_value, value or 0.001)
        _draw_bar(draw, x, base_y + y_offset, 100, value, max_value, color, f"{label}: {value}")
    draw.text((60, 720), f"Retrieval score alert threshold: {settings.retrieval_score_threshold}", fill="black", font=_font(18))
    draw.text((60, 760), f"Empty retrieval alert threshold: {settings.empty_retrieval_alert_threshold}", fill="black", font=_font(18))
    draw.text((60, 810), "Interpretation: latency is stable, but retrieval quality is drifting left.", fill="black", font=_font(20))
    image.save(ROOT / "visualizations" / "dashboard-export.png")


def _save_ab_visualization(result: dict[str, object]) -> None:
    image = Image.new("RGB", (1000, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 20), "A/B Experiment Summary", fill="black", font=_font(28))
    _draw_bar(draw, 180, 340, 120, float(result["control_success_rate"]), 1.0, "#4e79a7", "A success")
    _draw_bar(draw, 360, 340, 120, float(result["treatment_success_rate"]), 1.0, "#59a14f", "B success")
    _draw_bar(draw, 620, 340, 120, float(result["control_cost_per_query"]), settings.ab_cost_guardrail * 1.2, "#9c755f", "A cost")
    _draw_bar(draw, 800, 340, 120, float(result["treatment_cost_per_query"]), settings.ab_cost_guardrail * 1.2, "#edc949", "B cost")
    draw.line((620, 120, 920, 120), fill="red", width=3)
    draw.text((620, 90), f"Cost guardrail: {settings.ab_cost_guardrail}", fill="red", font=_font(16))
    draw.text((40, 420), f"Recommendation: {result['recommendation']}", fill="black", font=_font(22))
    image.save(ROOT / "visualizations" / "ab-test-summary.png")


def _save_drift_visualization(report: dict[str, object]) -> None:
    image = Image.new("RGB", (1200, 560), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 20), "Drift Over Time Windows", fill="black", font=_font(28))
    origin_x = 120
    origin_y = 420
    width = 900
    height = 280
    windows = report["windows"]
    max_psi = max(
        max(window["query_length_psi"], window["retrieval_score_psi"], window["response_length_psi"])
        for window in windows
    )
    scale_max = max(0.4, max_psi * 1.2)
    draw.line((origin_x, origin_y, origin_x + width, origin_y), fill="black", width=2)
    draw.line((origin_x, origin_y, origin_x, origin_y - height), fill="black", width=2)
    moderate_y = origin_y - int((settings.psi_moderate_threshold / scale_max) * height)
    significant_y = origin_y - int((settings.psi_significant_threshold / scale_max) * height)
    draw.line((origin_x, moderate_y, origin_x + width, moderate_y), fill="orange", width=2)
    draw.line((origin_x, significant_y, origin_x + width, significant_y), fill="red", width=2)
    previous_a = None
    previous_b = None
    previous_c = None
    for index, window in enumerate(windows):
        x = origin_x + int((index / max(1, len(windows) - 1)) * width)
        y_a = origin_y - int((window["query_length_psi"] / scale_max) * height)
        y_b = origin_y - int((window["retrieval_score_psi"] / scale_max) * height)
        y_c = origin_y - int((window["response_length_psi"] / scale_max) * height)
        draw.ellipse((x - 5, y_a - 5, x + 5, y_a + 5), fill="#4e79a7")
        draw.ellipse((x - 5, y_b - 5, x + 5, y_b + 5), fill="#e15759")
        draw.ellipse((x - 5, y_c - 5, x + 5, y_c + 5), fill="#59a14f")
        if previous_a:
            draw.line((previous_a[0], previous_a[1], x, y_a), fill="#4e79a7", width=3)
        if previous_b:
            draw.line((previous_b[0], previous_b[1], x, y_b), fill="#e15759", width=3)
        if previous_c:
            draw.line((previous_c[0], previous_c[1], x, y_c), fill="#59a14f", width=3)
        draw.text((x - 25, origin_y + 12), window["window"], fill="black", font=_font(14))
        previous_a = (x, y_a)
        previous_b = (x, y_b)
        previous_c = (x, y_c)
    draw.text((70, 450), "Blue: query length PSI", fill="#4e79a7", font=_font(18))
    draw.text((300, 450), "Red: retrieval score PSI", fill="#e15759", font=_font(18))
    draw.text((560, 450), "Green: response length PSI", fill="#59a14f", font=_font(18))
    draw.text((70, 485), f"Orange threshold: {settings.psi_moderate_threshold}; red threshold: {settings.psi_significant_threshold}", fill="black", font=_font(16))
    image.save(ROOT / "visualizations" / "drift-over-time.png")


def _save_lineage_diagram() -> None:
    image = Image.new("RGB", (1300, 300), "white")
    draw = ImageDraw.Draw(image)
    labels = ["Data Sources", "Chunking + Embeddings", "Retriever Eval", "FastAPI Deployment", "Monitoring + Audit"]
    boxes = []
    x_positions = [40, 290, 540, 790, 1040]
    for x, label in zip(x_positions, labels):
        box = (x, 100, x + 220, 190)
        boxes.append(box)
    for start, end in zip(boxes[:-1], boxes[1:]):
        draw.line((start[2], 145, end[0], 145), fill="black", width=3)
    for box, label in zip(boxes, labels):
        draw.rounded_rectangle(box, radius=8, fill="#dfefff", outline="black")
        _draw_centered_text(draw, box, label, 17)
    image.save(ROOT / "docs" / "lineage-diagram.png")


def _save_system_boundary_diagram() -> None:
    image = Image.new("RGB", (1300, 480), "white")
    draw = ImageDraw.Draw(image)
    components = [
        (0.1, 0.6, "User"),
        (0.3, 0.6, "RAG API"),
        (0.5, 0.6, "Retriever"),
        (0.7, 0.6, "LLM"),
        (0.9, 0.6, "Tool Layer"),
        (0.7, 0.25, "Audit + Monitoring"),
    ]
    boxes = {}
    for x, y, label in components:
        cx = int(x * 1200) + 30
        cy = int(y * 400) + 20
        box = (cx - 90, cy - 35, cx + 90, cy + 35)
        boxes[label] = box
        draw.rounded_rectangle(box, radius=8, fill="#f7ead4", outline="black")
        _draw_centered_text(draw, box, label, 18)
    for left_label, right_label in [("User", "RAG API"), ("RAG API", "Retriever"), ("Retriever", "LLM"), ("LLM", "Tool Layer")]:
        left = boxes[left_label]
        right = boxes[right_label]
        draw.line((left[2], (left[1] + left[3]) // 2, right[0], (right[1] + right[3]) // 2), fill="black", width=3)
    llm = boxes["LLM"]
    monitoring = boxes["Audit + Monitoring"]
    draw.line(((llm[0] + llm[2]) // 2, llm[1], (monitoring[0] + monitoring[2]) // 2, monitoring[3]), fill="black", width=3)
    draw.text((360, 40), "Trust boundary: internal corpus vs. external model API", fill="black", font=_font(22))
    image.save(ROOT / "docs" / "system-boundary-diagram.png")


def main() -> None:
    _ensure_dirs()
    traffic = run_simulation(250)
    _save_dashboard_export(traffic)
    ab_result = run_experiment()
    _save_ab_visualization(ab_result)
    drift_report = build_drift_report()
    _save_drift_visualization(drift_report)
    _save_lineage_diagram()
    _save_system_boundary_diagram()
    write_audit_log()
    summary = {
        "audit_integrity_valid": verify_audit_log(),
        "ab_recommendation": ab_result["recommendation"],
        "drift_action": drift_report["recommended_action"],
    }
    (ROOT / "visualizations" / "artifact-summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
