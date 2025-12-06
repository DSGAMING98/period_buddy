from __future__ import annotations

from pathlib import Path
import streamlit as st

APP_NAME = "Period Buddy"
APP_VERSION = "v1.0 – Offline Edition"
LOGO_PATH = Path("assets/logo.png")


def render_page_header(page_title: str, subtitle: str | None = None) -> None:
    """
    Standard header for every page:
    - logo on the left
    - app name + version
    - page title
    """
    col_logo, col_text = st.columns([0.2, 0.8])

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
        else:
            # Fallback if logo is missing
            st.markdown(
                "<div style='font-size: 2rem; font-weight: 700; letter-spacing: 0.08em;'>PB</div>",
                unsafe_allow_html=True,
            )

    with col_text:
        st.markdown(
            f"""
            <div class="pb-header">
                <div class="pb-header-top">
                    <span class="pb-app-name">{APP_NAME}</span>
                    <span class="pb-app-version">{APP_VERSION}</span>
                </div>
                <div class="pb-page-title">{page_title}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if subtitle:
            st.caption(subtitle)

    st.divider()
