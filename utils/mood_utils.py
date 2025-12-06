from __future__ import annotations

from datetime import date
from typing import List, Dict, Any, Optional

import pandas as pd


# Consistent mood labels -> numeric scores for plotting / stats
MOOD_SCORE_MAP: Dict[str, int] = {
    "Chill": 3,
    "Pretty okay": 3,
    "Numb / meh": 2,
    "Sad / low mood": 1,
    "Irritated / angry": 1,
    "Anxious": 1,
    "Overwhelmed": 0,
}


def logs_to_dataframe(logs: List[Dict[str, Any]]) -> Optional[pd.DataFrame]:
    """
    Convert symptom_logs (from session/storage) into a clean DataFrame.

    Expected entry shape:
    {
      "date": date,
      "symptoms": [str, ...],
      "pain": int,
      "flow": str,
      "mood": str,
      "notes": str,
      "analysis": {...}   # optional
    }
    """
    if not logs:
        return None

    rows = []
    for entry in logs:
        d = entry.get("date")
        if not isinstance(d, date):
            # Skip weird entries
            continue

        rows.append(
            {
                "date": d,
                "pain": entry.get("pain", None),
                "mood": entry.get("mood", None),
                "flow": entry.get("flow", None),
                "symptoms": entry.get("symptoms", []),
                "notes": entry.get("notes", ""),
            }
        )

    if not rows:
        return None

    df = pd.DataFrame(rows)
    df = df.sort_values("date").reset_index(drop=True)

    # Add numeric mood score if possible
    df["mood_score"] = df["mood"].map(MOOD_SCORE_MAP).astype("Int64")

    return df


def mood_counts(df: pd.DataFrame) -> Dict[str, int]:
    """
    Return frequency of each mood in the dataframe.

    df should have a 'mood' column.
    """
    if df is None or "mood" not in df.columns:
        return {}

    counts = df["mood"].value_counts(dropna=True)
    return counts.to_dict()


def average_pain(df: pd.DataFrame) -> Optional[float]:
    """
    Compute overall average pain from df['pain'].
    Returns None if no pain data.
    """
    if df is None or "pain" not in df.columns:
        return None

    series = df["pain"].dropna()
    if series.empty:
        return None

    return float(series.mean())


def recent_window(df: pd.DataFrame, days: int = 30) -> Optional[pd.DataFrame]:
    """
    Filter dataframe to only last N days.
    """
    if df is None or df.empty:
        return None

    latest_date = df["date"].max()
    cutoff = latest_date - pd.Timedelta(days=days)

    df_window = df[df["date"] >= cutoff].copy()
    if df_window.empty:
        return None
    return df_window
