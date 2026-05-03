from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.logging import get_logger
from app.models.schemas import EligibilityRequest, EligibilityResponse, NextStep

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["eligibility"])

_NVSP_URL = "https://voterportal.eci.gov.in"
_FORM6_URL = "https://voterportal.eci.gov.in/form6"

_NEXT_STEPS_EN = {
    "register": NextStep(label="Register on Voter Portal (Form 6)", url=_FORM6_URL),
    "portal": NextStep(label="Check your voter status on NVSP", url=_NVSP_URL),
    "helpline": NextStep(label="Call Voter Helpline: 1950", url="tel:1950"),
}
_NEXT_STEPS_HI = {
    "register": NextStep(label="मतदाता पोर्टल पर पंजीकरण करें (फॉर्म 6)", url=_FORM6_URL),
    "portal": NextStep(label="NVSP पर मतदाता स्थिति जांचें", url=_NVSP_URL),
    "helpline": NextStep(label="मतदाता हेल्पलाइन पर कॉल करें: 1950", url="tel:1950"),
}


@router.post("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(
    body: EligibilityRequest,
    lang: str = Query(default="en", pattern="^(en|hi)$"),
) -> EligibilityResponse:
    reasons: list[str] = []
    eligible = True
    steps_map = _NEXT_STEPS_HI if lang == "hi" else _NEXT_STEPS_EN

    # --- Age check ---
    if body.age < 18:
        eligible = False
        if lang == "hi":
            reasons.append(
                f"आपकी आयु {body.age} वर्ष है। मतदान के लिए न्यूनतम आयु 18 वर्ष है "
                "(61वां संवैधानिक संशोधन, 1988)।"
            )
        else:
            reasons.append(
                f"Your age ({body.age}) is below the minimum voting age of 18 years "
                "(61st Constitutional Amendment, 1988)."
            )
    else:
        if lang == "hi":
            reasons.append(f"आयु {body.age} वर्ष — मतदान के लिए 18+ की शर्त पूरी होती है।")
        else:
            reasons.append(f"Age {body.age} — meets the 18+ requirement for voting.")

    # --- Citizenship check ---
    if body.citizenship != "indian":
        eligible = False
        if lang == "hi":
            reasons.append(
                "केवल भारतीय नागरिक ही मतदाता सूची में पंजीकरण करा सकते हैं "
                "(अनुच्छेद 326, भारत का संविधान)।"
            )
        else:
            reasons.append(
                "Only citizens of India are eligible to register as voters "
                "(Article 326, Constitution of India)."
            )
    else:
        if lang == "hi":
            reasons.append("भारतीय नागरिकता — पंजीकरण की शर्त पूरी होती है।")
        else:
            reasons.append("Indian citizenship — registration requirement satisfied.")

    # --- Registration status ---
    if eligible and not body.already_registered:
        if lang == "hi":
            reasons.append(
                "आप मतदान के लिए पात्र हैं लेकिन अभी पंजीकृत नहीं हैं। "
                "voterportal.eci.gov.in पर फॉर्म 6 भरकर अभी पंजीकरण करें।"
            )
        else:
            reasons.append(
                "You are eligible to vote but not yet registered. "
                "Apply now via Form 6 at voterportal.eci.gov.in."
            )

    if eligible and body.already_registered:
        if lang == "hi":
            reasons.append("आप मतदान के लिए पात्र और पंजीकृत हैं। आप मतदान कर सकते हैं!")
        else:
            reasons.append("You are eligible and registered. You can vote!")

    # --- Build next steps ---
    next_steps: list[NextStep] = []
    if not eligible:
        next_steps.append(steps_map["helpline"])
    elif not body.already_registered:
        next_steps.extend([steps_map["register"], steps_map["portal"], steps_map["helpline"]])
    else:
        next_steps.extend([steps_map["portal"], steps_map["helpline"]])

    logger.info(
        "Eligibility check: age=%d citizenship=%s state=%s eligible=%s lang=%s",
        body.age,
        body.citizenship,
        body.state,
        eligible,
        lang,
    )

    return EligibilityResponse(eligible=eligible, reasons=reasons, next_steps=next_steps)
