from __future__ import annotations

from typing import Optional

import streamlit as st


def pb_card(
    pill: Optional[str] = None,
    body_md: str = "",
    margin_bottom: str = "0.9rem",
) -> None:
    """
    Render a Period Buddy styled card using the .pb-card CSS.
    body_md is markdown/HTML content for inside the card.
    """
    pill_html = ""
    if pill:
        pill_html = f'<div class="pb-pill">{pill}</div>'

    st.markdown(
        f"""
        <div class="pb-card" style="margin-bottom: {margin_bottom};">
            {pill_html}
            {body_md}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pb_metric_card(
    pill: str,
    label: str,
    value: str,
    extra_md: str = "",
) -> None:
    """
    Small pre-styled card for showing a value + label.
    """
    st.markdown(
        f"""
        <div class="pb-card" style="margin-bottom: 0.9rem;">
            <div class="pb-pill">{pill}</div>
            <h4 style="margin-top:0.55rem; margin-bottom:0.3rem;">{label}</h4>
            <p style="margin-top:0.1rem; font-size:1.1rem;"><b>{value}</b></p>
            <p style="margin-top:0.3rem; font-size:0.85rem; color:#c6bed8;">
                {extra_md}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pb_info_text(text: str) -> None:
    """
    Quick helper for soft info text with consistent style.
    """
    st.markdown(
        f"<p style='font-size:0.85rem; color:#c6bed8;'>{text}</p>",
        unsafe_allow_html=True,
    )
