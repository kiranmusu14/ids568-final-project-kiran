# Dashboard Interpretation

The monitoring dashboard shows an agentic RAG system that is operationally healthy on latency but exposed to retrieval-quality degradation. End-to-end latency remains clustered below two seconds and TTFT is tightly centered near 0.2 seconds, which suggests the serving layer and generation path are not the active bottlenecks. Token throughput is also stable, so the model invocation path looks capacity-consistent rather than compute-starved.

The risk signal comes from retrieval. The exported dashboard shows a visible left-shift in retrieval scores alongside an empty-retrieval rate that crosses the `EMPTY_RETRIEVAL_ALERT_THRESHOLD` from `.env`. That combination matters diagnostically because it points to evidence quality drift rather than generic infrastructure instability. If latency were rising at the same time, I would suspect downstream model saturation or network contention. Instead, the system is answering quickly while grounding quality weakens, which is consistent with a stale or incomplete knowledge base, newly emerging user topics, or chunking coverage gaps.

The highest-probability bottleneck is therefore corpus freshness and retrieval coverage, not FastAPI throughput. In production I would trigger an alert under three conditions:

1. p95 TTFT exceeds the configured bucket range for two consecutive windows.
2. Empty retrieval rate exceeds `0.15`, indicating a material increase in unanswered or weakly grounded queries.
3. Retrieval-score PSI crosses the significant threshold, signaling structural change in what the retriever is matching.

The operational recommendation is to treat retrieval degradation as a first-class incident. The immediate response would be to audit recent failed topics, refresh the indexed corpus, and compare chunking parameters before considering model changes. That preserves the Module 8 distinction between observable operations metrics and slower evaluated quality review.
