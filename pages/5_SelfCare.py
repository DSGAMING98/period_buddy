import streamlit as st

from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.ui_utils import render_page_header


SELFCARE_SECTIONS = {
    "Cramps & body pain": [
        "Use a warm water bag / heating pad on your lower belly or lower back for 15–20 minutes.",
        "Do slow, gentle stretches (child’s pose, knees-to-chest, cat–cow style movements).",
        "Stay hydrated with warm water or herbal tea; being even a little dehydrated can worsen cramps.",
        "If it’s safe for you and allowed by your doctor, over-the-counter pain relief can be an option.",
    ],
    "Bloating & digestion": [
        "Sip warm water slowly instead of chugging cold water.",
        "Avoid super gassy drinks (like soda) for a bit – they can worsen bloating.",
        "Light walking for 5–10 minutes can help gas move and reduce discomfort.",
        "Eat smaller, more frequent meals instead of a huge heavy one.",
    ],
    "Mood, sadness & overwhelm": [
        "Name what you’re feeling out loud or in notes – it sounds silly but it helps your brain organise it.",
        "Do one tiny ‘win’: shower, change clothes, or clean a small surface. It can shift your mood a little.",
        "Text or call someone safe and say, ‘I’m not okay today, can I just exist near you?’",
        "Give yourself permission to not be productive. Rest is allowed.",
    ],
    "Anxiety & overthinking": [
        "Your body being on high alert doesn’t mean you actually did something wrong.",
        "Try a simple breathing pattern: inhale 4s, hold 4s, exhale 6–8s. Repeat 5–10 times.",
        "Use grounding: 5 things you can see, 4 you can feel, 3 you can hear, 2 you can smell, 1 you can taste.",
        "Write down your worries, then split them into ‘I can do something’ vs ‘I can’t control this’.",
    ],
    "Low energy & fatigue": [
        "If you can, take a 20–30 minute nap or just lie down with eyes closed and no phone.",
        "Eat something with a mix of carbs + protein (like fruit + nuts, toast + egg, yoghurt + granola).",
        "Switch from ‘intense workout’ to ‘soft movement’ – stretching, slow walk, or just standing up every 30–40 minutes.",
        "Drop the pressure to be 100% today. Operating at 40% while bleeding is still effort.",
    ],
    "Sleep & night time": [
        "Dim your lights and get off bright screens 20–30 minutes before sleep if possible.",
        "Do a tiny night ritual: pee, wash face, change into comfy clothes, drink a bit of water.",
        "Avoid super heavy or spicy food right before bed if your stomach is already struggling.",
        "Try a calm playlist / white noise / rain sounds to help your brain wind down.",
    ],
    "Comfort food & cravings": [
        "It’s okay to honour cravings – just try to add some water and maybe a fruit / veg somewhere in the day.",
        "If you’re craving sweets, pair them with protein (like chocolate + nuts) to avoid a harsh crash.",
        "Warm, easy-to-digest foods (soups, khichdi, rice + dal, etc.) can feel extra soothing.",
        "Don’t shame yourself for eating more on your period; your body is literally doing heavy work.",
    ],
    "Movement ideas (low effort)": [
        "Do a 5-minute stretch session: neck rolls, shoulder rolls, back stretch, ankle circles.",
        "If you can step outside for 5–10 minutes of fresh air, that counts as movement.",
        "Put on one song and just sway / vibe in your room; it doesn’t have to be ‘real exercise’.",
        "If everything hurts, stretching in bed is also valid.",
    ],
}

QUICK_ACTIONS = {
    "2 minutes": [
        "Drink some water.",
        "Unclench your jaw, drop your shoulders, relax your face.",
        "Send one ‘I’m alive but drained’ text to someone safe.",
    ],
    "10 minutes": [
        "Stretch a little or walk around your room / house.",
        "Heat pack on cramps + scroll something light/funny instead of stressful feeds.",
        "Write down how you feel in 3 sentences, no filter.",
    ],
    "30 minutes": [
        "Warm shower + fresh clothes + clean pillowcase if possible.",
        "Make or order a simple comfort meal and eat slowly.",
        "Watch one episode / one YouTube video that makes you feel genuinely lighter, not worse.",
    ],
}


def main():
    init_auth_state()
    if not is_logged_in():
        render_page_header(
            page_title="Self-Care & Coping",
            subtitle="Pick small, realistic actions for cramps, mood, energy and more.",
        )
        st.warning("Please log in on the '0_Login / Profile' page to access self-care suggestions.")
        return

    render_page_header(
        page_title="Self-Care & Coping",
        subtitle="Not everything will fit you; treat this as a menu of options, not a checklist.",
    )

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 0.9rem;">
                <div class="pb-pill">What do you need help with right now?</div>
                <p style="margin-top: 0.55rem; font-size: 0.9rem; color:#c6bed8;">
                    Choose an area and I’ll throw some gentle, low-pressure ideas at you.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        category = st.selectbox(
            "Pick an area:",
            list(SELFCARE_SECTIONS.keys()),
            index=0,
        )

        tips = SELFCARE_SECTIONS.get(category, [])

        st.markdown(
            f"""
            <div class="pb-card" style="margin-bottom: 0.9rem;">
                <div class="pb-pill">{category}</div>
            """,
            unsafe_allow_html=True,
        )
        if tips:
            for t in tips:
                st.markdown(f"- {t}")
        else:
            st.markdown("- (No tips loaded yet, my bad.)")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 0.9rem;">
                <div class="pb-pill">Tiny steps menu</div>
                <p style="margin-top: 0.55rem; font-size: 0.9rem; color:#c6bed8;">
                    How much energy do you have in you?
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        energy_slot = st.radio(
            "Energy check:",
            ["2 minutes", "10 minutes", "30 minutes"],
            index=0,
        )

        actions = QUICK_ACTIONS.get(energy_slot, [])

        st.markdown(
            f"""
            <div class="pb-card" style="margin-bottom: 0.9rem;">
                <div class="pb-pill">{energy_slot} ideas</div>
            """,
            unsafe_allow_html=True,
        )
        for a in actions:
            st.markdown(f"- {a}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="pb-card">
                <div class="pb-pill">Gentle reminder</div>
                <p style="margin-top: 0.55rem; font-size: 0.9rem; color:#c6bed8;">
                    You don’t have to ‘earn’ rest or comfort. 
                    Bleeding, cramping, feeling like your brain is glitching – it’s a lot. 
                    Being kind to yourself isn’t a luxury, it’s survival.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
