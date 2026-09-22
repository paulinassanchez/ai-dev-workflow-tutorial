# Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 e-commerce sales dashboard from `prd/ecommerce-analytics.md` — a Streamlit app showing Total Sales / Total Orders KPIs, a monthly sales trend line chart, and category/region bar charts, loaded from `data/sales-data.csv`.

**Architecture:** A pure-function data module (`sales_data.py`) loads and validates the CSV and computes every metric; `app.py` is a thin Streamlit UI layer that calls into it and renders KPI cards + Plotly charts. Calculation functions are covered by pytest tests against small synthetic DataFrames; `app.py` is verified manually.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly, pytest.

**Spec:** `docs/superpowers/specs/2026-09-21-sales-dashboard-design.md`

## Global Constraints

- Work happens directly on the current branch, `feature/sales-dashboard` — no git worktree.
- Dependencies live in a plain virtual environment at `venv/` with a `requirements.txt` (no uv, no conda). `venv/` is already gitignored.
- Calculation logic lives in `sales_data.py`, fully separate from the Streamlit UI in `app.py`, and is tested with pytest in `tests/test_sales_data.py`.
- Code favors simplicity and readability over abstraction — no classes, no premature helpers.
- Required CSV columns: `date, order_id, product, category, region, quantity, unit_price, total_amount`.
- `compute_total_orders` counts unique `order_id` values, not raw row count.
- Every chart uses a single accent color, `#2a78d6`, on Streamlit's default light theme.
- Every commit message is prefixed with the `TASKS.md` milestone ID it belongs to (e.g. `TASK-1: ...`), per the Definition of Done.

## Milestone → Plan Task Map

`TASKS.md` tracks milestones (TASK-1 ... TASK-7); this plan's own tasks are numbered separately (Task 1 ... Task 11) so the two numbering schemes never collide.

| TASKS.md milestone | Plan tasks |
|---|---|
| TASK-1: Environment setup and project initialization | Task 1 |
| TASK-2: Data loading and basic structure | Task 2, Task 3 |
| TASK-3: KPI cards implementation | Task 4, Task 5 |
| TASK-4: Sales trend chart | Task 6, Task 7 |
| TASK-5: Category and region breakdowns | Task 8, Task 9 |
| TASK-6: Testing and refinement | Task 10 |
| TASK-7: Deployment to Streamlit Community Cloud | Task 11 (developer's manual step — see below) |

## File Structure

- `requirements.txt` — created in Task 1: `streamlit`, `pandas`, `plotly`, `pytest`.
- `app.py` — created in Task 1 (minimal shell); extended in Task 3 (data loading + error handling), Task 5 (KPI cards), Task 7 (trend chart), Task 9 (category/region charts). Streamlit UI only — no calculation logic.
- `sales_data.py` — created in Task 2 (`SalesDataError`, `load_sales_data`); extended in Task 4 (`compute_total_sales`, `compute_total_orders`), Task 6 (`compute_monthly_trend`), Task 8 (`compute_sales_by_category`, `compute_sales_by_region`). Pure functions, no Streamlit/Plotly imports.
- `tests/test_sales_data.py` — created in Task 2, extended in Tasks 4, 6, 8. Tests only `sales_data.py`, using small synthetic DataFrames built inline via `tmp_path` (for CSV tests) or `pd.DataFrame(...)` (for calculation tests). Never touches the real CSV.
- `venv/` — created in Task 1, not committed (already gitignored).

---

### Task 1: Project setup, dependencies, and minimal app shell

**Milestone:** TASK-1

**Files:**
- Create: `requirements.txt`
- Create: `app.py`

**Interfaces:**
- Produces: an importable, runnable `app.py` that later tasks extend.

- [ ] **Step 1: Create the virtual environment**

Run: `python3 -m venv venv`

- [ ] **Step 2: Activate it and install dependencies**

Write `requirements.txt`:

```
streamlit
pandas
plotly
pytest
```

Run:
```bash
source venv/bin/activate
pip install -r requirements.txt
```
Expected: all four packages install with no errors.

- [ ] **Step 3: Write the minimal app shell**

Create `app.py`:

```python
import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 4: Verify it runs**

Run: `streamlit run app.py`
Expected: terminal shows no errors/warnings; browser opens to a page titled "ShopSmart Sales Dashboard" with that heading visible. Stop the server with Ctrl+C.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app.py
git commit -m "TASK-1: set up project dependencies and minimal app shell"
```

---

### Task 2: Data loading with validation (TDD)

**Milestone:** TASK-2

**Files:**
- Create: `sales_data.py`
- Test: `tests/test_sales_data.py`

**Interfaces:**
- Produces: `class SalesDataError(Exception)`, `load_sales_data(csv_path: str) -> pd.DataFrame` — later tasks (3, 4, 6, 8) import both from `sales_data`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_sales_data.py`:

```python
import pandas as pd
import pytest

from sales_data import SalesDataError, load_sales_data

VALID_COLUMNS = [
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
]


def _write_csv(tmp_path, rows, columns):
    path = tmp_path / "sales.csv"
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)
    return str(path)


def test_load_sales_data_returns_dataframe_with_parsed_types(tmp_path):
    rows = [
        ["2024-01-03", "ORD-001", "Wireless Earbuds", "Audio", "North", 2, 79.99, 159.98],
        ["2024-02-04", "ORD-002", "Phone Case", "Accessories", "South", 3, 24.99, 74.97],
    ]
    path = _write_csv(tmp_path, rows, VALID_COLUMNS)

    df = load_sales_data(path)

    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["total_amount"].tolist() == [159.98, 74.97]


def test_load_sales_data_missing_file_raises_sales_data_error(tmp_path):
    missing_path = str(tmp_path / "does-not-exist.csv")

    with pytest.raises(SalesDataError, match="not found"):
        load_sales_data(missing_path)


def test_load_sales_data_missing_column_raises_sales_data_error(tmp_path):
    rows = [["2024-01-03", "ORD-001", "Wireless Earbuds", "Audio", "North", 2, 79.99]]
    columns = VALID_COLUMNS[:-1]  # drop total_amount
    path = _write_csv(tmp_path, rows, columns)

    with pytest.raises(SalesDataError, match="missing required columns"):
        load_sales_data(path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_sales_data.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sales_data'` (or `ImportError`).

- [ ] **Step 3: Implement `sales_data.py`**

Create `sales_data.py`:

```python
"""Data loading and calculation functions for the sales dashboard."""

import pandas as pd

REQUIRED_COLUMNS = [
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
]


class SalesDataError(Exception):
    """Raised when the sales CSV is missing or malformed."""


def load_sales_data(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise SalesDataError(f"Sales data file not found: {csv_path}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise SalesDataError(
            f"Sales data is missing required columns: {', '.join(missing)}"
        )

    try:
        df["date"] = pd.to_datetime(df["date"])
        df["quantity"] = pd.to_numeric(df["quantity"])
        df["unit_price"] = pd.to_numeric(df["unit_price"])
        df["total_amount"] = pd.to_numeric(df["total_amount"])
    except (ValueError, TypeError) as exc:
        raise SalesDataError(
            f"Sales data contains values that could not be parsed: {exc}"
        ) from exc

    return df
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_sales_data.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-2: add CSV loading with validation"
```

---

### Task 3: Wire data loading into the dashboard with error handling

**Milestone:** TASK-2

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `SalesDataError`, `load_sales_data(csv_path: str) -> pd.DataFrame` from `sales_data` (Task 2).
- Produces: a module-level `df` in `app.py` that Tasks 5, 7, 9 read from.

- [ ] **Step 1: Update `app.py`**

Replace the contents of `app.py` with:

```python
import streamlit as st

from sales_data import SalesDataError, load_sales_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

try:
    df = load_sales_data("data/sales-data.csv")
except SalesDataError as e:
    st.error(str(e))
    st.stop()
```

- [ ] **Step 2: Verify the happy path**

Run: `streamlit run app.py`
Expected: page loads with no errors; title shows. Stop the server with Ctrl+C.

- [ ] **Step 3: Verify the error path**

Temporarily rename the data file, rerun, then restore it:

```bash
mv data/sales-data.csv data/sales-data.csv.bak
streamlit run app.py
```
Expected: page shows a red `st.error` message containing "Sales data file not found" — no traceback, no crash. Stop the server with Ctrl+C, then restore the file:

```bash
mv data/sales-data.csv.bak data/sales-data.csv
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-2: load sales data into the dashboard with error handling"
```

---

### Task 4: Total Sales and Total Orders calculations (TDD)

**Milestone:** TASK-3

**Files:**
- Modify: `sales_data.py`
- Test: `tests/test_sales_data.py`

**Interfaces:**
- Produces: `compute_total_sales(df: pd.DataFrame) -> float`, `compute_total_orders(df: pd.DataFrame) -> int` — Task 5 imports both.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sales_data.py`:

```python
from sales_data import compute_total_orders, compute_total_sales


def _kpi_sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-02-01"]),
        "order_id": ["ORD-001", "ORD-002", "ORD-002"],
        "category": ["Audio", "Accessories", "Accessories"],
        "region": ["North", "South", "South"],
        "total_amount": [159.98, 74.97, 24.99],
    })


def test_compute_total_sales_sums_total_amount():
    df = _kpi_sample_df()

    assert compute_total_sales(df) == 259.94


def test_compute_total_orders_counts_unique_order_ids():
    df = _kpi_sample_df()  # ORD-002 appears twice

    assert compute_total_orders(df) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_sales_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'compute_total_orders'`.

- [ ] **Step 3: Implement the functions**

Append to `sales_data.py`:

```python
def compute_total_sales(df: pd.DataFrame) -> float:
    return float(df["total_amount"].sum())


def compute_total_orders(df: pd.DataFrame) -> int:
    return int(df["order_id"].nunique())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_sales_data.py -v`
Expected: all tests pass (5 total so far).

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-3: add total sales and total orders calculations"
```

---

### Task 5: Render KPI cards

**Milestone:** TASK-3

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `compute_total_sales`, `compute_total_orders` from `sales_data` (Task 4); `df` from Task 3.

- [ ] **Step 1: Update `app.py`**

Change the import line:

```python
from sales_data import (
    SalesDataError,
    compute_total_orders,
    compute_total_sales,
    load_sales_data,
)
```

Append after the `try/except` block:

```python
total_sales = compute_total_sales(df)
total_orders = compute_total_orders(df)

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: two KPI cards render — Total Sales as currency with no decimals (e.g. `$116,500`), Total Orders as a comma-formatted count matching the PRD's expected ~482. Stop the server with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-3: render Total Sales and Total Orders KPI cards"
```

---

### Task 6: Monthly sales trend calculation (TDD)

**Milestone:** TASK-4

**Files:**
- Modify: `sales_data.py`
- Test: `tests/test_sales_data.py`

**Interfaces:**
- Produces: `compute_monthly_trend(df: pd.DataFrame) -> pd.DataFrame` with columns `month` (pandas `Period`, freq `M`) and `total_sales`, sorted chronologically. Task 7 imports this.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_sales_data.py`:

```python
from sales_data import compute_monthly_trend


def test_compute_monthly_trend_groups_and_sorts_chronologically():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-02-01", "2024-01-03", "2024-01-04"]),
        "total_amount": [100.0, 50.0, 25.0],
    })

    trend = compute_monthly_trend(df)

    assert trend["month"].astype(str).tolist() == ["2024-01", "2024-02"]
    assert trend["total_sales"].tolist() == [75.0, 100.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sales_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'compute_monthly_trend'`.

- [ ] **Step 3: Implement the function**

Append to `sales_data.py`:

```python
def compute_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.assign(month=df["date"].dt.to_period("M"))
        .groupby("month")["total_amount"]
        .sum()
        .reset_index(name="total_sales")
        .sort_values("month")
        .reset_index(drop=True)
    )
    return monthly
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sales_data.py -v`
Expected: all tests pass (6 total so far).

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-4: add monthly sales trend calculation"
```

---

### Task 7: Render the sales trend chart

**Milestone:** TASK-4

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `compute_monthly_trend` from `sales_data` (Task 6).

- [ ] **Step 1: Update `app.py`**

Add to the top imports:

```python
import plotly.express as px
```

Change the `sales_data` import to include `compute_monthly_trend`:

```python
from sales_data import (
    SalesDataError,
    compute_monthly_trend,
    compute_total_orders,
    compute_total_sales,
    load_sales_data,
)
```

Append after the KPI card block:

```python
trend = compute_monthly_trend(df)
trend["month_label"] = trend["month"].astype(str)

st.subheader("Sales Trend")
trend_fig = px.line(trend, x="month_label", y="total_sales", markers=True)
trend_fig.update_traces(
    line_color="#2a78d6",
    hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
)
trend_fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
st.plotly_chart(trend_fig, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: a line chart renders below the KPI cards, one point per month, x-axis labeled by month (e.g. `2024-01`), hovering a point shows `2024-01: $9,234` (currency-formatted, not a raw float). Stop the server with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-4: render sales trend line chart"
```

---

### Task 8: Category and region breakdown calculations (TDD)

**Milestone:** TASK-5

**Files:**
- Modify: `sales_data.py`
- Test: `tests/test_sales_data.py`

**Interfaces:**
- Produces: `compute_sales_by_category(df: pd.DataFrame) -> pd.DataFrame`, `compute_sales_by_region(df: pd.DataFrame) -> pd.DataFrame`, both with columns `category`/`region` and `total_sales`, sorted descending. Task 9 imports both.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sales_data.py`:

```python
from sales_data import compute_sales_by_category, compute_sales_by_region


def _breakdown_sample_df():
    return pd.DataFrame({
        "category": ["Audio", "Accessories", "Audio"],
        "region": ["North", "South", "South"],
        "total_amount": [100.0, 30.0, 50.0],
    })


def test_compute_sales_by_category_sums_and_sorts_descending():
    df = _breakdown_sample_df()

    result = compute_sales_by_category(df)

    assert result["category"].tolist() == ["Audio", "Accessories"]
    assert result["total_sales"].tolist() == [150.0, 30.0]


def test_compute_sales_by_region_sums_and_sorts_descending():
    df = _breakdown_sample_df()

    result = compute_sales_by_region(df)

    assert result["region"].tolist() == ["South", "North"]
    assert result["total_sales"].tolist() == [80.0, 100.0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_sales_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'compute_sales_by_category'`.

- [ ] **Step 3: Implement the functions**

Append to `sales_data.py`:

```python
def compute_sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")["total_amount"]
        .sum()
        .reset_index(name="total_sales")
        .sort_values("total_sales", ascending=False)
        .reset_index(drop=True)
    )


def compute_sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region")["total_amount"]
        .sum()
        .reset_index(name="total_sales")
        .sort_values("total_sales", ascending=False)
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_sales_data.py -v`
Expected: all tests pass (8 total so far).

- [ ] **Step 5: Commit**

```bash
git add sales_data.py tests/test_sales_data.py
git commit -m "TASK-5: add category and region breakdown calculations"
```

---

### Task 9: Render category and region bar charts

**Milestone:** TASK-5

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `compute_sales_by_category`, `compute_sales_by_region` from `sales_data` (Task 8).

- [ ] **Step 1: Update `app.py`**

Change the `sales_data` import to include both new functions:

```python
from sales_data import (
    SalesDataError,
    compute_monthly_trend,
    compute_sales_by_category,
    compute_sales_by_region,
    compute_total_orders,
    compute_total_sales,
    load_sales_data,
)
```

Append after the trend chart block:

```python
by_category = compute_sales_by_category(df)
by_region = compute_sales_by_region(df)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Sales by Category")
    category_fig = px.bar(by_category, x="category", y="total_sales")
    category_fig.update_traces(
        marker_color="#2a78d6",
        hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
    )
    category_fig.update_layout(xaxis_title="Category", yaxis_title="Sales ($)")
    st.plotly_chart(category_fig, use_container_width=True)

with col4:
    st.subheader("Sales by Region")
    region_fig = px.bar(by_region, x="region", y="total_sales")
    region_fig.update_traces(
        marker_color="#2a78d6",
        hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
    )
    region_fig.update_layout(xaxis_title="Region", yaxis_title="Sales ($)")
    st.plotly_chart(region_fig, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run: `streamlit run app.py`
Expected: two bar charts render side by side below the trend chart — categories and regions each sorted highest to lowest by sales, hovering a bar shows currency-formatted exact values. Stop the server with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-5: render category and region breakdown charts"
```

---

### Task 10: Full-suite verification and polish

**Milestone:** TASK-6

**Files:**
- Modify: `app.py` (only if a polish issue is found)

**Interfaces:**
- Consumes: the complete `app.py` and `sales_data.py` from Tasks 1-9.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: all 8 tests pass, no warnings.

- [ ] **Step 2: Verify against the PRD's expected output**

Run: `streamlit run app.py`
Expected, matching the PRD's Expected Output table:
- Total Sales ≈ `$116,500`
- Total Orders: `482`
- Top category by sales: Electronics
- Regions shown: North, South, East, West
- No errors or warnings in the terminal or browser console.

- [ ] **Step 3: Polish pass**

With the app still running, check: KPI/chart spacing is even, no overlapping labels, subheaders are present above each chart, the page reads cleanly at a glance (NFR-2: "professional appearance suitable for executive presentations"). If anything is off, fix it directly in `app.py` (e.g., adjust `st.subheader` text or column ratios) — this is a non-TDD visual fix, not a calculation change. Stop the server with Ctrl+C when done.

- [ ] **Step 4: Commit (only if Step 3 changed anything)**

```bash
git add app.py
git commit -m "TASK-6: polish dashboard layout and verify against PRD expected output"
```

If Step 3 made no changes, skip this commit — there's nothing to save.

---

### Task 11: Deploy to Streamlit Community Cloud

**Milestone:** TASK-7

**⚠️ Do not execute this task.** Every prior task is built and verified on `feature/sales-dashboard`; this one runs only after that branch is merged into `main`, and it's the developer's step to run by hand, not the agent's. When the plan reaches this point, stop and hand off with a summary of what's ready to deploy.

For the developer, once `feature/sales-dashboard` is merged into `main`:

1. Push `main` to GitHub (`git push origin main`) if it isn't already up to date.
2. Sign in to [Streamlit Community Cloud](https://streamlit.io/cloud) with the GitHub account that owns this repo.
3. Click "New app," select this repository, branch `main`, and main file path `app.py`.
4. Deploy and wait for the build to finish (it installs from `requirements.txt`).
5. Open the resulting public URL and confirm it matches local behavior: same KPI values, same charts, no errors.
6. Record the public URL and update `TASKS.md`: move TASK-7 to Done, check off its acceptance criteria, and fill in its `Commit:` line.

---

## Self-Review

**Spec coverage:** Architecture & data flow → Tasks 1-3. Data module signatures → Tasks 2, 4, 6, 8 (all five functions plus `SalesDataError` match the spec exactly). Error handling → Task 3. UI layout & visual design (KPI cards, monthly trend, sorted bar charts, single accent color, currency-formatted hover) → Tasks 5, 7, 9. Testing strategy (synthetic DataFrames, no real CSV, no `app.py` unit tests) → Tasks 2, 4, 6, 8, 10. Out-of-scope items (auth, database, export, alerts, filtering, drill-down, mobile) → correctly absent from every task.

**Placeholder scan:** No TBD/TODO markers; every step has runnable code or an exact command; no "similar to Task N" references — each task's code is written out in full, including cumulative import lists.

**Type consistency:** `load_sales_data(csv_path: str) -> pd.DataFrame` (Task 2) is the exact signature imported in Task 3. `compute_total_sales`/`compute_total_orders` (Task 4) match their Task 5 call sites. `compute_monthly_trend` returns `month`/`total_sales` columns (Task 6), consumed as `trend["month"]`/`trend["total_sales"]` in Task 7. `compute_sales_by_category`/`compute_sales_by_region` return `category`/`region` + `total_sales` (Task 8), consumed identically in Task 9. No naming drift found.
