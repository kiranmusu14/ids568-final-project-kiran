# Risk Matrix

| Risk ID | Likelihood | Severity | Score | Priority | Mitigation Plan |
| --- | --- | --- | --- | --- | --- |
| R001 | 3 | 4 | 12 | High | Refresh KB on cadence, add age and retrieval-score alerts |
| R002 | 3 | 5 | 15 | High | Prompt isolation, tool allow-list, validation and filtering |
| R003 | 4 | 4 | 16 | Critical | PII masking, contractual controls, minimal retention |
| R004 | 3 | 3 | 9 | High | Coverage review, topic-gap analysis, fallback escalation |
| R005 | 2 | 4 | 8 | Medium | Tamper-evident audit trail and release approvals |
| R006 | 4 | 4 | 16 | Critical | Weak-grounding block, empty-retrieval alert, safe fallback |

The matrix shows that operational trust risks in an agentic RAG system are not limited to the model itself. Two of the highest-priority risks arise at system boundaries: raw prompt data leaving the environment and low-confidence retrieval still reaching end users as fluent text. Those are the conditions most likely to cause harm quickly, so they deserve stronger controls than cosmetic model-quality improvements.
