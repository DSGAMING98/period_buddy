import time
import streamlit as st

from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.session_data import ensure_user_data
from utils.cycle_utils import compute_cycle_summary
from utils.ui_utils import render_page_header
from utils.offline_chat import generate_reply


def _build_chat_context() -> dict:
    """
    Build context for the AI from current session:
    - cycle summary
    - latest mood / pain / flow from symptom logs
    """
    ctx: dict = {}

    # Cycle context
    period_starts = st.session_state.get("period_starts") or []
    if period_starts:
        try:
            ctx["cycle_summary"] = compute_cycle_summary(period_starts)
        except Exception:
            ctx["cycle_summary"] = None

    # Symptom / mood context
    symptom_logs = st.session_state.get("symptom_logs") or []
    if symptom_logs:
        latest = symptom_logs[-1]
        ctx["latest_mood"] = latest.get("mood")
        ctx["latest_pain"] = latest.get("pain")
        ctx["latest_flow"] = latest.get("flow")

    return ctx


def _init_chat_history():
    if "pb_chat_history" not in st.session_state:
        # role = "user" | "assistant"
        st.session_state["pb_chat_history"] = [
            {
                "role": "assistant",
                "content": (
                    "Hey, I’m Period Buddy.\n\n"
                    "You can vent about body stuff (cramps, nausea, bleeding, weird symptoms), "
                    "brain stuff (overthinking, sadness, anger), or both. "
                    "I’ll react based on what you say + what you’ve tracked, but I’m not a doctor or therapist."
                ),
            }
        ]


def _render_chat_history():
    for msg in st.session_state["pb_chat_history"]:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)


def main():
    init_auth_state()

    if not is_logged_in():
        render_page_header(
            page_title="Period Buddy AI",
            subtitle="Offline chat that actually knows your cycle — but you need to log in first.",
        )
        st.warning("Log in on the Login/Profile page to use the chat.")
        return

    username = get_current_profile_name()
    ensure_user_data(username)

    render_page_header(
        page_title="Period Buddy AI",
        subtitle="Chat with your offline, hormone-aware buddy. I read your logs, but your data never leaves this device.",
    )

    # Small description under header
    st.markdown(
        """
        This chat is:
        - Fully offline (no servers, no API calls).  
        - A mix of body + brain support, based on what you type.  
        - Not a doctor / diagnosis, but something in between journaling and a friend who actually reads your cycle data.
       
        - Also the AI might be/ is very dumb. So only try asking and chatting about periods and that related stuff.  
        - I only appended very few human emotions. So no ChatGPT type but it's similar. Best I could do
        """.strip()
    )

    _init_chat_history()
    _render_chat_history()

    # Clear chat button (optional)
    with st.sidebar:
        if st.button("Clear Period Buddy chat"):
            st.session_state["pb_chat_history"] = []
            _init_chat_history()
            st.rerun()

    # Chat input – this feels like real chat (like we’re using now)
    user_input = st.chat_input("Tell me what’s going on — body, brain, or both?")

    if user_input:
        # 1) Add user message to history
        st.session_state["pb_chat_history"].append(
            {"role": "user", "content": user_input}
        )

        # 2) Build context from cycle + symptom logs
        context = _build_chat_context()

        # 3) Render assistant “typing” + response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            # fake typing dots
            placeholder.markdown("⋯")
            time.sleep(0.6)

            reply = generate_reply(user_input, context)
            placeholder.markdown(reply)

        # 4) Save reply to history so it persists on rerun
        st.session_state["pb_chat_history"].append(
            {"role": "assistant", "content": reply}
        )


# Streamlit pages execute top-level, so we call main() directly
main()
