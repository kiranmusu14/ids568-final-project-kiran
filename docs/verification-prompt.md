# Final Repository Verification Prompt

Role: Senior IDS 568 Submission Auditor.

Objective: Verify that this repository fully satisfies the IDS 568 Final Project requirements using the Final Project Specification, the Submission Checklist, and the Module 8 Slides as the source of truth.

Audit Instructions:

1. Review the repository structure and confirm that all required deliverables exist in the expected locations.
2. Cross-check every checkbox in the Submission Checklist against an actual file, script, visualization, or written section in this repository.
3. Use the LLM/RAG adaptation guidance from Module 8 when evaluating Components 1, 3, 4, and 5.
4. Distinguish between:
   - `PASS`: requirement is clearly satisfied with direct evidence
   - `PARTIAL`: some evidence exists, but it is incomplete or weak
   - `FAIL`: requirement is missing or unsupported
5. For every checklist item, cite the exact supporting path, for example:
   - `src/monitoring/instrumentation.py`
   - `docs/model-card.md`
   - `logs/audit_trail.jsonl`
   - `visualizations/dashboard-export.png`
6. Validate the repository against these major sections:
   - Component 1: monitoring instrumentation, collector config, dashboard config, dashboard export, interpretation
   - Component 2: experiment specification, sample size justification, simulation, statistics, recommendation memo
   - Component 3: system card, lineage diagram, risk register, audit trail with tamper detection
   - Component 4: drift scripts, PSI outputs, drift visualization, diagnostic reasoning, action plan
   - Component 5: system boundary diagram, governance review, risk matrix, CTO memo
   - Repository requirements: README, setup scripts, pinned dependencies, reproducibility, root-level organization, file size, tagging note
7. Specifically verify these RAG-specific requirements from Module 8:
   - TTFT, token throughput, and retrieval-score monitoring
   - System card language rather than vendor-internal model claims
   - PSI applied to query length and retrieval distributions
   - At least two LLM/RAG-specific risks in the governance artifacts
8. Run and consider the result of `./verify_submission.sh`.
9. Produce the final answer in three sections only:
   - `Checklist Audit`
   - `Rubric Evidence Map`
   - `Gaps / Final Fixes`

Expected response format:

- Use a flat checklist with one line per requirement.
- Mark each line `PASS`, `PARTIAL`, or `FAIL`.
- Include exact file paths as evidence.
- If everything passes, still call out any manual items that cannot be proven automatically, such as git tagging, final repo naming, or visual polish.

Non-negotiable constraints:

- Do not invent evidence.
- Do not assume a checkbox is satisfied without pointing to a file or script.
- Prefer direct repo evidence over summary claims.
