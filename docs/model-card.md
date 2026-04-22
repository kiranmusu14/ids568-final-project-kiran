# System Card

## System Details

- System name: IDS 568 Agentic RAG Compliance Assistant
- Version: 1.0.0
- Interface: FastAPI service with observable Prometheus metrics
- Prompt template version: `rag-v3`

## Deployment Configuration

| Parameter | Value |
| --- | --- |
| LLM provider | Simulated (local inference; replace with OpenAI / Anthropic endpoint in production) |
| Model ID | Simulated generative model; production target is a gpt-4o-class or claude-3-class endpoint |
| Temperature | Loaded from `.env` → `LLM_TEMPERATURE` (default: deterministic simulation; set 0.2–0.7 in production) |
| Retrieval top-k | `RETRIEVAL_TOP_K=4` (raised from 3 via audit event evt-006) |
| Chunk size | Loaded from `.env` → `CHUNK_SIZE` (default corpus uses fixed-size chunking) |
| Retrieval score threshold | `RETRIEVAL_SCORE_THRESHOLD=0.55` |
| Prompt template version | `rag-v3` (logged in every audit event) |
| Observed p95 TTFT | ~0.2 s (simulated load; mean 0.19 s, std 0.05 s) |
| Observed p95 end-to-end latency | ~2.0 s (simulated; mean 1.54 s) |
| Cache hit ratio | Tracked via audit trail; not yet instrumented as a separate Prometheus metric |

## Intended Use

This system supports internal compliance research workflows by retrieving policy evidence, surfacing relevant controls, and synthesizing a grounded answer for a human reviewer. It is intended for low-risk operational analysis where staff can validate cited information before acting on it.

## Out-of-Scope Use

- Automated legal advice
- Decisions affecting employment, credit, insurance, or protected-class outcomes
- Handling raw production secrets or credentials
- Autonomous actions without human approval

## Observable Performance Metrics

- p95 TTFT is centered near 0.2 seconds in the simulated load test
- End-to-end latency remains below two seconds for most requests
- Token throughput remains stable during synthetic traffic
- Retrieval quality shows meaningful degradation under the current drift scenario, which is the dominant operational risk

## Training and Knowledge Data Description

The repository uses synthetic compliance-style prompts and simulated retrieval outputs rather than proprietary enterprise data. The system card therefore documents the deployed workflow that is under local control: prompt versioning, retrieval settings, monitoring signals, and governance practices. Vendor-model internals are intentionally excluded because they are not independently verifiable.

## Limitations and Failure Modes

- Retrieval quality depends on corpus freshness and chunk coverage
- Long queries can produce evidence dilution when multiple candidate chunks partially match
- The system can return plausible but incomplete summaries if no high-scoring chunk is retrieved
- Observable performance does not replace periodic evaluated quality review

## Ethical Risks and Considerations

- Differential service quality may emerge if some policy topics are better represented in the corpus than others
- Over-trust risk exists if users treat a synthesized answer as authoritative without reading retrieved evidence
- Third-party model processing raises data handling and retention considerations at the trust boundary

## Monitoring and Governance Commitments

- Audit events are hash-chained for tamper detection
- Drift thresholds and alert conditions are externally configured in `.env`
- Retrieval degradation triggers knowledge-base review before model changes are considered
