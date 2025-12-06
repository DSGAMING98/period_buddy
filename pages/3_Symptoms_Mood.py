import streamlit as st
from datetime import date

import pandas as pd

from utils.symptom_utils import SYMPTOM_ALIASES, analyze_symptoms
from utils.storage_utils import save_symptom_logs
from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.session_data import ensure_user_data
from utils.ui_utils import render_page_header


def main():
    init_auth_state()
    if not is_logged_in():
        render_page_header(
            page_title="Symptoms & Mood",
            subtitle="Log how your body and brain feel to unlock personalised support.",
        )
        st.warning("Please log in on the '0_Login / Profile' page to log symptoms and mood.")
        return

    username = get_current_profile_name()
    ensure_user_data(username)

    render_page_header(
        page_title="Symptoms & Mood",
        subtitle="Track pain, flow, and emotions; get practical tips and gentle validation.",
    )

    col_left, col_right = st.columns([2, 1.3])

    #  LEFT: INPUT
    with col_left:
        st.markdown("#### Today’s check-in")

        entry_date = st.date_input(
            "Date",
            value=date.today(),
            max_value=date.today(),
        )

        symptoms = st.multiselect(
            "What are you feeling in your body?",
            options=list(SYMPTOM_ALIASES.keys()),
            help="You can pick multiple: cramps, back pain, bloating, low mood, etc.",
        )

        pain_scale = st.slider(
            "Pain level right now (0 = chill, 10 = I want to scream):",
            min_value=0,
            max_value=10,
            value=4,
        )

        flow_level = st.selectbox(
            "Bleeding / flow level right now:",
            [
                "Not on period",
                "Spotting",
                "Light",
                "Medium",
                "Heavy",
                "Very heavy",
            ],
        )
        flow_for_logic = None if flow_level == "Not on period" else flow_level

        mood_label = st.selectbox(
            "Emotion-wise, what’s closest to how you feel?",
            [
                "Chill",
                "Sad / low mood",
                "Irritated / angry",
                "Anxious",
                "Numb / meh",
                "Overwhelmed",
                "Pretty okay",
            ],
        )

        notes = st.text_area(
            "Anything you want to add? (optional)",
            placeholder="Example: Fought with someone, slept badly, ate late, super stressed about exams, etc.",
        )

        if st.button("Analyze today & save", type="primary"):
            result = analyze_symptoms(
                selected_labels=symptoms,
                pain_scale=pain_scale,
                flow_level=flow_for_logic,
                mood_label=mood_label,
            )

            logs = st.session_state.get("symptom_logs", [])
            log_entry = {
                "date": entry_date,
                "symptoms": symptoms,
                "pain": pain_scale,
                "flow": flow_level,
                "mood": mood_label,
                "notes": notes.strip(),
                "analysis": result,
            }
            logs.append(log_entry)
            st.session_state["symptom_logs"] = logs

            save_symptom_logs(logs, username)

            st.success("Saved and analyzed ✅; Scroll right to see your personalized breakdown.")
            _show_analysis(result)

        # Export
        st.markdown("#### Export logs")

        logs = st.session_state.get("symptom_logs", [])
        if logs:
            df = _logs_to_dataframe(logs)
            csv_bytes = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download symptoms & mood logs (CSV)",
                data=csv_bytes,
                file_name="symptom_mood_logs.csv",
                mime="text/csv",
                help="Download all your logged entries (date, pain, mood, flow, symptoms, notes).",
            )
        else:
            st.caption("Once you have some logs, you can export them as CSV from here.")

    #  RIGHT: ANALYSIS
    with col_right:
        st.markdown("#### Current analysis")

        logs = st.session_state.get("symptom_logs", [])
        if logs:
            latest = logs[-1]
            _show_analysis(latest["analysis"])
        else:
            st.info("Log your symptoms on the left to see personalized tips here.")

        st.markdown("#### Recent check-ins")

        if not logs:
            st.caption("Your recent days will appear here once you start logging.")
        else:
            last_entries = logs[-5:][::-1]
            for entry in last_entries:
                date_str = entry["date"].strftime("%d %b %Y")
                mood = entry["mood"]
                pain = entry["pain"]
                sev = entry["analysis"]["severity_label"]

                st.markdown(
                    f"""
                    <div class="pb-card" style="margin-bottom: 0.45rem; padding: 0.65rem 0.8rem;">
                        <div class="pb-pill">Log — {date_str}</div>
                        <p style="margin: 0.35rem 0 0.15rem 0; font-size: 0.9rem;">
                            Mood: <b>{mood}</b> · Pain: <b>{pain}/10</b> · Overall: <b>{sev.capitalize()}</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _show_analysis(result: dict) -> None:
    severity = result["severity_label"]
    tips = result["combined_tips"]
    mood_support = result["mood_support"]
    general_support = result["general_support"]
    red_flags = result["red_flags"]

    sev_color = {
        "mild": "#7cf5ff",
        "moderate": "#ffb347",
        "severe": "#ff4b8a",
        "unknown": "#c6bed8",
    }.get(severity, "#c6bed8")

    st.markdown(
        f"""
        <div class="pb-card" style="margin-bottom: 0.8rem;">
            <div class="pb-pill">Overall intensity</div>
            <h4 style="margin-top: 0.6rem; margin-bottom: 0.3rem; color: {sev_color};">
                {severity.capitalize()}
            </h4>
            <p style="margin: 0.2rem 0; font-size: 0.9rem; color: #c6bed8;">
                This is a rough label based on your pain level, symptoms, and flow. 
                It’s here to validate what you’re feeling, not minimise it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if tips:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 0.8rem;">
                <div class="pb-pill">Body comfort tips</div>
            """,
            unsafe_allow_html=True,
        )
        for t in tips:
            st.markdown(f"- {t}")
        st.markdown("</div>", unsafe_allow_html=True)

    if mood_support:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 0.8rem;">
                <div class="pb-pill">Emotion check-in</div>
            """,
            unsafe_allow_html=True,
        )
        for m in mood_support:
            st.markdown(f"- {m}")
        st.markdown("</div>", unsafe_allow_html=True)

    if general_support:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 0.8rem;">
                <div class="pb-pill">Gentle reminders</div>
            """,
            unsafe_allow_html=True,
        )
        for g in general_support:
            st.markdown(f"- {g}")
        st.markdown("</div>", unsafe_allow_html=True)

    if red_flags:
        st.markdown(
            """
            <div class="pb-card" style="border: 1px solid rgba(255, 96, 96, 0.6); margin-bottom: 0.4rem;">
                <div class="pb-pill">When to consider a doctor</div>
            """,
            unsafe_allow_html=True,
        )
        for r in red_flags:
            st.markdown(f"- {r}")
        st.markdown(
            "<p style='font-size:0.8rem; color:#f8d0d0; margin-top:0.4rem;'>"
            "This app is not a doctor. If anything feels scary or unusual for you, "
            "please trust your gut and see a professional.</p></div>",
            unsafe_allow_html=True,
        )


def _logs_to_dataframe(logs):
    rows = []
    for entry in logs:
        rows.append(
            {
                "date": entry["date"].strftime("%Y-%m-%d"),
                "pain": entry.get("pain", None),
                "mood": entry.get("mood", None),
                "flow": entry.get("flow", None),
                "symptoms": ", ".join(entry.get("symptoms", [])),
                "notes": entry.get("notes", ""),
            }
        )
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    main()
