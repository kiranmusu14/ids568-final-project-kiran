# Risk Register

| ID | Risk | Category | Likelihood | Severity | Mitigation | Owner | Trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | Retrieval returns stale policy excerpts after control updates | Robustness | Possible | Major | Schedule KB refresh, add document-age alert, review low-score queries weekly | Data Engineering Lead | Document age p95 exceeds 90 days |
| R002 | Prompt injection attempts alter tool-use instructions | Compliance | Possible | Critical | Input validation, tool allow-list, response filter, red-team regression set | ML Platform Lead | Flagged interaction or security review finding |
| R003 | User query includes PII that crosses the external model boundary | Privacy | Likely | Major | PII masking before model call, data processing agreement, retention minimization | Security Lead | PII detector alert |
| R004 | Differential coverage quality for underrepresented compliance topics | Bias | Possible | Moderate | Corpus coverage audit, topic-gap review, escalation path for unsupported domains | Product Owner | Retrieval gap rate rises in a topic segment |
| R005 | Operators cannot reconstruct the exact state used for a past answer | Compliance | Unlikely | Major | Hash-chained audit trail, prompt version logging, KB update events | Governance Lead | Audit request or incident investigation |
| R006 | Empty retrieval events rise and the model answers anyway | Robustness | Likely | Major | Block weak-grounding responses, fallback messaging, alert on empty retrieval rate | On-call Engineer | Empty retrieval rate exceeds threshold |
