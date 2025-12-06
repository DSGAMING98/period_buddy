from __future__ import annotations

import streamlit as st

from utils.storage_utils import load_period_starts, load_symptom_logs


def ensure_user_data(username: str) -> None:
    """
    Make sure session_state['period_starts'] and ['symptom_logs'] belong
    to the given username. If user switched, reload fresh from disk.
    """
    owner_key = "data_user"

    if st.session_state.get(owner_key) == username:
        return

    st.session_state["period_starts"] = load_period_starts(username)
    st.session_state["symptom_logs"] = load_symptom_logs(username)
    st.session_state[owner_key] = username
