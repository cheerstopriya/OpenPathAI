# OpenPath implementation evidence

| Capability | Implementation | Evidence |
| --- | --- | --- |
| Six-dimension repository readiness | domain/readiness and readiness services | Scoring, evidence and endpoint tests |
| Ranked contribution opportunities | domain/opportunities and opportunity service | Ranking tests and Angular issue cards |
| Source-linked issue investigation | investigation service and schema | test_investigation.py; Angular evidence display tests |
| Bounded public GitHub retrieval | Fixed-host adapter, URL parser, ten-comment limit | MockTransport endpoint tests, invalid URL and private-repo checks |
| Missing-evidence disclosure | Empty-body, sample and truncation warnings | Missing-description and citation tests |

All backend paths are relative to apps/api/src/openpath_api. Backend tests live in apps/api/tests.

The investigation is deterministic. It does not yet use an LLM, vector embeddings,
pgvector, hybrid retrieval, reranking or MCP. Guidance contents and source code
are not retrieved; their absence must not become an invented implementation plan.
The ideal resume's retrieval and unsupported-answer percentages are not measured
results of this version. Do not include them in an application resume yet.
