from __future__ import annotations

from typing import List, Dict, Any, Optional


# SYMPTOM KNOWLEDGE BASE (OFFLINE)


# Canonical symptom codes so UI can be messy names but logic stays clean
SYMPTOM_ALIASES: Dict[str, str] = {
    "Cramps": "cramps",
    "Lower back pain": "back_pain",
    "Headache": "headache",
    "Migraine": "migraine",
    "Nausea": "nausea",
    "Bloating": "bloating",
    "Breast tenderness": "breast_tenderness",
    "Acne / breakouts": "acne",
    "Mood swings": "mood_swings",
    "Anxiety": "anxiety",
    "Irritability / anger": "irritability",
    "Sad / low mood": "low_mood",
    "Fatigue / low energy": "fatigue",
    "Craving sweets": "craving_sweet",
    "Craving salty food": "craving_salty",
    "Sleep issues": "sleep_issues",
    "Dizziness / feeling faint": "dizzy",
    "Very heavy bleeding": "very_heavy_flow",
    "Clots larger than 1 rupee coin": "large_clots",
    "Diarrhoea": "diarrhoea",
    "Constipation": "constipation",
}

# Base tips per symptom (will be merged)
SYMPTOM_TIPS: Dict[str, List[str]] = {
    "cramps": [
        "Use a warm water bag / heating pad on your lower belly or back.",
        "Gentle stretching or slow walking can help relax the muscles.",
        "Stay hydrated – warm water or herbal tea can ease cramping.",
    ],
    "back_pain": [
        "Try light stretching or a few cat–cow / child’s pose type movements.",
        "Use a heating pad or hot shower to relax lower back muscles.",
    ],
    "headache": [
        "Drink water and rest your eyes from screens for a bit.",
        "A cool cloth on your forehead or neck can help.",
    ],
    "migraine": [
        "Rest in a dark, quiet room if you can.",
        "Avoid bright screens and loud sounds for a while.",
    ],
    "nausea": [
        "Small, frequent sips of water or ginger tea can calm nausea.",
        "Avoid very oily or spicy food until it settles.",
    ],
    "bloating": [
        "Sip warm water and avoid very gassy drinks (like soda).",
        "Light movement (slow walk) can help reduce bloating.",
    ],
    "breast_tenderness": [
        "Wear a soft, supportive bra or sports bra for comfort.",
        "Avoid sleeping on your stomach if it feels sore.",
    ],
    "acne": [
        "Keep your usual skincare routine gentle – don’t over-scrub.",
        "Change pillowcases regularly if you can.",
    ],
    "mood_swings": [
        "Name what you’re feeling – it’s valid and not ‘too much’.",
        "Try a low-effort comfort activity: music, show, journaling, or calling someone safe.",
    ],
    "anxiety": [
        "Try slow breathing: inhale 4 seconds, hold 4, exhale 6–8 seconds.",
        "Ground yourself: name 5 things you see, 4 you can feel, 3 you hear, 2 you smell, 1 you can taste.",
    ],
    "irritability": [
        "Give yourself space from people if everything feels annoying.",
        "Physical outlet helps: stretch, shake out your arms/legs, or do a short walk.",
    ],
    "low_mood": [
        "Be gentle with yourself; you don’t have to be productive today.",
        "Tiny tasks (shower, changing clothes, making your bed) can shift your mood a bit.",
    ],
    "fatigue": [
        "If possible, take a short nap or lie down for a bit.",
        "Eat something with a mix of carbs + protein (like fruit + nuts, toast + egg).",
    ],
    "craving_sweet": [
        "It’s okay to have something sweet; pairing it with fibre/protein helps avoid a crash.",
    ],
    "craving_salty": [
        "Salt cravings can be normal; just balance it with water and some fruit/veg if you can.",
    ],
    "sleep_issues": [
        "Avoid heavy screens for ~30 minutes before sleep.",
        "Try a simple night routine: dim lights, slow music, breathing exercises.",
    ],
    "dizzy": [
        "Sit or lie down immediately so you don’t fall.",
        "Sip water slowly; if it keeps happening, a doctor should check it.",
    ],
    "very_heavy_flow": [
        "Change pads/tampons frequently and use high-absorbency products.",
        "If you’re soaking through in under an hour repeatedly, that can be a red flag.",
    ],
    "large_clots": [
        "Some clots can be normal, but many large clots with heavy flow can be a sign to see a doctor.",
    ],
    "diarrhoea": [
        "Sip water or oral hydration; avoid heavy, oily foods for a bit.",
    ],
    "constipation": [
        "Drink water and try to add some fibre (fruit, veg, whole grains) if possible.",
    ],
}

GENERAL_SUPPORT_LINES: List[str] = [
    "You’re not dramatic for feeling this way. Periods genuinely affect your body hard.",
    "You’re allowed to rest. Existing while bleeding is already work.",
    "Listening to your body is a strength, not a weakness.",
]

# Red flag rules (these just add a “go to doctor” nudge, not diagnosis)
def _detect_red_flags(
    symptom_codes: List[str],
    pain_scale: Optional[int],
    flow_level: Optional[str],
) -> List[str]:
    red_flags: List[str] = []

    # Very heavy flow + clots + high pain
    if "very_heavy_flow" in symptom_codes or (flow_level and flow_level.lower() in {"very heavy", "flooding"}):
        red_flags.append(
            "Your bleeding sounds quite heavy. If you’re soaking through a pad/tampon in under an hour for several hours, "
            "feel dizzy, or see many large clots, it’s important to see a doctor or gynecologist."
        )

    if "large_clots" in symptom_codes:
        red_flags.append(
            "Passing clots larger than a 1 rupee coin regularly can be a sign to get checked by a professional."
        )

    if "dizzy" in symptom_codes:
        red_flags.append(
            "Dizziness or feeling faint during your period can sometimes be linked to low blood pressure or low iron. "
            "Please talk to a doctor if this keeps happening."
        )

    if pain_scale is not None and pain_scale >= 8:
        red_flags.append(
            "Pain at this level (8/10 or more) is not something you just ‘have to live with’. "
            "If this is usual for you, a gynecologist can check for conditions like endometriosis or fibroids."
        )

    return red_flags


def normalize_symptom_labels(selected_labels: List[str]) -> List[str]:
    """
    Convert human-facing labels like 'Cramps', 'Lower back pain'
    to internal codes like 'cramps', 'back_pain'.
    """
    codes: List[str] = []
    for label in selected_labels:
        code = SYMPTOM_ALIASES.get(label, None)
        if code:
            codes.append(code)
    # Remove duplicates while preserving order
    seen = set()
    unique_codes: List[str] = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique_codes.append(c)
    return unique_codes


def analyze_symptoms(
    selected_labels: List[str],
    pain_scale: Optional[int] = None,
    flow_level: Optional[str] = None,
    mood_label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main function to call from the UI.

    Inputs:
    - selected_labels: list of user-facing symptom names (e.g. ["Cramps", "Bloating"])
    - pain_scale: 0–10 if you ask them to rate pain
    - flow_level: e.g. "Light", "Medium", "Heavy", "Very heavy"
    - mood_label: optional mood like "Chill", "Sad", "Irritated"

    Output:
    {
      "severity_label": str,
      "combined_tips": [str, ...],
      "mood_support": [str, ...],
      "general_support": [str, ...],
      "red_flags": [str, ...]
    }
    """
    symptom_codes = normalize_symptom_labels(selected_labels)

    # Base severity from pain scale
    if pain_scale is None:
        severity = "unknown"
    elif pain_scale <= 3:
        severity = "mild"
    elif pain_scale <= 6:
        severity = "moderate"
    else:
        severity = "severe"

    # Boost severity based on flow & red-flaggy symptoms
    high_risk_symptoms = {"very_heavy_flow", "large_clots", "dizzy"}
    if any(code in high_risk_symptoms for code in symptom_codes):
        if severity in {"unknown", "mild"}:
            severity = "moderate"

    if flow_level and flow_level.lower() in {"very heavy", "flooding"}:
        if severity != "severe":
            severity = "moderate"

    # Collect tips
    combined_tips: List[str] = []
    for code in symptom_codes:
        tips_for_symptom = SYMPTOM_TIPS.get(code, [])
        for tip in tips_for_symptom:
            if tip not in combined_tips:
                combined_tips.append(tip)

    # Mood-specific support
    mood_support: List[str] = []
    if mood_label:
        mood = mood_label.lower()
        if "sad" in mood or "low" in mood:
            mood_support.append("If everything feels heavy, that’s valid. You don’t have to force positivity today.")
            mood_support.append("Try one tiny comforting thing: favourite music, a show, or texting someone you trust.")
        if "irritated" in mood or "angry" in mood:
            mood_support.append("You’re not ‘too much’ for feeling snappy. Hormones can amplify everything.")
            mood_support.append("If possible, warn people close to you that you’re low on patience today – it’s okay.")
        if "anxious" in mood:
            mood_support.append("Try a 5–10 minute breathing or grounding exercise; it genuinely helps your nervous system.")
            mood_support.append("You are still safe and okay, even if your body feels on high alert right now.")

    # General support lines (always)
    general_support = GENERAL_SUPPORT_LINES.copy()

    # Red flags
    red_flags = _detect_red_flags(symptom_codes, pain_scale, flow_level)

    return {
        "severity_label": severity,
        "combined_tips": combined_tips,
        "mood_support": mood_support,
        "general_support": general_support,
        "red_flags": red_flags,
    }
