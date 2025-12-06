import streamlit as st
import pandas as pd
from datetime import date
from typing import List, Dict, Any, Optional

from utils.cycle_utils import compute_cycle_summary
from utils.auth_utils import init_auth_state, is_logged_in, get_current_profile_name
from utils.session_data import ensure_user_data
from utils.ui_utils import render_page_header


PMS_DAYS = 5  # days before period counted as PMS window


def _build_symptom_dataframe() -> Optional[pd.DataFrame]:
    logs = st.session_state.get("symptom_logs", [])
    if not logs:
        return None

    rows = []
    for entry in logs:
        rows.append(
            {
                "date": entry["date"],
                "pain": entry["pain"],
                "mood": entry["mood"],
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return None

    df = df.sort_values("date").reset_index(drop=True)
    return df


def _build_cycle_df(period_starts: List[date], logs: List[Dict[str, Any]]) -> Optional[pd.DataFrame]:
    if not period_starts or not logs:
        return None

    periods = sorted(period_starts)
    logs_sorted = sorted(logs, key=lambda x: x["date"])

    # PMS windows per period
    pms_windows = []
    for p in periods:
        start = p - pd.Timedelta(days=PMS_DAYS)
        end = p - pd.Timedelta(days=1)
        pms_windows.append((start, end))

    rows = []
    idx = 0

    for entry in logs_sorted:
        d = entry["date"]
        if d < periods[0]:
            continue

        # find which cycle this log belongs to
        while idx + 1 < len(periods) and d >= periods[idx + 1]:
            idx += 1

        period_start = periods[idx]
        cycle_index = idx
        cycle_day = (d - period_start).days + 1

        in_pms = False
        for (pms_start, pms_end) in pms_windows:
            if pms_start <= pd.Timestamp(d) <= pms_end:
                in_pms = True
                break

        rows.append(
            {
                "date": d,
                "pain": entry["pain"],
                "mood": entry["mood"],
                "cycle_index": cycle_index,
                "cycle_day": cycle_day,
                "in_pms_window": in_pms,
            }
        )

    if not rows:
        return None

    df = pd.DataFrame(rows)
    df = df.sort_values(["cycle_index", "date"]).reset_index(drop=True)
    return df


def main():
    init_auth_state()
    if not is_logged_in():
        render_page_header(
            page_title="Home / Overview",
            subtitle="Your dashboard shows up here after you log in and start tracking.",
        )
        st.warning("Please log in on the '0_Login / Profile' page to see your dashboard.")
        return

    username = get_current_profile_name()
    ensure_user_data(username)

    today = date.today()

    render_page_header(
        page_title="Home / Overview",
        subtitle="Quick view of your cycle, pain, and mood patterns using your logs.",
    )

    #  TOP METRICS
    col_top_left, col_top_mid, col_top_right = st.columns(3)

    with col_top_left:
        st.markdown("#### Today")
        st.metric("Date", today.strftime("%d %b %Y"))

    period_starts = st.session_state.get("period_starts", [])

    with col_top_mid:
        if period_starts:
            summary = compute_cycle_summary(period_starts)
            if summary:
                days_left = summary["days_until_next_period"]
                st.metric("Days until next period", days_left)
            else:
                st.metric("Days until next period", "—")
        else:
            st.metric("Days until next period", "—")

    with col_top_right:
        logs = st.session_state.get("symptom_logs", [])
        if logs:
            latest = logs[-1]
            st.metric(
                "Latest pain (0–10)",
                latest["pain"],
                help="From your last Symptoms & Mood log.",
            )
        else:
            st.metric("Latest pain (0–10)", "—")

    st.divider()

    # ROW 1: SNAPSHOT + BASIC TREND
    col_bottom_left, col_bottom_right = st.columns([1.7, 1.3])

    with col_bottom_left:
        st.markdown("#### Cycle snapshot")

        if not period_starts:
            st.info(
                "No period history yet. Log some dates in the Cycle Tracker page and I’ll show predictions here."
            )
        else:
            summary = compute_cycle_summary(period_starts)
            if not summary:
                st.warning("Not enough info yet to show a proper summary.")
            else:
                next_start = summary["predicted_next_period_start"]
                next_end = summary["predicted_next_period_end"]
                pms_start = summary["pms_window_start"]
                pms_end = summary["pms_window_end"]
                fertile_start = summary["fertile_window_start"]
                fertile_end = summary["fertile_window_end"]
                avg_cycle = summary["average_cycle_length_days"]

                st.markdown(
                    f"""
                    <div class="pb-card" style="margin-bottom: 0.9rem;">
                        <div class="pb-pill">Next period window</div>
                        <p style="margin-top:0.55rem; font-size:0.9rem;">
                            <b>{next_start.strftime('%d %b %Y')}</b> → <b>{next_end.strftime('%d %b %Y')}</b>
                        </p>
                        <p style="margin-top:0.3rem; font-size:0.85rem; color:#c6bed8;">
                            Using average cycle length of <b>{avg_cycle} days</b> from your logs / settings.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="pb-card" style="margin-bottom: 0.9rem;">
                        <div class="pb-pill">PMS & fertile windows</div>
                        <p style="margin-top:0.55rem; font-size:0.9rem;">
                            PMS: <b>{pms_start.strftime('%d %b %Y')}</b> → <b>{pms_end.strftime('%d %b %Y')}</b><br>
                            Fertile (rough): <b>{fertile_start.strftime('%d %b %Y')}</b> → <b>{fertile_end.strftime('%d %b %Y')}</b>
                        </p>
                        <p style="margin-top:0.3rem; font-size:0.8rem; color:#c6bed8;">
                            This is all approximate and not a reliable method of pregnancy prevention.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("#### Pain trend (recent logs)")

        df_basic = _build_symptom_dataframe()
        if df_basic is None or df_basic.empty:
            st.caption("Log your Symptoms & Mood to see a pain graph here.")
        else:
            df_plot = df_basic.set_index("date")[["pain"]]
            st.line_chart(df_plot)

    with col_bottom_right:
        st.markdown("#### Mood history")

        df_basic = _build_symptom_dataframe()
        if df_basic is None or df_basic.empty:
            st.info(
                "Once you log moods, I’ll summarise them here so you can see patterns "
                "around your cycle."
            )
        else:
            latest_row = df_basic.sort_values("date").iloc[-1]
            st.markdown(
                f"""
                <div class="pb-card" style="margin-bottom: 0.9rem;">
                    <div class="pb-pill">Latest log</div>
                    <p style="margin-top:0.55rem; font-size:0.9rem;">
                        Date: <b>{latest_row['date'].strftime('%d %b %Y')}</b><br>
                        Mood: <b>{latest_row['mood']}</b><br>
                        Pain: <b>{latest_row['pain']}/10</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            mood_counts = df_basic["mood"].value_counts()
            st.markdown(
                """
                <div class="pb-card" style="margin-bottom: 0.9rem;">
                    <div class="pb-pill">Most common moods</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for mood, count in mood_counts.items():
                st.markdown(f"- {mood}: **{count}×**")

        st.markdown(
            """
            <div class="pb-card">
                <div class="pb-pill">How to use this</div>
                <p style="margin-top:0.55rem; font-size:0.85rem; color:#c6bed8;">
                    Over time, you’ll start to see patterns: which days of your cycle your mood dips, 
                    when pain spikes, what kind of weeks feel heavier. 
                    The point isn’t to judge yourself, but to understand your body better.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    #  ROW 2: ADVANCED PATTERNS
    st.divider()
    st.markdown("### Patterns across cycles")

    df_cycle = _build_cycle_df(
        period_starts=st.session_state.get("period_starts", []),
        logs=st.session_state.get("symptom_logs", []),
    )

    if df_cycle is None or df_cycle.empty:
        st.caption(
            "Once you have at least one period logged and a few Symptoms & Mood entries, "
            "I’ll start showing deeper patterns here."
        )
        return

    col_adv_left, col_adv_mid, col_adv_right = st.columns(3)

    # 1) Pain vs cycle day
    with col_adv_left:
        st.markdown("#### Pain vs cycle day")

        pain_by_day = (
            df_cycle.groupby("cycle_day")["pain"]
            .mean()
            .reset_index()
            .sort_values("cycle_day")
        )
        pain_by_day = pain_by_day.set_index("cycle_day")
        st.line_chart(pain_by_day, height=220)

        st.caption(
            "Each point = average pain on that day of your cycle (Day 1 = first day of period). "
            "Spikes can show which days tend to hit hardest."
        )

    # 2) Mood vs PMS window
    with col_adv_mid:
        st.markdown("#### Mood inside vs outside PMS")

        df_pms = df_cycle.copy()
        if df_pms["in_pms_window"].any():
            pms_counts = df_pms[df_pms["in_pms_window"]]["mood"].value_counts()
            non_counts = df_pms[~df_pms["in_pms_window"]]["mood"].value_counts()

            all_moods = sorted(set(pms_counts.index).union(non_counts.index))
            mood_vs_pms = pd.DataFrame(
                {
                    "Mood": all_moods,
                    "PMS window": [pms_counts.get(m, 0) for m in all_moods],
                    "Outside PMS": [non_counts.get(m, 0) for m in all_moods],
                }
            ).set_index("Mood")

            st.bar_chart(mood_vs_pms, height=220)

            st.caption(
                f"PMS window is counted as the last {PMS_DAYS} days before each period start. "
                "You might see certain moods cluster more in that window."
            )
        else:
            st.caption(
                "I don’t have any logs in PMS windows yet (last few days before a period). "
                "Once you log more around those days, I’ll compare moods here."
            )

    # 3) Average pain per cycle
    with col_adv_right:
        st.markdown("#### Average pain per cycle")

        pain_per_cycle = (
            df_cycle.groupby("cycle_index")["pain"]
            .mean()
            .reset_index()
            .sort_values("cycle_index")
        )

        if pain_per_cycle.empty:
            st.caption("Not enough data yet to calculate per-cycle averages.")
        else:
            pain_per_cycle["Cycle"] = pain_per_cycle["cycle_index"].apply(
                lambda i: f"Cycle {i + 1}"
            )
            chart_df = pain_per_cycle.set_index("Cycle")[["pain"]]
            st.bar_chart(chart_df, height=220)
            st.caption(
                "Each bar is the average pain across one full cycle. "
                "You can see if some cycles were rougher than others."
            )


if __name__ == "__main__":
    main()
