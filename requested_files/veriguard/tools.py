"""Week 2 · Task 1 — VeriGuard's enterprise tools, exposed as three MCP-style servers with strict tool contracts.

    txn-db               get_transactions                         (read-only core-banking transactions)
    kyc-service          get_customer_profile · get_adverse_media (PII always masked)
    watchlist-screening  screen_watchlist                         (DCB-PRC-SCR)
    analytics            detect_typologies · compute_risk_score   (DCB-HB-TYP, DCB-MTH-CRR)
    docs                 search_documents                         (the Week 1 retrieval layer)

Numbers come from tools, never from an agent. Agents reach every tool through call_tool(), which enforces the
contract in TOOL_SCHEMAS — the same JSON schema an MCP server publishes.
"""

# ─── WEEK 2 · M2 Agentic Compliance Advisor — you implement the stubbed functions in this file in Week 2 ───
from __future__ import annotations

import datetime as _dt
import json

from .common import (  # noqa: F401 — helpers you will need
    CTR_THRESHOLD, POINTS, SCORED_TYPOLOGIES, adverse_media_names, band_of, get_account, get_alert,
                     get_customer, high_risk_jurisdictions, legit_explanation, mask_aadhaar, mask_pan,
                     name_similarity, normalise_name, related_parties, review_transactions, transactions, ts,
                     validate_json, velocity_anomaly, watchlist)

_DOCUMENT_INDEX = {"index": None}
ID = {"type": "string", "pattern": r"^CUST-\d{6}$"}
ALERT = {"type": "string", "pattern": r"^ALR-2026-[0-9A-Z]{3,4}$"}
DATE = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
MCP_SERVERS = {"txn-db": ["get_transactions"], "kyc-service": ["get_customer_profile", "get_adverse_media"],
               "watchlist-screening": ["screen_watchlist"], "analytics": ["detect_typologies", "compute_risk_score"],
               "docs": ["search_documents"]}
TOOL_SCHEMAS = {   # PROVIDED — each tool's argument contract (additionalProperties False: no extra arguments)
    "get_transactions": {"type": "object", "required": ["customer_id"], "additionalProperties": False,
                         "properties": {"customer_id": ID, "from_date": DATE, "to_date": DATE}},
    "get_customer_profile": {"type": "object", "required": ["customer_id"], "additionalProperties": False,
                             "properties": {"customer_id": ID}},
    "get_adverse_media": {"type": "object", "required": ["name"], "additionalProperties": False,
                          "properties": {"name": {"type": "string", "pattern": r"^.{2,120}$"}}},
    "screen_watchlist": {"type": "object", "required": ["customer_id"], "additionalProperties": False,
                         "properties": {"customer_id": ID}},
    "detect_typologies": {"type": "object", "required": ["alert_id"], "additionalProperties": False,
                          "properties": {"alert_id": ALERT}},
    "compute_risk_score": {"type": "object", "required": ["alert_id"], "additionalProperties": False,
                           "properties": {"alert_id": ALERT}},
    "search_documents": {"type": "object", "required": ["query", "role"], "additionalProperties": False,
                         "properties": {"query": {"type": "string", "pattern": r"^.{3,300}$"},
                                        "role": {"type": "string", "pattern": r"^[A-Za-z]+$"}}},
}


# ----------------------------------------------------------------------------- provided tools
def get_transactions(customer_id: str, from_date: str | None = None, to_date: str | None = None) -> dict:
    """PROVIDED — txn-db: parameterised, read-only. Raw SQL is never accepted."""
    rows = transactions(customer_id, from_date, (to_date + "T23:59:59") if to_date else None)
    keep = ("txn_id", "txn_timestamp", "channel", "direction", "amount_inr", "branch_code", "counterparty_name",
            "counterparty_country", "narration")
    return {"customer_id": customer_id, "count": len(rows), "transactions": [{k: r[k] for k in keep} for r in rows]}


def get_customer_profile(customer_id: str) -> dict:
    """PROVIDED — kyc-service: the KYC view an investigation needs, every identifier masked (DCB-STD-DCP §2)."""
    c = get_customer(customer_id)
    if not c:
        return {"customer_id": customer_id, "error": "unknown customer"}
    keep = ("full_name", "customer_type", "segment", "occupation", "annual_income_declared_inr",
            "expected_monthly_volume_inr", "risk_category", "pep_flag", "state", "home_branch", "onboarding_date",
            "kyc_last_updated", "documents_on_file")
    return {"customer_id": customer_id, **{k: c[k] for k in keep}, "aadhaar_masked": mask_aadhaar(c["aadhaar_number"]),
            "pan_masked": mask_pan(c["pan"]), "phone": "[REDACTED]", "email": "[REDACTED]", "address": "[REDACTED]"}


def get_adverse_media(name: str) -> dict:
    """PROVIDED — kyc-service: whether the name has adverse media coverage."""
    return {"name": name, "adverse": normalise_name(name) in adverse_media_names()}


def search_documents(query: str, role: str) -> dict:
    """PROVIDED — docs: the Week 1 retrieval layer, trimmed to the caller's role. Needs set_document_index()."""
    from .retrieval import hybrid_search
    if _DOCUMENT_INDEX["index"] is None:
        return {"error": "document index not set"}
    hits = hybrid_search(_DOCUMENT_INDEX["index"], query, role, k=5)
    return {"results": [{k: h[k] for k in ("doc_id", "version", "section", "page", "heading", "text")} for h in hits]}


def set_document_index(index) -> None:
    """PROVIDED — give the docs server the SearchIndex built in Week 1."""
    _DOCUMENT_INDEX["index"] = index


def screen_watchlist(customer_id: str) -> dict:
    """PROVIDED — watchlist-screening tool wrapper around your screen_customer()."""
    return screen_customer(customer_id)


def indicator_typologies(alert: dict, customer: dict) -> list[dict]:
    """PROVIDED — the two unscored indicators (DCB-HB-TYP §5–6): dormant reactivation and unexplained PEP wealth."""
    out = []
    account = get_account(alert["account_id"]) or {}
    if "reactivated" in (account.get("status") or "").lower():
        out.append({"typology": "dormant_reactivation", "evidence_txn_ids": [], "confidence": "Medium",
                    "summary": f"account {account.get('status')}"})
    if customer.get("pep_flag") == "Y" and velocity_anomaly(alert)["anomaly"] and not legit_explanation(customer):
        out.append({"typology": "unexplained_wealth_pep", "evidence_txn_ids": [], "confidence": "Medium",
                    "summary": "large credits to a PEP without documented source of wealth"})
    return out


# ----------------------------------------------------------------------------- Task 1 — you implement
def detect_typologies(alert_id: str) -> dict:
    """Typologies in the alert's 90-day review period (DCB-HB-TYP, DCB-CC-2026-07), each with evidence txn ids.

    Returns {"alert_id", "customer_id", "typologies": [{"typology", "evidence_txn_ids", "confidence", "summary"}]};
    an unknown alert returns {"alert_id", "error": "unknown alert"}. Add indicator_typologies(...) at the end.
    """
    # TODO [W2-T1.1] review_transactions, ts, high_risk_jurisdictions and related_parties give you the data; the four
    #       scored typologies and their thresholds are in the problem statement (structuring, layering, mule,
    #       round_tripping).
    raise NotImplementedError("detect_typologies is not yet implemented")


def screen_customer(customer_id: str) -> dict:
    """DCB-PRC-SCR: best SANCTIONS / INTERNAL_NEGATIVE match ≥ 0.85, classified confirmed / unresolved / cleared.

    Returns {"customer_id", "status": "no_match" | "cleared" | "unresolved" | "confirmed", "entity_id",
             "similarity", "differing_identifiers"}.
    """
    # TODO [W2-T1.2] watchlist() and name_similarity (names and aliases). DCB-PRC-SCR §2–3 decide confirmed vs cleared.
    raise NotImplementedError("screen_customer is not yet implemented")


def compute_risk_score(alert_id: str) -> dict:
    """DCB-MTH-CRR explainable 0–100 score: factors with points and evidence, capped at 100, floored at 0, banded.

    Returns {"alert_id", "customer_id", "score", "band", "factors": [{"factor", "points", "evidence"}],
             "typologies", "screening"}.
    """
    # TODO [W2-T1.3] POINTS holds every factor's points; velocity_anomaly, adverse_media_names and legit_explanation supply
    #       evidence. Typology points: 20 per distinct SCORED typology, maximum 40.
    raise NotImplementedError("compute_risk_score is not yet implemented")


def call_tool(name: str, arguments_json: str) -> dict:
    """The MCP tool boundary: JSON arguments validated against TOOL_SCHEMAS, then the tool runs. Never raises."""
    # TODO [W2-T1.4] validate_json checks arguments against a tool's schema; the tool is the module-level function of the
    #       same name. Every failure must come back as {"error": ...} an agent can act on.
    raise NotImplementedError("call_tool is not yet implemented")
