import streamlit as st

from utils.ui_utils import render_page_header


def main():
    # Simple, calm, millennial-style tone here
    render_page_header(
        page_title="Author’s Note",
        subtitle="A small thank you, a bit of context, and proper credit where it’s due."
    )

    st.markdown(
        """
        ### Thank you for being here

        If you’re reading this, you’ve already done something important:  
        you took time to check in with your body and your cycle instead of just powering through it in silence.

        Period Buddy was built to be:
        - A private, offline space to track what your body is doing  
        - A gentle nudge to notice patterns instead of ignoring them  
        - A companion on rough days, not a replacement for real medical care  

        None of this works without you actually using it, logging honestly, and coming back on the good days *and* the bad ones.
        So, truly: thank you for trusting the app enough to spend your time here.
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ### Why this exists

        This project started from a simple idea:  
        periods affect almost everything – mood, focus, energy, pain –  
        but most tools either feel too clinical or too shallow.

        Period Buddy tries to sit in the middle:
        - Practical enough to help you notice red flags  
        - Warm enough to feel like a human built it, not a corporation  
        - Honest about its limits: it can support you, not diagnose you  
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ### Credits & creator

        **Developed by:**  
        **Prajwal Pradhan**  

        Built with:
        - Python & Streamlit  
        - A lot of late-night debugging  
        - A lot of respect for anyone dealing with cramps, mood swings, and life at the same time  

        If this app helped you feel even a little more seen or a little more in control of your cycle,  
        then all the effort behind the scenes was worth it.
        """
    )

    st.markdown("---")

    st.markdown(
        """
        ### A gentle reminder

        Period Buddy is designed as:
        - A supportive companion  
        - A pattern-spotter  
        - A place to listen and reflect  

        It is **not** a doctor, therapist, or emergency service.  
        If something feels seriously wrong in your body or in your mind,  
        please reach out to a real-world professional or someone you trust.
        """
    )

    st.markdown("---")

    st.markdown(
        """
        #### Legal & copyright

        © 2025 Period Buddy by Prajwal Pradhan.  
        All rights reserved.  

        You’re welcome to use this app for personal support,  
        but please don’t copy, resell, or redistribute it as your own work.
        """
    )

    st.caption(
        "And yes, this was written with care. Any women who like the app – "
        "Love you guys too back. Hope this had been helpful to you in some way."
    )


# Streamlit executes modules top-level, so just call main()
main()
