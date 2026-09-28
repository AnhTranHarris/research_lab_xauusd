"""R10 Alpha: source-aware, chronological, month-block XAUUSD tick research engine."""
from .data import (MONTH_SHA256, PRICE_SCALE, BAR_WIDTHS_MS, prepare_month,
                   load_month, bars_from_ticks, month_iso_week_rollup)