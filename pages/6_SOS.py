import streamlit as st
from datetime import date

from utils.cycle_utils import compute_cycle_summary
from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.session_data import ensure_user_data
from utils.ui_utils import render_page_header


def main():
    init_auth_state()
    if not is_logged_in():
        render_page_header(
            page_title="SOS Zone",
            subtitle="For the ‘I’m not okay, this is too much’ days.",
        )
        st.warning("Please log in on the '0_Login / Profile' page to use the SOS zone.")
        return

    username = get_current_profile_name()
    ensure_user_data(username)

    render_page_header(
        page_title="SOS Zone",
        subtitle=(
            "I can’t replace a doctor or crisis support, but I can help you sort out what might be going on "
            "and what to do next."
        ),
    )

    col_left, col_right = st.columns([2, 1])

    # ---------- LEFT: MODES ----------
    with col_left:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 1rem;">
                <div class="pb-pill">What kind of SOS is today?</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        mode = st.radio(
            "Pick what feels closest:",
            [
                "Pain is too much",
                "Bleeding feels scary",
                "Emotionally not okay",
                "Dizzy / faint / weird symptoms",
            ],
            index=0,
            key="sos_mode_radio",
        )

        if mode == "Pain is too much":
            _pain_sos_block()
        elif mode == "Bleeding feels scary":
            _bleeding_sos_block()
        elif mode == "Emotionally not okay":
            _emotional_sos_block()
        elif mode == "Dizzy / faint / weird symptoms":
            _dizzy_sos_block()

    # ---------- RIGHT: CONTEXT + RED FLAGS ----------
    with col_right:
        _render_context_panel()
        _render_emergency_red_flags()


def _render_context_panel():
    st.markdown(
        """
        <div class="pb-card" style="margin-bottom: 0.8rem;">
            <div class="pb-pill">Where you are right now</div>
        """,
        unsafe_allow_html=True,
    )

    today = date.today()
    st.markdown(
        f"<p style='margin-top:0.5rem; font-size:0.9rem;'>Date: <b>{today.strftime('%d %b %Y')}</b></p>",
        unsafe_allow_html=True,
    )

    # Cycle context
    period_starts = st.session_state.get("period_starts") or []
    if period_starts:
        cycle_summary = compute_cycle_summary(period_starts)
        if cycle_summary:
            days_left = cycle_summary.get("days_until_next_period")
            next_start = cycle_summary.get("predicted_next_period_start")
            st.markdown(
                f"""
                <p style="margin:0.2rem 0; font-size:0.85rem;">
                    Predicted next period: <b>{next_start.strftime('%d %b %Y')}</b><br>
                    Days until then: <b>{days_left}</b>
                </p>
                """,
                unsafe_allow_html=True,
            )

            labels = []
            if cycle_summary.get("is_currently_on_period"):
                labels.append("in a logged period window")
            if cycle_summary.get("is_in_pms_window"):
                labels.append("in your PMS window")
            if cycle_summary.get("is_in_fertile_window"):
                labels.append("in your approx. fertile window")

            if labels:
                st.markdown(
                    "<p style='margin:0.2rem 0; font-size:0.85rem; color:#c6bed8;'>Currently: "
                    + ", ".join(labels)
                    + ".</p>",
                    unsafe_allow_html=True,
                )

    # Latest symptom log context
    symptom_logs = st.session_state.get("symptom_logs") or []
    if symptom_logs:
        latest = symptom_logs[-1]
        d_str = latest["date"].strftime("%d %b %Y")
        mood = latest["mood"]
        pain = latest["pain"]
        flow = latest["flow"]
        st.markdown(
            f"""
            <p style="margin-top:0.6rem; font-size:0.85rem; color:#c6bed8;">
                Latest logged check-in: <b>{d_str}</b><br>
                Mood: <b>{mood}</b> · Pain: <b>{pain}/10</b> · Flow: <b>{flow}</b>
            </p>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<p style='margin-top:0.6rem; font-size:0.85rem; color:#c6bed8;'>"
            "You haven’t logged symptoms yet, but you still deserve help and care.</p>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def _render_emergency_red_flags():
    st.markdown(
        """
        <div class="pb-card" style="border: 1px solid rgba(255, 96, 96, 0.6);">
            <div class="pb-pill">EMERGENCY RED FLAGS</div>
            <p style="margin-top:0.6rem; font-size:0.85rem; color:#f8d0d0;">
                Get medical help <b>immediately</b> (emergency / ER / local equivalent) if:
            </p>
            <ul style="font-size:0.85rem; color:#f8d0d0; margin-top:0.2rem;">
                <li>You are soaking through a pad or tampon in less than an hour for several hours.</li>
                <li>You feel like you might faint, or you actually faint.</li>
                <li>You have sudden, sharp, unbearable pain in your lower abdomen.</li>
                <li>You have chest pain, trouble breathing, or one leg is very swollen and painful.</li>
                <li>You have thoughts of hurting yourself or not wanting to live anymore.</li>
            </ul>
            <p style="margin-top:0.4rem; font-size:0.8rem; color:#fbe3e3;">
                This app cannot judge how serious it is in your body. 
                If your gut says “this feels wrong”, trust that and seek real-world help.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------- INDIVIDUAL SOS BLOCKS -------------

def _pain_sos_block():
    st.markdown(
        """
        <div class="pb-card" style="margin-bottom: 0.9rem;">
            <div class="pb-pill">Pain SOS</div>
            <p style="margin-top:0.55rem; font-size:0.9rem; color:#c6bed8;">
                When your cramps or body pain are doing the most.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Step 1: Check the level**")
    pain_now = st.slider(
        "Right now, how bad is the pain?",
        0,
        10,
        8,
        key="sos_pain_level_slider",
    )

    if pain_now <= 3:
        st.caption("Annoying but manageable – still valid, but maybe not emergency.")
    elif pain_now <= 6:
        st.caption("Medium–high. You deserve proper pain relief and rest.")
    else:
        st.caption(
            "This is intense. Pain above 7–8/10 is not something you just have to ‘tolerate’ forever."
        )

    st.markdown("**Step 2: Immediate body actions (pick 1–2 you can do now)**")
    st.markdown(
        """
        - Put a warm water bag / heating pad on your lower belly or back for 15–20 minutes.  
        - If you can, lie on your side with knees slightly bent or try child’s pose.  
        - Sip warm water or herbal tea slowly.  
        - If it’s safe for you and allowed by your doctor, use your usual prescribed / OTC pain relief.  
        """
    )

    st.markdown("**Step 3: When pain means ‘call a doctor’**")
    st.markdown(
        """
        - If this level of pain is normal for you every month, it’s worth talking to a gynecologist.  
        - If the pain is sudden, sharp, or very different from your usual, treat it seriously.  
        - If pain + fever + vomiting show up together, that can be a medical red flag.  
        """
    )


def _bleeding_sos_block():
    st.markdown(
        """
        <div class="pb-card" style="margin-bottom: 0.9rem;">
            <div class="pb-pill">Bleeding SOS</div>
            <p style="margin-top:0.55rem; font-size:0.9rem; color:#c6bed8;">
                When the amount of blood feels like way too much or just scary.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Check these questions:**")
    st.markdown(
        """
        - Are you soaking through a pad/tampon in under an hour, for several hours in a row?  
        - Are you passing many clots larger than a 1 rupee coin?  
        - Do you feel very weak, dizzy, or short of breath?  
        """
    )

    heavy = st.checkbox(
        "Yes, at least one of these is happening.",
        key="sos_bleeding_heavy_checkbox",
    )
    if heavy:
        st.warning(
            "This level of bleeding can be unsafe. Please treat this as urgent and contact a doctor, "
            "clinic or emergency services as soon as you can."
        )

    st.markdown("**For now (non-emergency moments):**")
    st.markdown(
        """
        - Use higher-absorbency pads / tampons / menstrual cups if possible.  
        - Track roughly how often you’re changing products.  
        - Drink water; heavy bleeding can dehydrate you.  
        - If this keeps happening every cycle, not just once, this absolutely deserves a proper medical check-up.  
        """
    )


def _emotional_sos_block():
    st.markdown(
        """
        <div class="pb-card" style="margin-bottom: 0.9rem;">
            <div class="pb-pill">Emotional SOS</div>
            <p style="margin-top:0.55rem; font-size:0.9rem; color:#c6bed8;">
                When your brain feels heavier than your body.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Step 1: Name it**")
    feeling = st.text_input(
        "In one messy sentence, what does it feel like in your head right now?",
        placeholder="Example: I feel useless and like everyone would be better without me.",
        key="sos_emotional_feeling_input",
    )
    if feeling.strip():
        st.caption("Thank you for putting that into words. That’s not nothing.")

    st.markdown("**Step 2: Tiny grounding in your body (do along)**")
    st.markdown(
        """
        - Look around and name **5 things you can see**.  
        - Touch **4 things you can feel** (clothes, bed, floor, etc.).  
        - Listen for **3 sounds** (fan, street noise, birds, etc.).  
        - Notice **2 things you can smell**.  
        - Think of **1 thing you could taste** if you wanted (water, tea, snack).  
        """
    )

    st.markdown("**Step 3: Safety check**")
    dark_thoughts = st.checkbox(
        "I’ve had thoughts of hurting myself or not wanting to be here.",
        key="sos_emotional_dark_thoughts_checkbox",
    )
    if dark_thoughts:
        st.error(
            "I’m really glad you clicked that. Those thoughts are heavy and serious, "
            "and you do not deserve to carry them alone.\n\n"
            "This app can’t handle crisis by itself. Please, if you can:\n"
            "- Tell a friend, partner, or family member that you’re not okay.\n"
            "- Reach out to a mental health professional or helpline in your area.\n"
            "- If you feel in immediate danger, contact local emergency services.\n"
        )

    st.markdown("**Step 4: One gentle action**")
    st.markdown(
        """
        Pick one, not all:
        - Drink a glass of water slowly.  
        - Sit or lie somewhere a bit more comfortable.  
        - Put on a comfort show / playlist and let yourself just exist.  
        - Text someone “I’m not okay today, can I just talk or be around you?”  
        """
    )

    st.markdown(
        """
        <p style="font-size:0.85rem; color:#c6bed8; margin-top:0.4rem;">
            Your brain saying you’re worthless does not make it true. 
            You being here and reading this already means you haven’t given up.
        </p>
        """,
        unsafe_allow_html=True,
    )


def _dizzy_sos_block():
    st.markdown(
        """
        <div class="pb-card" style="margin-bottom: 0.9rem;">
            <div class="pb-pill">Dizzy / faint / weird symptoms</div>
            <p style="margin-top:0.55rem; font-size:0.9rem; color:#c6bed8;">
                When your body feels off in a way that scares you.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Immediate safety moves:**")
    st.markdown(
        """
        - Sit or lie down <b>right now</b> so you don’t fall.  
        - If possible, keep your phone near you in case you need to call someone.  
        - Take slow, steady breaths.  
        """
    )

    st.markdown("**Check if any of these are true:**")
    chest_pain = st.checkbox(
        "Chest pain / pressure, or trouble breathing.",
        key="sos_dizzy_chest_pain_checkbox",
    )
    one_leg = st.checkbox(
        "One leg is very swollen, red, or painful compared to the other.",
        key="sos_dizzy_one_leg_checkbox",
    )
    blackout = st.checkbox(
        "You actually fainted, or almost blacked out.",
        key="sos_dizzy_blackout_checkbox",
    )
    heart = st.checkbox(
        "Heart racing out of nowhere in a scary way, not just anxiety-ish.",
        key="sos_dizzy_heart_checkbox",
    )

    if chest_pain or one_leg or blackout or heart:
        st.error(
            "These can be serious medical red flags. Please treat this as urgent:\n\n"
            "- Call local emergency services if you can.\n"
            "- Or ask someone near you to help you get to an emergency room / urgent care.\n"
            "- Do not try to ‘tough it out’ alone if your body feels like it’s shutting down.\n"
        )

    st.markdown("**If it feels milder but still scary:**")
    st.markdown(
        """
        - Sip water slowly (not too fast).  
        - Eat something small with salt + carbs if you haven’t eaten in a while.  
        - Book a doctor’s appointment as soon as you reasonably can and describe these symptoms clearly.  
        """
    )

    st.markdown(
        """
        <p style="font-size:0.85rem; color:#c6bed8; margin-top:0.4rem;">
            You know your body better than this app ever could. 
            If your gut says “this is not normal for me”, trust that and get checked.
        </p>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
