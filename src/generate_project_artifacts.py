from __future__ import annotations

import json

from PIL import Image, ImageDraw, ImageFont

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


def _save_dashboard_export(records: list[dict[str, object]]) -> None:
    latencies = [float(row["latency_seconds"]) for row in records]
    ttft = [float(row["ttft_seconds"]) for row in records]
    throughput = [float(row["token_throughput_tps"]) for row in records]
    retrieval_scores = [score for row in records for score in row["retrieval_scores"]]
    image = Image.new("RGB", (1300, 850), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 20), "Agentic RAG Monitoring Dashboard Export", fill="black", font=_font(28))
    metrics = [
        ("Avg Latency (s)", round(sum(latencies) / len(latencies), 3), 3.0, "#4e79a7"),
        ("Avg TTFT (s)", round(sum(ttft) / len(ttft), 3), 1.0, "#f28e2b"),
        ("Avg Throughput", round(sum(throughput) / len(throughput), 3), 25.0, "#59a14f"),
        ("Avg Retrieval", round(sum(retrieval_scores) / len(retrieval_scores), 3), 1.0, "#e15759"),
    ]
    base_y = 330
    for index, (label, value, max_value, color) in enumerate(metrics):
        x = 90 + (index * 280)
        draw.rectangle((x - 20, 120, x + 150, 380), outline="black", width=2)
        _draw_bar(draw, x, base_y, 100, value, max_value, color, f"{label}: {value}")
    draw.text((60, 450), f"Retrieval score alert threshold: {settings.retrieval_score_threshold}", fill="black", font=_font(18))
    draw.text((60, 490), f"Empty retrieval alert threshold: {settings.empty_retrieval_alert_threshold}", fill="black", font=_font(18))
    draw.text((60, 540), "Interpretation: latency is stable, but retrieval quality is drifting left.", fill="black", font=_font(20))
    image.save(ROOT / "visualizations" / "dashboard-export.png")


def _save_ab_visualization(result: dict[str, object]) -> None:
    image = Image.new("RGB", (1000, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 20), "A/B Experiment Summary", fill="black", font=_font(28))
    _draw_bar(draw, 180, 340, 120, float(result["control_success_rate"]), 1.0, "#4e79a7", "A success")
    _draw_bar(draw, 360, 340, 120, float(result["treatment_success_rate"]), 1.0, "#59a14f", "B success")
    _draw_bar(draw, 620, 340, 120, 0.0116, settings.ab_cost_guardrail * 1.2, "#9c755f", "A cost")
    _draw_bar(draw, 800, 340, 120, float(result["treatment_cost_per_query"]), settings.ab_cost_guardrail * 1.2, "#edc949", "B cost")
    draw.line((620, 120, 920, 120), fill="red", width=3)
    draw.text((620, 90), f"Cost guardrail: {settings.ab_cost_guardrail}", fill="red", font=_font(16))
    draw.text((40, 420), f"Recommendation: {result['recommendation']}", fill="black", font=_font(22))
    image.save(ROOT / "visualizations" / "ab-test-summary.png")


def _save_drift_visualization(report: dict[str, object]) -> None:
    image = Image.new("RGB", (1100, 520), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 20), "Drift Over Time Windows", fill="black", font=_font(28))
    origin_x = 120
    origin_y = 420
    width = 820
    height = 280
    draw.line((origin_x, origin_y, origin_x + width, origin_y), fill="black", width=2)
    draw.line((origin_x, origin_y, origin_x, origin_y - height), fill="black", width=2)
    moderate_y = origin_y - int((settings.psi_moderate_threshold / 0.4) * height)
    significant_y = origin_y - int((settings.psi_significant_threshold / 0.4) * height)
    draw.line((origin_x, moderate_y, origin_x + width, moderate_y), fill="orange", width=2)
    draw.line((origin_x, significant_y, origin_x + width, significant_y), fill="red", width=2)
    windows = report["windows"]
    previous_a = None
    previous_b = None
    for index, window in enumerate(windows):
        x = origin_x + int((index / max(1, len(windows) - 1)) * width)
        y_a = origin_y - int((window["query_length_psi"] / 0.4) * height)
        y_b = origin_y - int((window["retrieval_score_psi"] / 0.4) * height)
        draw.ellipse((x - 5, y_a - 5, x + 5, y_a + 5), fill="#4e79a7")
        draw.ellipse((x - 5, y_b - 5, x + 5, y_b + 5), fill="#e15759")
        if previous_a:
            draw.line((previous_a[0], previous_a[1], x, y_a), fill="#4e79a7", width=3)
        if previous_b:
            draw.line((previous_b[0], previous_b[1], x, y_b), fill="#e15759", width=3)
        draw.text((x - 25, origin_y + 12), window["window"], fill="black", font=_font(14))
        previous_a = (x, y_a)
        previous_b = (x, y_b)
    draw.text((70, 450), "Blue: query length PSI", fill="#4e79a7", font=_font(18))
    draw.text((300, 450), "Red: retrieval score PSI", fill="#e15759", font=_font(18))
    image.save(ROOT / "visualizations" / "drift-over-time.png")


def _save_lineage_diagram() -> None:
    image = Image.new("RGB", (1300, 300), "white")
    draw = ImageDraw.Draw(image)
    labels = ["Data Sources", "Chunking + Embeddings", "Retriever Eval", "FastAPI Deployment", "Monitoring + Audit"]
    x_positions = [0.08, 0.29, 0.5, 0.71, 0.92]
    for x, label in zip(x_positions, labels):
        cx = int(x * 1200) + 30
        draw.rounded_rectangle((cx - 95, 100, cx + 95, 190), radius=15, fill="#dfefff", outline="black")
        draw.text((cx - 70, 135), label, fill="black", font=_font(18))
    for start, end in zip(x_positions[:-1], x_positions[1:]):
        x1 = int((start + 0.07) * 1200) + 30
        x2 = int((end - 0.07) * 1200) + 30
        draw.line((x1, 145, x2, 145), fill="black", width=3)
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
    for x, y, label in components:
        cx = int(x * 1200) + 30
        cy = int(y * 400) + 20
        draw.rounded_rectangle((cx - 90, cy - 35, cx + 90, cy + 35), radius=15, fill="#f7ead4", outline="black")
        draw.text((cx - 60, cy - 8), label, fill="black", font=_font(18))
    arrows = [((0.15, 0.6), (0.25, 0.6)), ((0.35, 0.6), (0.45, 0.6)), ((0.55, 0.6), (0.65, 0.6)), ((0.75, 0.6), (0.85, 0.6))]
    for start, end in arrows:
        x1 = int(start[0] * 1200) + 30
        y1 = int(start[1] * 400) + 20
        x2 = int(end[0] * 1200) + 30
        y2 = int(end[1] * 400) + 20
        draw.line((x1, y1, x2, y2), fill="black", width=3)
    draw.line((870, 228, 870, 340), fill="black", width=3)
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
