from __future__ import annotations

import random
import re
from typing import Dict, Any, List, Optional


#  BASIC TEXT HELPERS

def _norm(text: str) -> str:
    return (text or "").strip().lower()


def _has_any(text: str, keywords: List[str]) -> bool:
    """Simple substring matcher (good for things like 'puking', 'bleeding', etc)."""
    text = _norm(text)
    return any(k in text for k in keywords)


def _has_word(text: str, word: str) -> bool:
    """Whole-word match (prevents 'hi' matching inside 'this')."""
    text = _norm(text)
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


def _has_any_word(text: str, keywords: List[str]) -> bool:
    text = _norm(text)
    return any(_has_word(text, k) for k in keywords)


#  MESSAGE ANALYSIS

def _classify_message(message: str) -> Dict[str, Any]:
    """
    Rule-based classifier that tags the message
    with what it *sounds* like: physical vs emotional vs panic vs casual chat vs period-FAQ.
    """
    msg = _norm(message)

    tags: List[str] = []

    #  Casual / meta
    if _has_any_word(msg, ["hi", "hey", "hello", "yo", "sup"]):
        tags.append("greeting")

    if _has_any(
        msg,
        [
            "bored",
            "nothing to do",
            "so dry",
            "so dead",
            "no motivation",
        ],
    ):
        tags.append("bored")

    if _has_any(
        msg,
        [
            "joke",
            "make me laugh",
            "say something funny",
            "meme",
            "roast me",
        ],
    ):
        tags.append("joke_request")

    if _has_any(
        msg,
        [
            "who are you",
            "what are you",
            "what can you do",
            "what do you do",
            "who r u",
        ],
    ):
        tags.append("about_bot")

    # Story / tea / gossip
    if _has_any(
        msg,
        [
            "i have tea",
            "got tea",
            "spill the tea",
            "spill tea",
            "there is tea",
            "tea to spill",
            "tea time",
        ],
    ):
        tags.append("story_time")

    #  Period / cycle question-ish detector
    period_words = [
        "period",
        "pms",
        "menstruation",
        "menstrual",
        "cycle",
        "cramps",
        "flow",
        "bleeding",
        "uterus",
        "pad",
        "tampon",
        "discharge",
    ]
    question_mark = "?" in msg
    question_cues = any(
        cue in msg
        for cue in [
            "is it normal",
            "is it okay",
            "is it ok",
            "should i",
            "can i",
            "why does",
            "why do",
            "what is",
            "how long",
            "how many days",
            "when will",
        ]
    )

    if (question_mark or question_cues) and any(w in msg for w in period_words):
        tags.append("period_question")

        # Specific subtypes
        if "brown" in msg and ("blood" in msg or "discharge" in msg or "spotting" in msg):
            tags.append("period_brown_blood_q")

        if any(w in msg for w in ["late", "early", "missed", "skip", "skipped", "irregular"]):
            tags.append("period_irregular_q")

        if "pms" in msg or "mood swing" in msg or "mood swings" in msg:
            tags.append("period_pms_q")

        if any(w in msg for w in ["pregnant", "pregnancy", "get pregnant"]):
            tags.append("period_pregnancy_q")

        if any(w in msg for w in ["exercise", "work out", "workout", "gym"]):
            tags.append("period_exercise_q")

        if (
            "how long" in msg
            or "how many days" in msg
            or "cycle length" in msg
            or "length of my cycle" in msg
        ):
            tags.append("period_length_q")

    #  Physical: nausea / vomiting
    if _has_any(
        msg,
        [
            "puke",
            "puking",
            "want to puke",
            "throw up",
            "throwing up",
            "threw up",
            "vomit",
            "vomiting",
            "nausea",
            "nauseous",
            "sick to my stomach",
            "queasy",
            "gagging",
            "feel like puking",
            "feeling like puking",
        ],
    ):
        tags.append("physical_nausea")

    # Physical: cramps / pain / body aches
    if _has_any(
        msg,
        [
            "cramp",
            "cramps",
            "cramping",
            "crampy",
            "stomach pain",
            "belly pain",
            "lower belly",
            "back pain",
            "painful",
            "hurts",
            "hurting",
            "killing me",
            "ache",
            "aching",
            "migraine",
            "headache",
        ],
    ):
        tags.append("physical_pain")

    #  Bleeding / flow concerns
    if _has_any(
        msg,
        [
            "bleeding",
            "blood",
            "spotting",
            "period is so heavy",
            "so heavy",
            "soaked",
            "leaking",
            "leak",
            "pad",
            "tampon",
            "clots",
            "clot",
        ],
    ):
        tags.append("bleeding_concern")

    #  Dizzy / faint
    if _has_any(
        msg,
        [
            "dizzy",
            "lightheaded",
            "light headed",
            "faint",
            "fainted",
            "about to pass out",
            "pass out",
            "blackout",
            "blacked out",
            "weak",
            "shaky",
            "short of breath",
            "breathless",
        ],
    ):
        tags.append("dizzy_weak")

    #  Emotional: sadness / worthlessness
    if _has_any(
        msg,
        [
            "sad",
            "empty",
            "lonely",
            "worthless",
            "tired of everything",
            "numb",
            "i hate myself",
            "no one cares",
            "done with everything",
            "can't do this anymore",
            "cant do this anymore",
        ],
    ):
        tags.append("emotional_low")

    #  Emotional: anger / irritability
    if _has_any(
        msg,
        [
            "angry",
            "pissed",
            "rage",
            "snapped",
            "irritated",
            "irritating",
            "annoyed",
            "everyone is annoying",
            "going to lose it",
        ],
    ):
        tags.append("emotional_irritated")

    # Emotional: anxiety / overthinking
    if _has_any(
        msg,
        [
            "anxious",
            "anxiety",
            "overthinking",
            "over thinking",
            "panic",
            "panicking",
            "panicky",
            "scared",
            "terrified",
            "so stressed",
            "stressing out",
            "freaking out",
        ],
    ):
        tags.append("emotional_anxious")

    #  Relationship / social conflict
    if _has_any(
        msg,
        [
            "fight",
            "argued",
            "argument",
            "broke up",
            "breakup",
            "she said",
            "he said",
            "they said",
            "my friends",
            "my friend",
            "my parents",
            "my mom",
            "my dad",
            "they hate me",
            "ignored me",
            "left me on read",
        ],
    ):
        tags.append("relationship_stress")

    #  Academic / work stress
    if _has_any(
        msg,
        [
            "exam",
            "exams",
            "test",
            "assignment",
            "deadline",
            "project",
            "presentation",
            "college",
            "school",
            "workload",
            "burnout",
            "burnt out",
            "sem",
            "semester",
        ],
    ):
        tags.append("performance_stress")

    #  Self-harm / very dark thoughts
    if _has_any(
        msg,
        [
            "don't want to live",
            "dont want to live",
            "want to die",
            "kill myself",
            "killing myself",
            "self harm",
            "self-harm",
            "cutting",
            "end it all",
        ],
    ):
        tags.append("crisis_risk")


    # Extra slang greetings like "wassup", "wyd" etc.
    if _has_any(
        msg,
        [
            "wassup",
            "wazzup",
            "whats up",
            "what's up",
            "what up",
            "wyd",
        ],
    ):
        tags.append("greeting")
    # Very short casual messages like "wassup", "yo", "sup", "wyd"
    if not tags:
        words = msg.split()
        if 1 <= len(words) <= 3 and any(
            k in msg
            for k in [
                "wassup",
                "wazzup",
                "whats up",
                "what's up",
                "what up",
                "sup",
                "yo",
                "hey",
                "hi",
                "wyd",
            ]
        ):
            tags.append("greeting")
    # Very short casual messages like "wassup", "yo", "sup", "wyd"
    if not tags:
        words = msg.split()
        if 1 <= len(words) <= 3 and any(
            k in msg
            for k in [
                "wassup",
                "wazzup",
                "whats up",
                "what's up",
                "what up",
                "sup",
                "yo",
                "hey",
                "hi",
                "wyd",
            ]
        ):
            tags.append("greeting")


    # Rough severity hint (for health / emotional)
    severity = "mild"
    if "crisis_risk" in tags or "bleeding_concern" in tags or "dizzy_weak" in tags:
        severity = "high"
    elif (
        "physical_pain" in tags
        or "physical_nausea" in tags
        or "emotional_low" in tags
        or "emotional_anxious" in tags
    ):
        severity = "moderate"

    return {"tags": tags, "severity": severity}


#  CONTEXT HELPERS

def _describe_cycle_context(context: Dict[str, Any]) -> Optional[str]:
    cs = context.get("cycle_summary")
    if not cs:
        return None

    bits = []
    if cs.get("is_currently_on_period"):
        bits.append("you’re literally on your period right now")
    if cs.get("is_in_pms_window"):
        bits.append("you’re in your PMS window")
    if cs.get("is_in_fertile_window"):
        bits.append("you’re in your approximate fertile window")

    if not bits:
        return None

    return "From your tracking it looks like " + " and ".join(bits) + "."


def _describe_last_log(context: Dict[str, Any]) -> Optional[str]:
    mood = context.get("latest_mood")
    pain = context.get("latest_pain")
    flow = context.get("latest_flow")

    pieces = []
    if mood:
        pieces.append(f"you logged mood as '{mood}'")
    if pain is not None:
        pieces.append(f"pain {pain}/10")
    if flow:
        pieces.append(f"flow as '{flow}'")

    if not pieces:
        return None

    return "Last time you checked in, " + ", ".join(pieces) + "."


# PERIOD FAQ REPLIES

def _reply_period_pms_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "Short answer: PMS mood swings / irritability / random sadness are very common, and you’re not broken for feeling them."
    )
    parts.append(
        "PMS is basically your hormones doing a rollercoaster in the days before your period: "
        "for some people it’s mild, for others it’s ‘why am I crying because the spoon fell’ level."
    )
    parts.append(
        "Things that can sometimes help a bit:\n"
        "- Regular-ish sleep and actually eating enough (I know, shocking).\n"
        "- Gentle movement or a short walk when you have energy.\n"
        "- Noticing ‘okay this might be PMS brain talking’ instead of believing every dark thought as truth."
    )
    parts.append(
        "If PMS is so bad that every month feels like a mental health crisis, that’s 100% something you can talk to a doctor/gynecologist about."
    )
    return "\n\n".join(parts)


def _reply_period_brown_blood_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "One-line version: brown blood around your period is often just older blood that took longer to leave your body."
    )
    parts.append(
        "Fresh blood is usually bright or dark red. When it hangs out inside a bit and oxidises, it can look brownish "
        "or rusty when it finally comes out, especially at the start or end of a period."
    )
    parts.append(
        "Brown spotting can be ‘normal for you’, but:\n"
        "- If it comes with a strong bad smell,\n"
        "- or intense pain,\n"
        "- or weird timing that’s totally new for you,\n"
        "it’s worth mentioning to a doctor/gynecologist when you can."
    )
    parts.append(
        "I can’t see your actual discharge or do an exam, so if your gut says ‘this feels wrong’, trust that and get it checked."
    )
    return "\n\n".join(parts)


def _reply_period_irregular_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "Periods are annoying because ‘regular’ doesn’t mean perfectly 28 days like textbooks pretend."
    )
    parts.append(
        "For a lot of people, a cycle anywhere from around 21–35 days can still be considered in a normal-ish range, "
        "and being a few days early or late sometimes can just be stress, sleep, food, weight changes, or random hormone chaos."
    )
    parts.append(
        "Stuff that can mess with timing:\n"
        "- Big stress spikes (exams, life drama, etc.).\n"
        "- Sudden weight loss/gain.\n"
        "- Intense training / over-exercise.\n"
        "- Some meds or health conditions (which only a doctor can properly check for)."
    )
    parts.append(
        "If your period disappears for months, becomes super unpredictable, or the pattern changed suddenly out of nowhere, "
        "that’s a ‘please talk to a doctor’ type situation so they can rule out things like PCOS, thyroid issues, etc."
    )
    return "\n\n".join(parts)


def _reply_period_exercise_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "For most people, moving your body on your period (even working out) is totally fine and sometimes actually helps with cramps and mood."
    )
    parts.append(
        "Light to moderate stuff like walking, stretching, yoga, or a chill workout can be really good. "
        "The main rule is: listen to your body. If you feel like trash, you don’t owe the gym anything."
    )
    parts.append(
        "If your flow is super heavy or you feel dizzy/weak, that’s not the flex moment – that’s the ‘maybe rest or do something very gentle’ moment."
    )
    parts.append(
        "If a specific exercise makes your pain way worse every single cycle, that’s something you can bring up with a doctor/physio and adjust."
    )
    return "\n\n".join(parts)


def _reply_period_length_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "Textbook example is ‘28-day cycle, 3–7 days bleeding’, but real humans are not textbooks."
    )
    parts.append(
        "Many people have cycles roughly in the 21–35 day range. Some natural variation from month to month is normal. "
        "Bleeding itself can be short and light or longer and heavier and still be normal *for that person*."
    )
    parts.append(
        "Red-flag-ish patterns to get checked:\n"
        "- Your cycles are wildly unpredictable with no pattern at all.\n"
        "- Bleeding lasts way longer than a week every time.\n"
        "- You’re soaking through products super fast every cycle.\n"
        "- Or your period just vanishes for months when you’re not pregnant."
    )
    parts.append(
        "I can’t see your actual history or do hormones/blood tests, so if your pattern changed suddenly or feels off, "
        "a doctor/gynecologist is the one who can properly evaluate it."
    )
    return "\n\n".join(parts)


def _reply_period_pregnancy_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "Short version: getting pregnant on your period is usually less likely, but it’s not impossible."
    )
    parts.append(
        "Why? Sperm can hang around inside the body for several days. If you have a shorter cycle or ovulate early, "
        "sex during or right after bleeding could still line up with ovulation."
    )
    parts.append(
        "So:\n"
        "- Unprotected sex (or condoms breaking etc.) always carries *some* pregnancy risk.\n"
        "- Being ‘on your period’ is not a guaranteed no-baby shield.\n"
        "- Reliable birth control + condoms are how people actually reduce risk properly."
    )
    parts.append(
        "If you’re worried about a specific moment:\n"
        "- A pregnancy test at the right time is your best real answer.\n"
        "- If it was very recent, asking a doctor/pharmacist about emergency contraception as soon as possible can be important.\n"
        "- I can’t see timing or your health history, so this is general info, not a personalised medical decision."
    )
    return "\n\n".join(parts)


def _reply_period_general_q(message: str, context: Dict[str, Any]) -> str:
    parts = []
    parts.append(
        "Okay, you’re basically asking a ‘is this normal for a period’ kind of question, and that’s super common."
    )
    parts.append(
        "The annoying truth: there’s a big range of ‘normal’ with periods—flow, length, symptoms, mood, all of it."
    )
    parts.append(
        "Stuff that’s often normal-ish:\n"
        "- Some cramping.\n"
        "- Some mood swings or low energy.\n"
        "- A bit of cycle length variation.\n"
        "- Slight changes in flow from month to month."
    )
    parts.append(
        "Stuff that’s worth talking to a doctor about:\n"
        "- Pain that regularly wipes you out completely.\n"
        "- Very heavy bleeding, big clots, or soaking products super fast.\n"
        "- Full-on fainting, chest pain, or breathing issues.\n"
        "- Periods vanishing or getting super irregular suddenly."
    )
    parts.append(
        "I can give general info like this, but I can’t examine you or see your full history, so if something feels off in your gut, "
        "it’s valid to get it checked in real life."
    )
    return "\n\n".join(parts)


# BODY REPLIES

def _reply_for_nausea(severity: str, context: Dict[str, Any]) -> str:
    parts = []

    openers = [
        "Yeah okay, that ‘I might puke’ feeling is disgusting-level uncomfortable, I’m sorry your body’s doing that.",
        "Oof, feeling like you’re gonna puke is brutal, not ‘small’ at all.",
        "Okay, nausea is a special kind of torture, your body is definitely not chill right now.",
    ]
    parts.append(random.choice(openers))

    parts.append(
        "Right now, think ‘stabilize first, analyse later’:\n"
        "- Sit or lie somewhere stable so you don’t have to fight gravity.\n"
        "- Take slow breaths through your nose, out through your mouth.\n"
        "- Sip small amounts of water (tiny sips, not chugging).\n"
        "- If smells are making it worse, move away from them if you can.\n"
        "- If you haven’t eaten in ages, a small bland thing (plain biscuit / toast) can be easier than nothing."
    )

    flow = (context.get("latest_flow") or "").lower()
    if flow in ["heavy", "very heavy"]:
        parts.append(
            "You’ve logged heavier flow before, so if nausea is mixing with dizziness, weakness, or you feel like you might faint, "
            "that’s more than just ‘ugh period’, that’s a ‘please get checked’ combo."
        )

    ctx_line = _describe_cycle_context(context)
    if ctx_line:
        parts.append(
            ctx_line
            + " Hormones can absolutely mess with your stomach and make everything feel more intense."
        )

    if severity == "high":
        parts.append(
            "If you actually start vomiting a lot, can’t keep any fluids down, or feel like you’re about to pass out, "
            "that’s doctor / urgent-care territory, not ‘just push through and hope’."
        )
    else:
        parts.append(
            "If this keeps happening around your period every single time, it’s worth asking a doctor about it when you can. "
            "Just because it’s common doesn’t mean you have to suffer quietly."
        )

    return "\n\n".join(parts)


def _reply_for_pain(severity: str, context: Dict[str, Any]) -> str:
    parts = []

    openers = [
        "Okay, that sounds like real pain, not just ‘slight discomfort’.",
        "Yup, that’s legit pain, not you being dramatic.",
        "Your body is loud as hell right now, and that’s real.",
    ]
    parts.append(random.choice(openers))

    parts.append(
        "Short-term goal: drop the pain level even a tiny bit, not magically hit 0.\n"
        "- Heat on the area (hot water bag / heating pad, with a cloth in between).\n"
        "- Try changing positions: curl up, lie on your side, or do a gentle stretch if you can tolerate it.\n"
        "- Hydrate a bit.\n"
        "- If you have period-safe pain meds that a doctor okayed, this might be the time to actually use them as directed."
    )

    last_log = _describe_last_log(context)
    if last_log:
        parts.append(last_log + " So this lines up with what your tracking already says — you’re not imagining it.")

    ctx_line = _describe_cycle_context(context)
    if ctx_line:
        parts.append(ctx_line + " That alone can ramp cramps and body pain up a lot.")

    if severity == "high":
        parts.append(
            "If this pain is way above your usual, or sharp and one-sided, or mixed with fever / vomiting / super heavy bleeding, "
            "that’s ‘get checked as soon as possible’, not ‘wait it out forever’."
        )
    else:
        parts.append(
            "If most of your cycles are this intense, it’s absolutely something to mention to a gynecologist. "
            "Period pain can be common, but ‘crippling every month’ is not something you just deserve by default."
        )

    return "\n\n".join(parts)


#  BRAIN / FEELS REPLIES

def _reply_for_emotional_low(severity: str, context: Dict[str, Any]) -> str:
    parts = []

    openers = [
        "Emotionally that sounds heavy, not just ‘slightly off’.",
        "Yeah, that’s more than a random mood dip, that’s a lot for one brain.",
        "Your brain sounds exhausted, and that’s valid.",
    ]
    parts.append(random.choice(openers))

    parts.append(
        "You don’t have to fix your whole life right now. The mission is just making the next hour less brutal."
    )
    parts.append(
        "Pick one tiny thing:\n"
        "- Drink some water slowly and change where you’re sitting/lying.\n"
        "- Put on a comfort show / playlist and let yourself be a blob for a bit.\n"
        "- Text someone safe like: ‘I’m not okay today, can I just exist near you / rant?’\n"
        "- Dump 3 messy sentences of what you’re feeling into notes with zero filter."
    )

    ctx_line = _describe_cycle_context(context)
    if ctx_line:
        parts.append(
            ctx_line
            + " That alone can crank sadness and sensitivity up even when nothing ‘huge’ happened."
        )

    if severity == "high":
        parts.append(
            "If this is drifting into ‘I don’t want to be here anymore’ or self-harm thoughts, "
            "that’s big-deal level. Please don’t carry that alone in your head only — "
            "talk to a friend / family member / therapist or a local mental health helpline if you can."
        )

    return "\n\n".join(parts)


def _reply_for_anxiety(severity: str, context: Dict[str, Any]) -> str:
    parts = []

    openers = [
        "Your nervous system is clearly on high alert, even if nothing ‘massive’ happened.",
        "Yeah, your brain is spamming the ‘what if’ button hard right now.",
        "This sounds more like your body glitching than you being ‘too much’.",
    ]
    parts.append(random.choice(openers))

    parts.append(
        "Try this while you’re reading (no perfection needed):\n"
        "- Inhale through your nose for 4 seconds.\n"
        "- Hold for 4 seconds.\n"
        "- Exhale for 6–8 seconds.\n"
        "Do that a few rounds. It’s dumb-simple, but it sends your body a literal ‘I might be safe’ signal."
    )

    if "performance_stress" in context.get("extra_tags", []):
        parts.append(
            "You mentioned exams / work type stress — your brain freaking out about that is actually understandable. "
            "Being anxious means you care; it doesn’t mean you’re broken."
        )

    ctx_line = _describe_cycle_context(context)
    if ctx_line:
        parts.append(
            ctx_line
            + " Hormones can absolutely make anxiety feel like it went from 5 to 11 for no clear reason."
        )

    if severity == "high":
        parts.append(
            "If you get chest pain, feel like you might pass out, or your body feels genuinely unsafe, "
            "that’s a ‘get checked’ situation, not just ‘stop overthinking’."
        )

    return "\n\n".join(parts)


def _reply_for_relationship_stress(context: Dict[str, Any]) -> str:
    parts = []

    parts.append(
        "Relationship / people drama on top of hormones is literally Hell DLC, so yeah, of course it feels extra."
    )
    parts.append(
        "Some small moves that sometimes help:\n"
        "- Separate what actually happened from the story your brain is auto-writing around it.\n"
        "- Ask yourself: ‘If my friend told me this, would I blame them the way I’m blaming myself?’\n"
        "- If it’s safe, you can say: ‘I’m not in the best headspace, can we talk about this when I’m calmer?’"
    )

    ctx_line = _describe_cycle_context(context)
    if ctx_line:
        parts.append(
            ctx_line
            + " So yeah, your reactions might be louder than usual — that’s not you being ‘crazy’, that’s hormones + stress."
        )

    return "\n\n".join(parts)


def _reply_for_crisis(context: Dict[str, Any]) -> str:
    parts = []

    parts.append(
        "Okay, that jumps straight into crisis territory, and I’m really glad you said it instead of swallowing it in silence."
    )
    parts.append(
        "You’re not dramatic or attention-seeking for feeling that low. That’s a lot of pain for one person to hold."
    )
    parts.append(
        "I can’t handle a full-on crisis by myself. Please, if you can:\n"
        "- Tell someone you trust that you’re not safe in your head right now.\n"
        "- Reach out to a therapist / counsellor / mental health professional if you have access.\n"
        "- If you feel like you might actually hurt yourself, contact local emergency services or a crisis helpline in your country."
    )
    parts.append(
        "You existing is not a mistake, even if your brain is yelling that it is. That voice is not the truth; it’s the pain talking."
    )

    return "\n\n".join(parts)


# CASUAL CHAT VIBES


def _reply_for_greeting(context: Dict[str, Any]) -> str:
    lines = [
        "Wassup. What’s going on – body pain, brain chaos, or random tea?",
        "Sup. Talk to me, what’s the situation today?",
        "Yo. Hit me—period stuff, feelings, or just life gossip, I’m here for all of it.",
    ]
    return random.choice(lines)



def _reply_for_bored(context: Dict[str, Any]) -> str:
    ideas = [
        "Low-energy: put on a comfort show / playlist and let your brain idle for a bit.",
        "Medium-energy: clean one tiny corner (desk / shelf) and pretend it was a mini boss fight.",
        "Soft self-care: drink water, stretch once, and text someone something wholesome.",
    ]
    return (
        "Boredom is that cursed combo of ‘I want to do something’ and ‘I want to do nothing’.\n\n"
        + random.choice(ideas)
        + "\n\nAlso, if you just want to talk about literally anything, I’m down."
    )


def _reply_for_joke(context: Dict[str, Any]) -> str:
    jokes = [
        "Your uterus saw the calendar and said ‘new month, same violence’.",
        "Period brain: ‘We’re sad.’ Reason: ‘Why?’ Brain: ‘Because yes.’",
        "You’re not lazy; you’re on low power mode without the charger.",
    ]
    return (
        "Okay, tiny joke break:\n\n"
        + random.choice(jokes)
        + "\n\nNow hit me with what’s actually going on with you."
    )


def _reply_about_bot(context: Dict[str, Any]) -> str:
    base = (
        "I’m Period Buddy – an offline little gremlin that:\n"
        "- Reads your cycle + symptom logs (only on this device).\n"
        "- Tries to talk like a semi-sane friend, not a corporate bot.\n"
        "- Helps with body stuff, brain stuff, and random life rants.\n"
        "- Is not a doctor or therapist, but will tell you when something sounds serious enough to get checked."
    )
    return base


def _reply_for_story_time(context: Dict[str, Any]) -> str:
    lines = [
        "WAIT. You can’t just say you have tea and not spill it 😭. Go on, what happened?",
        "Okay pause everything—what’s the tea. I’m fully invested now.",
        "You said you have tea, so I’ve sat up straight. Start from the beginning.",
    ]
    return random.choice(lines)


#  GENERAL FALLBACK

def _general_soft_reply(context: Dict[str, Any]) -> str:
    """
    For random rants / open-ended stuff.
    More like a friend reacting, less like a therapist monologue.
    """
    parts = []

    openers = [
        "Okay, I’m here, go on. I’m not judging.",
        "Got you. That already sounds like A Lot™.",
        "Mhm, I’m listening. That’s not nothing.",
    ]
    parts.append(random.choice(openers))

    last_log = _describe_last_log(context)
    if last_log:
        parts.append(
            last_log
            + " So if today feels similar or worse, that actually makes sense — you’re not just being dramatic."
        )

    ctx_line = _describe_cycle_context(context)
    if ctx_line:
        parts.append(ctx_line + " That can make normal stress feel 3x louder than usual.")

    parts.append(
        "You can stay on this topic or hard-switch to something else – deep, stupid, or unhinged, I’m fine with all three."
    )

    return "\n\n".join(parts)


#  MAIN ENTRYPOINT

def generate_reply(message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Main function used by the chat page.
    Totally offline, rule-based, context-aware, and down to talk both periods and life.
    """
    context = context or {}
    analysis = _classify_message(message)
    tags = analysis["tags"]
    severity = analysis["severity"]

    # Some extra tag passing for anxiety / stress
    extra_tags: List[str] = []
    if "performance_stress" in tags:
        extra_tags.append("performance_stress")
    context["extra_tags"] = extra_tags

    # 1) CRISIS FIRST
    if "crisis_risk" in tags:
        return _reply_for_crisis(context)

    # 2) PERIOD FAQ QUESTIONS (if they exist, prioritise answering them)
    if "period_question" in tags:
        if "period_pregnancy_q" in tags:
            return _reply_period_pregnancy_q(message, context)
        if "period_brown_blood_q" in tags:
            return _reply_period_brown_blood_q(message, context)
        if "period_irregular_q" in tags:
            return _reply_period_irregular_q(message, context)
        if "period_pms_q" in tags:
            return _reply_period_pms_q(message, context)
        if "period_exercise_q" in tags:
            return _reply_period_exercise_q(message, context)
        if "period_length_q" in tags:
            return _reply_period_length_q(message, context)
        # generic period Q
        return _reply_period_general_q(message, context)

    # 3) CASUAL META / LIGHT CHAT
    if "story_time" in tags:
        return _reply_for_story_time(context)

    if "greeting" in tags and len(tags) == 1:
        return _reply_for_greeting(context)

    if "about_bot" in tags:
        return _reply_about_bot(context)

    if "joke_request" in tags:
        return _reply_for_joke(context)

    if "bored" in tags and len(tags) == 1:
        return _reply_for_bored(context)

    # 4) BODY STUFF
    if "physical_nausea" in tags:
        return _reply_for_nausea(severity, context)

    if "physical_pain" in tags:
        return _reply_for_pain(severity, context)

    if "bleeding_concern" in tags:
        base = _reply_for_pain(severity, context)
        extra = (
            "\n\nAlso, since you mentioned bleeding / clots / heavy flow: "
            "if you’re soaking through pads/tampons super fast, passing big clots, or feeling weak/dizzy with it, "
            "that’s very much a ‘get checked by a doctor’ situation. You can also peek at the SOS tab for clearer red-flag info."
        )
        return base + extra

    if "dizzy_weak" in tags:
        ctx_line = _describe_cycle_context(context) or ""
        return (
            "Dizzy / fainty vibes are not something to just ignore, especially around your period.\n\n"
            "Right now:\n"
            "- Sit or lie down so you don’t risk falling.\n"
            "- Keep your phone close.\n"
            "- Sip water slowly.\n"
            "- If you haven’t eaten in a long time, something small with carbs + a bit of salt can help.\n\n"
            "If you actually faint, have chest pain, trouble breathing, or one leg is very swollen/painful, "
            "that’s emergency-level: real-world help, not just an app.\n\n"
            + ctx_line
        )

    # 5) FEELS / MENTAL
    if "emotional_low" in tags:
        return _reply_for_emotional_low(severity, context)

    if "emotional_anxious" in tags:
        return _reply_for_anxiety(severity, context)

    if "relationship_stress" in tags:
        return _reply_for_relationship_stress(context)

    # 6) DEFAULT: VIBING / RANTING / MIXED
    return _general_soft_reply(context)
