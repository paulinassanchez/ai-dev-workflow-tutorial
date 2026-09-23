# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tutorial project: students build a Streamlit e-commerce sales dashboard (`prd/ecommerce-analytics.md`) using a structured AI-assisted workflow (PRD → `TASKS.md` milestones → Superpowers brainstorming/writing-plans/executing-plans skills → code → deploy). The dashboard itself is intentionally simple; the point is the workflow. See `README.md` for the full course context.

## Commands

```bash
# Activate the venv (plain venv, no uv/conda; already gitignored)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run the full test suite (pytest.ini sets pythonpath=. so this works from repo root)
pytest -v

# Run a single test file or test
pytest tests/test_sales_data.py -v
pytest tests/test_sales_data.py::test_compute_total_sales_sums_total_amount -v
```

There is no build/lint step — this is a two-file Python project.

## Architecture

- **`sales_data.py`** — pure calculation/loading functions only. No Streamlit or Plotly imports. Owns `SalesDataError`, `load_sales_data`, and every `compute_*` aggregation. This is the only module covered by tests.
- **`app.py`** — thin Streamlit UI layer. Imports from `sales_data.py`, calls its functions, renders KPI cards (`st.metric`) and Plotly charts. Contains no calculation logic — if you're adding math, it belongs in `sales_data.py`, not here.
- **`tests/test_sales_data.py`** — tests `sales_data.py` only, against small synthetic DataFrames built inline (`pd.DataFrame(...)` or `tmp_path` for CSV tests). Never imports Streamlit and never touches the real CSV at `data/sales-data.csv`.
- Data flows one direction: `data/sales-data.csv` → `sales_data.py` (load/validate/compute) → `app.py` (render). Required CSV columns: `date, order_id, product, category, region, quantity, unit_price, total_amount`.

Project conventions to preserve:
- Every chart uses one accent color, `#2a78d6`, on Streamlit's default light theme — no per-series categorical colors, no custom CSS theming.
- Charts use Plotly `hovertemplate` for currency-formatted tooltips, not raw values.
- `compute_total_orders` counts unique `order_id` values, not raw row count.
- Code favors simplicity over abstraction (no classes, no premature helpers) — this is a tutorial project, not production software.

## Workflow this repo follows

- `TASKS.md` is the source of truth for milestone status (To Do / In Progress / Done), each milestone with acceptance criteria and a `Commit:` line. Design docs and implementation plans for a milestone live under `docs/superpowers/specs/` and `docs/superpowers/plans/`.
- Definition of Done (from `TASKS.md`): acceptance criteria met, app runs locally with `streamlit run app.py`, and changes are committed with the milestone ID (e.g. `TASK-3: ...`) in the message.
- Established commit convention: moving a milestone between board columns gets its own commit (e.g. `TASK-6: move milestone to In Progress on the task board`, `TASK-6: mark done on the board`), separate from the implementation commit(s) for that milestone.
- Work happens directly on `feature/sales-dashboard` — no git worktree.
- The deployment milestone (TASK-7 / Task 11 in the plan) is a manual, developer-run step after merging to `main` — do not execute it as an agent task.

## Lessons

Rules distilled from the `Notes:` lines in `TASKS.md` — read those for full context.

- This environment has no browser access. Verify dashboard behavior by computing values directly with `sales_data.py` functions against the real CSV, and by running `streamlit run app.py --server.headless true` and checking the HTTP response/log — never claim a visual check happened.
- Always pass `--server.headless true` when running Streamlit non-interactively (background process, no TTY). Without it, Streamlit's first-run onboarding-email prompt blocks on stdin and the process exits nonzero.
- For a `git commit` message with an apostrophe, quotes, or multiple lines, write it to a file and use `git commit -F <file>` — a quoted heredoc breaks on an embedded apostrophe.
- Don't trust a plan's own test expectations at face value — cross-check them against the milestone's acceptance criteria and test name. TASK-5's plan had a test asserting ascending order for a function whose name and acceptance criteria both call for descending; the test was wrong, not the implementation.
- When polishing a milestone, diff the implementation against the design spec (`docs/superpowers/specs/`), not just against the plan's code — a milestone's acceptance criteria can pass while still drifting from the spec (e.g. TASK-4 shipped `2024-01`-style month labels when the spec called for `Jan 2024`; TASK-6 caught it).
- If the user asks for manual/step-by-step mode, stop for approval between steps — don't run a plan straight through.
