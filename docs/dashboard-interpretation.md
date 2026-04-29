# Dashboard Interpretation

## Monitoring Stack Design Justification

Prometheus and Grafana were selected as the monitoring stack for three reasons. First, the `prometheus_client` Python library integrates directly into a FastAPI service with no sidecar or agent required, keeping the instrumentation code co-located with the business logic and free of proprietary cloud dependencies. Second, Prometheus's pull-based scraping model decouples the service from the collector: the service exposes a `/metrics` endpoint and Prometheus scrapes it on a configurable interval, which is well-suited to a single-node local deployment without a persistent message queue. Third, Grafana's panel system maps naturally to the metric types used here — Histogram metrics (TTFT, retrieval score, latency) become heatmap or time-series panels, Gauge metrics (token throughput, empty retrieval rate) become stat panels, and Counter metrics (request count, errors) become rate panels. All three tools are OSS with active ML-community adoption, satisfying the no-proprietary-cloud constraint in the project specification.

The dashboard layout follows a left-to-right signal hierarchy: infrastructure health (request rate, error rate, latency) on the left, and RAG-specific quality signals (TTFT, token throughput, retrieval score distribution, response length, query length, and empty retrieval rate) on the right. That ordering surfaces the distinction between serving-layer health and evidence-quality health, which is the core diagnostic split in an agentic RAG system.

## Dashboard Findings

The monitoring dashboard shows an agentic RAG system that is operationally healthy on latency but exposed to retrieval-quality degradation. End-to-end latency remains clustered below two seconds and TTFT is tightly centered near 0.2 seconds, which suggests the serving layer and generation path are not the active bottlenecks. Token throughput is also stable, so the model invocation path looks capacity-consistent rather than compute-starved.

The risk signal comes from retrieval. The exported dashboard shows a visible left-shift in retrieval scores alongside response-length and query-length monitoring that would catch the RAG drift distributions described in Module 8. That combination matters diagnostically because it points to evidence quality drift rather than generic infrastructure instability. If latency were rising at the same time, I would suspect downstream model saturation or network contention. Instead, the system is answering quickly while grounding quality weakens, which is consistent with a stale or incomplete knowledge base, newly emerging user topics, or chunking coverage gaps.

The highest-probability bottleneck is therefore corpus freshness and retrieval coverage, not FastAPI throughput. In production I would trigger an alert under three conditions:

1. p95 TTFT exceeds the configured bucket range for two consecutive windows.
2. Empty retrieval rate exceeds `0.15`, indicating a material increase in unanswered or weakly grounded queries.
3. Retrieval-score PSI crosses the significant threshold, signaling structural change in what the retriever is matching.

The operational recommendation is to treat retrieval degradation as a first-class incident. The immediate response would be to audit recent failed topics, refresh the indexed corpus, and compare chunking parameters before considering model changes. That preserves the Module 8 distinction between observable operations metrics and slower evaluated quality review.
