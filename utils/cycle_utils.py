from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional, Dict, Any

# Default assumptions (you can tweak these later or make them user-configurable)
DEFAULT_CYCLE_LENGTH_DAYS = 28
DEFAULT_PERIOD_LENGTH_DAYS = 5
DEFAULT_PMS_LENGTH_DAYS = 5
FERTILE_OFFSET_START_DAYS = 14  # days before next period
FERTILE_OFFSET_END_DAYS = 10    # days before next period


def _clean_and_sort_dates(period_start_dates: List[date]) -> List[date]:
    """
    Internal helper.
    - Removes duplicates
    - Sorts from oldest -> newest
    """
    unique_dates = sorted(set(period_start_dates))
    return unique_dates


def estimate_average_cycle_length(period_start_dates: List[date]) -> Optional[int]:
    """
    Given a list of period start dates (unordered),
    return an estimated average cycle length in days.

    If there is only one date, returns None (not enough info).
    """
    dates = _clean_and_sort_dates(period_start_dates)
    if len(dates) < 2:
        return None

    gaps = []
    for i in range(1, len(dates)):
        diff = (dates[i] - dates[i - 1]).days
        if diff > 0:
            gaps.append(diff)

    if not gaps:
        return None

    avg = sum(gaps) / len(gaps)
    return int(round(avg))


def compute_cycle_summary(
    period_start_dates: List[date],
    average_cycle_length: Optional[int] = None,
    period_length_days: int = DEFAULT_PERIOD_LENGTH_DAYS,
    reference_date: Optional[date] = None,
) -> Optional[Dict[str, Any]]:
    """
    Core function:
    - Takes a list of period start dates (date objects)
    - Optionally an average cycle length if user wants to override
    - Returns predicted next period, PMS window, fertile window, and flags.

    Returns None if there is no usable period data.
    """
    if not period_start_dates:
        return None

    dates = _clean_and_sort_dates(period_start_dates)
    last_start = dates[-1]

    # Use passed-in avg or estimate from data or default fallback
    if average_cycle_length is None:
        estimated = estimate_average_cycle_length(dates)
        if estimated is None:
            avg_cycle = DEFAULT_CYCLE_LENGTH_DAYS
        else:
            avg_cycle = estimated
    else:
        avg_cycle = average_cycle_length

    # Choose "today" if no reference date is provided
    ref = reference_date or date.today()

    # Predicted next period start
    predicted_next_start = last_start + timedelta(days=avg_cycle)
    predicted_next_end = predicted_next_start + timedelta(days=period_length_days - 1)

    # PMS window = last few days before predicted next period
    pms_start = predicted_next_start - timedelta(days=DEFAULT_PMS_LENGTH_DAYS)
    pms_end = predicted_next_start - timedelta(days=1)

    # Fertile window = approx range before ovulation (very rough, not medical)
    fertile_start = predicted_next_start - timedelta(days=FERTILE_OFFSET_START_DAYS)
    fertile_end = predicted_next_start - timedelta(days=FERTILE_OFFSET_END_DAYS)

    # Derived flags
    days_until_next_period = (predicted_next_start - ref).days

    is_on_period = last_start <= ref <= (last_start + timedelta(days=period_length_days - 1))
    is_in_pms = pms_start <= ref <= pms_end
    is_in_fertile = fertile_start <= ref <= fertile_end

    summary: Dict[str, Any] = {
        "reference_date": ref,
        "last_period_start": last_start,
        "average_cycle_length_days": avg_cycle,
        "predicted_next_period_start": predicted_next_start,
        "predicted_next_period_end": predicted_next_end,
        "pms_window_start": pms_start,
        "pms_window_end": pms_end,
        "fertile_window_start": fertile_start,
        "fertile_window_end": fertile_end,
        "days_until_next_period": days_until_next_period,
        "is_currently_on_period": is_on_period,
        "is_in_pms_window": is_in_pms,
        "is_in_fertile_window": is_in_fertile,
        # You can add more later (e.g. cycle regularity score)
    }

    return summary
