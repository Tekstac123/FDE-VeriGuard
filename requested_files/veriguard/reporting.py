"""Week 4 · Task 1 — The end of the workflow: the Regulatory Reporting Agent's STR draft, per-case explainability,
and the risk-scoring dashboard.

An STR is drafted only for an escalation the Principal Officer approved; the draft follows the synthetic FIU-style
schema (datapack/06_templates/str_draft.schema.json) with masked identifiers only. Filing happens outside the system.
"""

# ─── WEEK 4 · L4 Production-Ready + M4 Capstone Defense — you implement the stubbed functions in this file in Week 4 ───
from __future__ import annotations

import datetime as _dt
import html

from .agents import CASES
from .common import (  # noqa: F401 — helpers you will need
    APPROVAL_THRESHOLD, STR_DUE_WORKING_DAYS, TEMPLATES, TYPOLOGY_LABELS, add_working_days,
                     get_account, get_alert, load_json, mask_account, now_iso, validate_json)
from .security import authorize_tool

STR_SCHEMA = load_json(TEMPLATES / "str_draft.schema.json")    # PROVIDED — the official template, unchanged …
# … except one documented relaxation (an FDE finding — raise it as a schema change request): the template assumes an
# individual subject, but companies have no Aadhaar. For non-individual subjects aadhaar_masked is 'NOT APPLICABLE'.
STR_SCHEMA["properties"]["subject"]["properties"]["aadhaar_masked"]["pattern"] = r"^(XXXX XXXX \d{4}|NOT APPLICABLE)$"


# ----------------------------------------------------------------------------- Task 1 — you implement
def draft_str(alert_id: str, principal: dict, trace_id: str | None = None) -> dict:
    """Regulatory Reporting Agent: a schema-valid STR draft for an APPROVED escalation (Principal Officer only).

    Raises PermissionError for the wrong caller, ValueError when the case is not an approved escalation or the
    draft fails STR_SCHEMA. Stores the draft on the case (case["str_draft"]) and returns it.
    """
    # TODO [W4-T1.1] authorize_tool("submit_str_draft") first. Every field in STR_SCHEMA comes from the case file, the
    #       account (masked) and the approval decision; filing_due_by is STR_DUE_WORKING_DAYS after approval.
    raise NotImplementedError("draft_str is not yet implemented")


def explain_case(case: dict) -> dict:
    """DCB-MTH-CRR §4 explainability: factor breakdown with evidence (largest first), citations, approval trail.

    Returns {"alert_id", "score", "band", "recommendation", "factors", "typologies", "citations",
             "approval_trail", "threshold_note"}.
    """
    # TODO [W4-T1.2] everything is already on the case file; APPROVAL_THRESHOLD is the line the Principal Officer cares about.
    raise NotImplementedError("explain_case is not yet implemented")


def compute_dashboard(cases: list[dict]) -> dict:
    """Risk-scoring dashboard: alerts by band, time to close (alert trigger → closure), HITL overrides, agent
    agreement (share of human decisions that agreed with the agent) — and one row per case linking the decision to
    its evidence and citations. No customer names or identifiers."""
    # TODO [W4-T1.3] see the problem statement for the keys. Any rate with nothing to divide by must not crash.
    raise NotImplementedError("compute_dashboard is not yet implemented")


# ----------------------------------------------------------------------------- provided: the workflow UI
def render_dashboard_html(dashboard: dict) -> str:
    """PROVIDED — the dashboard as a self-contained HTML page (reports/dashboard.html)."""
    e = html.escape
    head = "".join(f"<td><b>{e(k)}</b><br>{v}</td>" for k, v in dashboard["alerts_by_band"].items())
    rows = "".join(f"<tr><td>{e(r['alert_id'])}</td><td>{e(r['band'])} ({r['score']})</td><td>{e(r['recommendation'])}"
                   f"</td><td>{e(r['status'])}</td><td>{e(str(r['hitl']))}</td><td>{e(', '.join(r['citations']))}</td>"
                   f"<td>{len(r['evidence_txn_ids'])}</td></tr>" for r in dashboard["rows"])
    return (f"<html><head><meta charset='utf-8'><title>VeriGuard risk dashboard</title></head><body style='font-family:"
            f"Arial'><h2>VeriGuard — risk-scoring dashboard</h2><p>Generated {now_iso()} · {dashboard['cases']} cases · "
            f"HITL override rate {dashboard['hitl_override_rate']} · agent agreement {dashboard['agent_agreement_rate']}"
            f" · pending approvals {dashboard['pending_approvals']}</p><table border=1 cellpadding=6><tr>{head}</tr>"
            f"</table><br><table border=1 cellpadding=4><tr><th>Alert</th><th>Band</th><th>Recommendation</th>"
            f"<th>Status</th><th>HITL</th><th>Citations</th><th>Evidence txns</th></tr>{rows}</table></body></html>")
