import streamlit as st
from datetime import date

import pandas as pd

from utils.cycle_utils import compute_cycle_summary
from utils.storage_utils import save_period_starts
from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.session_data import ensure_user_data
from utils.ui_utils import render_page_header


def main():
    init_auth_state()
    if not is_logged_in():
        render_page_header(
            page_title="Cycle Tracker",
            subtitle="Log your period start dates to unlock predictions and patterns.",
        )
        st.warning("Please log in on the '0_Login / Profile' page to use the Cycle Tracker.")
        return

    username = get_current_profile_name()
    ensure_user_data(username)

    render_page_header(
        page_title="Cycle Tracker",
        subtitle="Estimate next period, PMS window, and fertile window from your history.",
    )

    col_form, col_side = st.columns([2, 1])

    #  LEFT: LOGGING
    with col_form:
        st.markdown("#### Log a period start")

        period_starts = st.session_state.get("period_starts", [])
        last_default = period_starts[-1] if period_starts else date.today()

        start_date = st.date_input(
            "Select the first day of your period:",
            value=last_default,
            max_value=date.today(),
        )

        avg_cycle_manual = st.number_input(
            "Typical cycle length (days) (optional, used for predictions):",
            min_value=20,
            max_value=40,
            value=28,
            step=1,
            help="If you know your usual cycle length, set it here. Otherwise, I’ll try to estimate from your history.",
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Save / update this date"):
                if start_date not in period_starts:
                    period_starts.append(start_date)
                period_starts = sorted(period_starts)

                st.session_state["period_starts"] = period_starts
                save_period_starts(period_starts, username)

                st.success("Period date saved ✅")

        with col_btn2:
            if st.button("Clear all logged periods"):
                st.session_state["period_starts"] = []
                save_period_starts([], username)
                st.warning("All logged period dates cleared.")

        st.markdown("#### Your logged periods")

        period_starts = st.session_state.get("period_starts", [])
        if not period_starts:
            st.info("No period history yet. Add at least one start date above.")
        else:
            history_str = "\n".join(
                f"- {d.strftime('%d %b %Y')}" for d in period_starts
            )
            st.markdown(history_str)

            df = pd.DataFrame(
                {
                    "period_start": [
                        d.strftime("%Y-%m-%d") for d in period_starts
                    ]
                }
            )
            csv_bytes = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download period history (CSV)",
                data=csv_bytes,
                file_name="period_history.csv",
                mime="text/csv",
                help="Download your logged period start dates as a CSV file.",
            )

    #  RIGHT: SUMMARY
    with col_side:
        st.markdown("#### Cycle summary (preview)")

        period_starts = st.session_state.get("period_starts", [])
        if not period_starts:
            st.info("Once you log some dates, I’ll show your predicted next period and windows here.")
            return

        summary = compute_cycle_summary(
            period_starts,
            average_cycle_length=int(avg_cycle_manual) if avg_cycle_manual else None,
        )

        if not summary:
            st.warning("Not enough information yet to estimate your cycle.")
            return

        next_start = summary["predicted_next_period_start"]
        next_end = summary["predicted_next_period_end"]
        pms_start = summary["pms_window_start"]
        pms_end = summary["pms_window_end"]
        fertile_start = summary["fertile_window_start"]
        fertile_end = summary["fertile_window_end"]
        days_left = summary["days_until_next_period"]
        avg_cycle = summary["average_cycle_length_days"]

        st.markdown(
            f"""
            <div class="pb-card" style="margin-bottom: 0.9rem;">
                <div class="pb-pill">Next period</div>
                <h4 style="margin-top: 0.7rem; margin-bottom: 0.4rem;">Estimated window</h4>
                <p style="margin: 0.1rem 0;">
                    <b>{next_start.strftime('%d %b %Y')}</b> → <b>{next_end.strftime('%d %b %Y')}</b>
                </p>
                <p style="margin: 0.4rem 0 0.2rem 0; font-size: 0.9rem; color: #c6bed8;">
                    Typical cycle length I’m using: <b>{avg_cycle} days</b>
                </p>
                <p style="margin: 0.2rem 0; font-size: 0.9rem; color: #c6bed8;">
                    Days until next period: <b>{days_left}</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="pb-card" style="margin-bottom: 0.9rem;">
                <div class="pb-pill">PMS window</div>
                <p style="margin-top:0.6rem; margin-bottom:0.2rem;">
                    <b>{pms_start.strftime('%d %b %Y')}</b> → <b>{pms_end.strftime('%d %b %Y')}</b>
                </p>
                <p style="margin:0.2rem 0; font-size:0.9rem; color:#c6bed8;">
                    You might feel mood, energy, or craving changes around here.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="pb-card">
                <div class="pb-pill">Fertile window (rough)</div>
                <p style="margin-top:0.6rem; margin-bottom:0.2rem;">
                    <b>{fertile_start.strftime('%d %b %Y')}</b> → <b>{fertile_end.strftime('%d %b %Y')}</b>
                </p>
                <p style="margin:0.2rem 0; font-size:0.85rem; color:#c6bed8;">
                    This is a rough estimate only and <b>not</b> a reliable method for pregnancy prevention.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        status_msg = []
        if summary["is_currently_on_period"]:
            status_msg.append("You’re currently within a logged period window.")
        if summary["is_in_pms_window"]:
            status_msg.append("You’re in your PMS window right now.")
        if summary["is_in_fertile_window"]:
            status_msg.append("You’re in your approximate fertile window.")

        if status_msg:
            st.success(" ".join(status_msg))
        else:
            st.caption("Today doesn’t fall in PMS, fertile, or period windows based on current data.")


if __name__ == "__main__":
    main()
