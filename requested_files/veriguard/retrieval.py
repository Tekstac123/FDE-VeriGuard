"""Week 1 · Task 2 — Security-trimmed hybrid retrieval, grounded answers with citations, and the M1 evaluation.

Only current documents the user's role may see are ever ranked; every answer cites document, version, section and
page, says so when a superseded version exists, and declines when the evidence is insufficient. The answer TEXT is
written by the LLM gateway (compose_answer → veriguard/llm.py, key from .env); the citations come from your code.

Find your work with:  grep -n "TODO" veriguard/retrieval.py
Check it with:        python check_week1.py --task 2   (evaluate_qa: --task 3)
"""
from __future__ import annotations

from .common import (  # noqa: F401 — helpers you will need
    MIN_COVERAGE, MIN_SIMILARITY, NO_DOCS, ROLES, RRF_K, SearchIndex, citation_of, compose_answer,
    expected_citations, groundedness, source_line, superseded_versions)

# ─── WEEK 1 · L0 + M1 Grounded Financial Intelligence — you implement the stubbed functions in this file in Week 1 ───

MODES = ("vector", "hybrid", "hybrid_rerank")
RERANK_CANDIDATES = 50


def is_allowed(chunk: dict, role: str) -> bool:
    """Security trimming: the chunk is current AND the role is in its access_roles. Unknown role → PermissionError."""
    # TODO [W1-T2.1] is_allowed — the security-trimming rule every search result must pass.
    #   What to do:
    #   1. If `role` is not one of ROLES ("Analyst", "Investigator", "Auditor", "PrincipalOfficer", "Admin"),
    #      raise PermissionError (an unknown role is never "just denied" — it is an error).
    #   2. Return True ONLY when chunk["status"] == "current" AND role is in chunk["access_roles"].
    #      A missing status or missing/empty access_roles → False. Superseded chunks → False for every role.
    #   Expected: Analyst on a Confidential chunk (Investigator;Auditor;PrincipalOfficer) → False;
    #             Auditor on DCB-IA-2026-06 → True; any role on DCB-POL-KYC v3.2 → False; role "CFO" → PermissionError.
    raise NotImplementedError("is_allowed is not yet implemented")


def hybrid_search(index: SearchIndex, query: str, role: str, k: int = 5, mode: str = "hybrid_rerank") -> list[dict]:
    """Top-k allowed chunks: 'vector' ranking only, 'hybrid' (RRF of BM25 + vector) or 'hybrid_rerank' (+ rerank).

    Results are copies of the chunks plus 'score', 'keyword_score', 'vector_score' (+ 'rerank_score').
    """
    # TODO [W1-T2.2] hybrid_search — role-trimmed hybrid retrieval with three modes (for the ablation).
    #   What to do:
    #   1. mode not in MODES → raise ValueError.
    #   2. kw = index.keyword_scores(query) (BM25) and vec = index.vector_scores(query) (cosine) — one score per
    #      index.chunks position.
    #   3. FILTER FIRST: keep only chunk positions i where is_allowed(index.chunks[i], role). Never rank the others.
    #   4. Build each ranking separately over the allowed positions:
    #        vector ranking  = positions with vec[i] >= MIN_SIMILARITY, sorted by vec desc (ties: lower i first)
    #        keyword ranking = positions with kw[i] > 0, sorted by kw desc (ties: lower i first) — NOT in "vector" mode
    #   5. Reciprocal Rank Fusion: score[i] = Σ over the rankings of 1 / (RRF_K + rank), rank starting at 1.
    #      Order by fused score desc (ties: lower i first).
    #   6. Results = copies of the chunks: {**chunk, "score": round(fused, 6), "keyword_score": kw[i],
    #      "vector_score": vec[i]}. Take the top k — or, for "hybrid_rerank", the top RERANK_CANDIDATES, pass them
    #      to index.rerank(query, results) (adds "rerank_score", reorders) and then take the top k.
    #   Expected: the Analyst never receives DCB-IA-2026-06 or any superseded chunk, even with k=50;
    #             Recall@5 in the ablation: vector < hybrid ≈ hybrid_rerank.
    raise NotImplementedError("hybrid_search is not yet implemented")


def answer_question(index: SearchIndex, question: str, role: str) -> dict:
    """Grounded answer citing the two best sections, with a superseded-version note — or the NO_DOCS decline.

    Returns {"answer", "citations": [{"doc_id", "version", "section", "page"}], "sources", "refused",
    "superseded_note"}.
    """
    # TODO [W1-T2.3] answer_question — the citation / decline contract VeriGuard answers with.
    #   What to do:
    #   1. results = hybrid_search(index, question, role, k=5, mode="hybrid_rerank").
    #   2. DECLINE (before any model call) when there are no results, or when no result has
    #      index.coverage(question, r) >= MIN_COVERAGE. Return
    #      {"answer": NO_DOCS, "citations": [], "sources": [], "refused": True, "superseded_note": None}.
    #   3. cited = [results[0]] + the runner-up results[1] ONLY if it also has coverage >= MIN_COVERAGE.
    #   4. Superseded note: for each distinct doc_id in cited, for every row in superseded_versions(doc_id), add
    #      f"{doc_id} v{old['version']} is superseded by v{current}; this answer uses v{current}."
    #      (current = that doc's version in cited). Join the notes with spaces; no notes → None.
    #   5. answer = compose_answer(question, cited) + f" [{top['doc_id']} v{top['version']} §{top['section']}]"
    #      — compose_answer sends the cited sections to the LLM gateway (VERIGUARD_LLM=gateway, key from .env)
    #        and falls back to the extractive answer; you MUST call it, never the model directly.
    #      If there is a note: answer += "\nNote: " + note. Always end with "\n\nSources: " + "; ".join(source_line(c)).
    #   6. Return {"answer", "citations": [citation_of(c) for c in cited], "sources": [source_line(c) ...],
    #      "refused": False, "superseded_note": note}.
    #   Expected: "What single cash deposit amount triggers an internal monitoring alert at DCB?" (Analyst) →
    #             Rs 3,00,000, top citation DCB-POL-KYC v4.0 §6 p.2, note "DCB-POL-KYC v3.2 is superseded by v4.0…";
    #             the crypto-threshold question → declined with NO_DOCS.
    raise NotImplementedError("answer_question is not yet implemented")


def evaluate_qa(index: SearchIndex, golden: list[dict], k: int = 5, mode: str = "hybrid_rerank") -> dict:
    """M1 metrics: Recall@k and citation accuracy (answerable items), decline rate (unanswerable), superseded-trap
    accuracy, groundedness (answered items) and leaks (restricted items). Returns the metrics plus "items"."""
    # TODO [W1-T3.1] evaluate_qa — measure the pipeline on the golden set (the M1 evidence).
    #   What to do, for every item (fields: qid, question_type, role, question, expected_*):
    #   1. expected = expected_citations(item) → {(doc_id, version, section), …}.
    #   2. hits = hybrid_search(index, item["question"], item["role"], k=4*k, mode=mode);
    #      retrieved = the first k UNIQUE doc_ids of hits (keep order).
    #   3. ans = answer_question(index, item["question"], item["role"]).
    #   4. row = {"qid", "type": question_type, "role", "retrieved", "refused": ans["refused"], "citations"} plus:
    #      unanswerable    → row["declined"] = ans["refused"]
    #      restricted      → row["leaked"] = sorted expected doc_ids that appear in retrieved OR in ans citations;
    #                        add len(row["leaked"]) to the leak total
    #      every other type (factual, multi_hop, superseded_trap):
    #                        row["recall"] = |expected doc_ids ∩ retrieved| / |expected doc_ids|  (0.0 if none)
    #                        row["citation_ok"] = not refused AND any (doc_id, version, section) of a citation is in expected
    #                        if answered: row["groundedness"] = groundedness(ans["answer"], <index.chunks matching the
    #                                     citations' doc_id + version + section>)
    #                        superseded_trap also: row["superseded_ok"] = citation_ok AND bool(ans["superseded_note"])
    #   5. Return {"k", "mode", "recall_at_k", "citation_accuracy", "decline_rate", "superseded_accuracy",
    #      "groundedness"  (each = mean over the rows that HAVE that key, rounded to 3 decimals, 0.0 if none),
    #      "leaks": total, "items": rows}.
    #   M1 bar (python run_week1.py): Recall@5 ≥ 0.80 · citation ≥ 0.90 · decline ≥ 0.80 · superseded 1.0 ·
    #   groundedness ≥ 4.0 · leaks 0.
    #
    # TODO [W1-T3.2] (data task — no code here) extend datapack/04_evaluation/golden_dataset.jsonl:
    #   append ≥ 10 new JSON lines (qid "GQ-031", "GQ-032", …) with the same 8 fields as the seed — qid,
    #   question_type, role, question, reference_answer, expected_doc_ids, expected_versions, expected_sections —
    #   including ≥ 3 "unanswerable" (expected_* = "") and ≥ 3 "superseded_trap" (DCB-POL-KYC v3.2 → v4.0,
    #   DCB-POL-RET v1.0 → v2.0). Expected citations must point at CURRENT versions. Keep GQ-001 … GQ-030 unchanged.
    raise NotImplementedError("evaluate_qa is not yet implemented")
