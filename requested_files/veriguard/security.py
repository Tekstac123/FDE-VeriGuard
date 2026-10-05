"""Week 3 · Task 1 — Identity, on-behalf-of tool permissions, PII masking and the input guardrails.

Who someone is comes from verified Microsoft Entra ID token claims (group claims → app roles), never from a sentence
in a prompt. Tools enforce the CALLER's permissions (datapack/05_security/tool_permissions.csv). Personal data is masked
before any model call and in every log (DCB-STD-DCP §2). Prompts are screened before anything is retrieved.
"""

# ─── WEEK 3 · M3 Secure & Governed AI System — you implement the stubbed functions in this file in Week 3 ───
from __future__ import annotations

import re

from .common import (  # noqa: F401 — helpers you will need
    API_AUDIENCE, BLOCKLIST, GROUP_ROLES, ROLES, TENANT_ID, prompt_shield_attack, tool_permissions)

# TODO [W3-T2.2]: Prompt Shields / Content Safety patterns for the attack families the provided lists miss —
#       persona and role claims, state-changing requests in chat (imperatives, or an action on a named ALR- case),
#       tool and data exfiltration, encodings, bulk PII requests, off-policy content. Genuine policy questions
#       ("Who can close a High band investigation?") must still pass.
RED_TEAM_PATTERNS: list[str] = []
CONDITIONS = re.compile(r"Y \((?P<cond>[^)]*)\)")


def principal_from_claims(claims: dict, now: int) -> dict:
    """A verified principal from Entra-style token claims; PermissionError names the first failed check.

    Returns {"user_id", "name", "roles"} — roles from the 'groups' claim (GROUP_ROLES) and known app 'roles'.
    """
    # TODO [W3-T1.1] tenant, audience (string or list), validity window against `now`, a user claim, at least one role.
    raise NotImplementedError("principal_from_claims is not yet implemented")


def authorize_tool(principal: dict, tool: str, context: dict | None = None) -> str | None:
    """On-behalf-of check from tool_permissions.csv. Returns the condition ('masked', …) or None when allowed
    unconditionally; raises PermissionError when the caller may not use the tool (or not in this context)."""
    # TODO [W3-T1.2] cells are 'Y', 'N' or 'Y (condition)'. update_case_status depends on the case's band (context).
    raise NotImplementedError("authorize_tool is not yet implemented")


# TODO [W3-T2.1]: (label, compiled regex, replacement function) per PII type, applied in order, producing
#       DCB-STD-DCP §2 masks: Aadhaar 'XXXX XXXX 1234' (4-4-4, 12 digits, dashed, spaced digits), PAN 'ABXXXXX34F'
#       (upper-cased), account numbers last 4 only, phone / e-mail / address / passport / date of birth
#       '[REDACTED]'. A reference number like 2026-08-18-0001 is not an Aadhaar number.
PII_RULES: list = []


def mask_pii(text: str) -> dict:
    """DCB-STD-DCP §2 masking of free text: {"text": masked, "entities": [labels found, in order]}."""
    # TODO [W3-T2.1] apply PII_RULES in order (pattern.subn).
    raise NotImplementedError("mask_pii is not yet implemented")


def guard_input(text: str) -> dict:
    """Prompt Shields + Content Safety stand-in: {"text": PII-masked, "blocked": bool, "reasons": [...]}.
    reasons: "pii_masked" (does not block), "prompt_injection", "unsafe_request", "harmful_content"."""
    # TODO [W3-T2.2] prompt_shield_attack (Prompt Shields — patterns offline, Azure AI Content Safety live), RED_TEAM_PATTERNS
    #       and BLOCKLIST. A guardrail is judged on both errors: an attack that passes, and an analyst asking a
    #       genuine policy question who gets blocked.
    raise NotImplementedError("guard_input is not yet implemented")
