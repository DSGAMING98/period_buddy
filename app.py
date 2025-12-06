import streamlit as st

from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.ui_utils import render_page_header


# PAGE CONFIG
st.set_page_config(
    page_title="Period Buddy",
    page_icon="🩸",
    layout="wide",
)


#  LOAD CUSTOM CSS
def load_css(file_path: str) -> None:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css("assets/styles.css")


#  MAIN LANDING PAGE
def main():
    init_auth_state()

    render_page_header(
        page_title="Welcome",
        subtitle=(
            "An offline, AI-feeling period buddy that helps track your cycle, symptoms, "
            "mood and self-care."
        ),
    )

    col1, col2 = st.columns([1.7, 1.3])

    with col1:
        st.markdown(
            """
            <div class="pb-card" style="margin-bottom: 1rem;">
                <div class="pb-pill">How to use</div>
                <p style="margin-top:0.5rem; font-size:0.9rem; color:#c6bed8;">
                    Use the <b>sidebar</b> on the left to move between pages:
                </p>
                <ul style="font-size:0.9rem; color:#f9f5ff; margin-top:0.4rem;">
                    <li><b>0_Login / Profile</b> — create a profile and log in so your data stays private.</li>
                    <li><b>Home / Overview</b> — dashboard with your next period estimate, pain graph and mood history.</li>
                    <li><b>Cycle Tracker</b> — log period start dates and see PMS + fertile windows.</li>
                    <li><b>Symptoms & Mood</b> — log pain, flow, mood and get practical tips + emotional support.</li>
                    <li><b>AI Buddy Chat</b> — vent to an offline, rule-based “bestie” that responds with context.</li>
                    <li><b>Self-Care</b> — menu of coping ideas for cramps, mood, fatigue, sleep, cravings, etc.</li>
                    <li><b>SOS</b> — “I’m not okay” mode with quick actions and red-flag info (not medical advice).</li>
                </ul>
                <p style="margin-top:0.6rem; font-size:0.85rem; color:#c6bed8;">
                    Nothing here is a medical diagnosis. It’s a support tool to understand your body better 
                    and remind you that what you’re feeling is real.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if is_logged_in():
            user = get_current_profile_name() or "Unknown"
            st.markdown(
                f"""
                <div class="pb-card" style="margin-bottom: 1rem;">
                    <div class="pb-pill">Profile</div>
                    <p style="margin-top:0.5rem; font-size:0.9rem; color:#c6bed8;">
                        Logged in as <b>{user}</b>.<br>
                        You can manage your account on the <b>0_Login / Profile</b> page.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="pb-card" style="margin-bottom: 1rem;">
                    <div class="pb-pill">Profile</div>
                    <p style="margin-top:0.5rem; font-size:0.9rem; color:#c6bed8;">
                        You’re not logged in yet.<br>
                        Go to <b>0_Login / Profile</b> in the sidebar to create or sign into a profile. 
                        All tracking data is tied to that profile only.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="pb-card">
                <div class="pb-pill">Next step</div>
                <p style="margin-top:0.5rem; font-size:0.9rem; color:#c6bed8;">
                    Start by logging your period dates in <b>Cycle Tracker</b>, then add a 
                    <b>Symptoms & Mood</b> check-in. After that, the <b>Home</b> dashboard and 
                    <b>AI Buddy Chat</b> will feel way more personal.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
