# Sales Dashboard — Design

Source: `prd/ecommerce-analytics.md` (Phase 1 scope only). Task board: `TASKS.md` (TASK-1 through TASK-7).

## Overview

A single-page Streamlit dashboard that loads `data/sales-data.csv` and shows two KPI cards, a monthly sales trend line chart, and two bar charts (sales by category, sales by region). No filtering, authentication, or database integration — those are explicitly Phase 2 in the PRD.

## Constraints

- Plain Python virtual environment in `venv/` with a `requirements.txt` (no uv, no conda). `venv/` is already gitignored.
- Work happens directly on the current feature branch (`feature/sales-dashboard`); no git worktree.
- Calculation logic lives in its own module with pytest tests, separate from the Streamlit UI.
- Code favors simplicity and readability over abstraction — this is a tutorial project, not a production system.
- Deployment to Streamlit Community Cloud is out of scope for this design/plan; it is a manual step the developer runs from `main` after merge.

## Architecture & Data Flow

```
sales-data.csv → sales_data.py (load + validate + calculate) → app.py (Streamlit UI) → browser
```

- **`sales_data.py`** — pure functions, no Streamlit or Plotly imports. Owns loading/validating the CSV and every calculation the dashboard needs.
- **`app.py`** — imports `sales_data.py`, calls its functions, and renders the page: page config, KPI columns, then the three charts. No calculation logic lives here.
- **`requirements.txt`** — `streamlit`, `pandas`, `plotly`, `pytest`.
- **`tests/test_sales_data.py`** — exercises `sales_data.py` only, against small synthetic DataFrames built inline. Never imports Streamlit, never touches the real CSV.

This keeps calculation logic decoupled from the UI (testable without running the dashboard) and keeps `app.py` a thin, readable rendering layer.

## Data Module

`sales_data.py` exposes:

```python
class SalesDataError(Exception):
    """Raised when the sales CSV is missing or malformed."""

def load_sales_data(csv_path: str) -> pd.DataFrame:
    """Load and validate the CSV. Raises SalesDataError on a missing file,
    missing required columns, or values that fail to parse as dates/numbers."""

def compute_total_sales(df: pd.DataFrame) -> float:
    """Sum of total_amount across all rows."""

def compute_total_orders(df: pd.DataFrame) -> int:
    """Count of unique order_id values (not raw row count)."""

def compute_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Columns: month (pandas Period, freq='M'), total_sales.
    Grouped by calendar month, sorted chronologically. app.py formats
    the month for display (e.g., "Jan 2024") when building the chart."""

def compute_sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Columns: category, total_sales. Sorted descending by total_sales."""

def compute_sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Columns: region, total_sales. Sorted descending by total_sales."""
```

Notes:
- `compute_total_orders` counts unique `order_id` values rather than raw rows — matches "count of transactions" from FR-1 and stays correct if the data ever contains duplicate rows for one order. For the current CSV both approaches agree (482).
- `load_sales_data` never lets a raw pandas/OS exception escape; it always raises `SalesDataError` with a human-readable message for: file not found, missing required columns, or unparseable data.
- Required columns: `date, order_id, product, category, region, quantity, unit_price, total_amount` (per the PRD's data specification).

## Error Handling (UI)

In `app.py`, the load call is wrapped:

```python
try:
    df = load_sales_data("data/sales-data.csv")
except SalesDataError as e:
    st.error(str(e))
    st.stop()
```

`st.stop()` prevents the KPI/chart layout from attempting to render against missing data — the user sees only the error message, never a broken dashboard shell or a raw traceback.

## UI Layout & Visual Design

`st.set_page_config(layout="wide")`. Layout matches the PRD's mockup:

```
┌─────────────────────────────────────────────┐
│         ShopSmart Sales Dashboard            │
├───────────────────┬───────────────────────────┤
│   Total Sales      │   Total Orders            │
├───────────────────┴───────────────────────────┤
│         Sales Trend (line, full width)          │
├───────────────────┬───────────────────────────┤
│  Sales by Category │   Sales by Region          │
│  (bar)             │   (bar)                    │
└───────────────────┴───────────────────────────┘
```

- **KPI cards**: `st.columns(2)` + `st.metric()`. Total Sales formatted as currency with no decimals (`$116,500`); Total Orders formatted as a comma-separated count.
- **Trend chart**: monthly granularity (12 points across the year) — chosen over daily because 482 orders spread across ~365 days would produce a noisy line, and Phase 2 explicitly excludes date-range filtering, so there's no way to let the user zoom in later.
- **Category / region charts**: vertical bar charts, sorted descending by value, matching the PRD mockup.
- **Color**: all three charts are single-series (one line; one set of ranked bars) — axis labels already identify each month/category/region, so no categorical color-per-series is needed. A single accent blue (`#2a78d6`) is reused consistently across all three charts, on Streamlit's default light theme. No custom CSS theming.
- **Interactivity**: Plotly's built-in hover tooltips satisfy the "interactive tooltips with exact values" requirement (FR-2/3/4); hover text is formatted as currency rather than raw floats.

## Testing Strategy

- `tests/test_sales_data.py` covers only `sales_data.py`.
- Each test builds a small synthetic DataFrame inline (4-6 rows spanning 2+ categories/regions/months) so expected values are easy to hand-calculate and verify by reading the test — no dependency on the real 482-row CSV.
- Coverage:
  - `load_sales_data`: valid file loads correctly; missing file raises `SalesDataError`; missing/malformed columns raise `SalesDataError`.
  - `compute_total_sales`: correct sum.
  - `compute_total_orders`: correct unique count, including a case with a duplicate `order_id` to confirm it doesn't double-count.
  - `compute_monthly_trend`: correct grouping and chronological sort.
  - `compute_sales_by_category` / `compute_sales_by_region`: correct sums, sorted descending.
- `app.py` itself is not unit-tested — it's a thin rendering layer verified manually via `streamlit run app.py`, per the Definition of Done in `TASKS.md`.

## Out of Scope (Phase 2, per PRD)

User authentication, real-time database integration, export (PDF/Excel), email alerts, filtering/date-range selection, drill-down to transaction detail, mobile-responsive design.
