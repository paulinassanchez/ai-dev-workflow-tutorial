# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard described in `prd/ecommerce-analytics.md`.

## Definition of Done

Before any milestone moves to Done, all of the following must be true:
- Acceptance criteria for the milestone are met
- App runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the commit message

## To Do

- **TASK-7: Deployment to Streamlit Community Cloud**
  Publish the dashboard to a public URL for stakeholder access.
  - [ ] App is deployed to Streamlit Community Cloud and reachable via a public URL
  - [ ] Deployed app matches local behavior (no errors, correct data)
  - Commit:

## In Progress

## Done

- **TASK-6: Testing and refinement**
  Validate correctness and polish the dashboard for stakeholder review.
  - [x] Dashboard runs with no errors or warnings and matches the PRD's Expected Output (~$116,500 total sales, 482 orders)
  - [x] Appearance is professional and suitable for an executive presentation
  - Commit: ffddde4
  - Notes: Full pytest suite passes (8/8, no warnings). Ran `streamlit run app.py` headlessly and curled it (HTTP 200, no errors/warnings in the server log besides the routine Watchdog performance tip) since this session has no browser access; confirmed exact values directly against the real CSV instead of visually: Total Sales $116,500.21, Total Orders 482, top category Electronics, all four regions (North, South, East, West) present — matches the PRD. Polish pass found one real gap against the design spec: the trend chart's month axis showed raw `2024-01` strings instead of the spec's `Jan 2024` format; fixed and re-verified chronological ordering holds (Plotly preserves row order for string category axes, confirmed directly).

- **TASK-5: Category and region breakdowns**
  Add bar charts for sales by category and by region.
  - [x] Category bar chart shows all categories, sorted highest to lowest
  - [x] Region bar chart shows all regions, sorted highest to lowest
  - [x] Both charts have interactive tooltips with exact values
  - Commit: f9ffa6d
  - Notes: The plan's own test for `compute_sales_by_region` had its expected values backwards — asserting ascending order despite the test name and this milestone's acceptance criteria both calling for descending. Fixed the test to expect descending order to match `compute_sales_by_category`'s identical sort pattern; no implementation code needed to change. Verified against the real CSV: top category is Electronics, all four regions present — both match the PRD.

- **TASK-4: Sales trend chart**
  Add a line chart showing sales over time.
  - [x] Line chart plots sales by date (daily or monthly) with correct values
  - [x] Interactive tooltips show exact values on hover
  - Commit: 1d63622
  - Notes: Verified the underlying monthly totals directly (12 months, chronologically sorted, summing to the validated $116,500) rather than visually in a browser, since this session has no browser access.

- **TASK-3: KPI cards implementation**
  Display the two headline metrics at the top of the dashboard.
  - [x] Total Sales shown as formatted currency ($X,XXX,XXX)
  - [x] Total Orders shown as a formatted count
  - Commit: 0245f29
  - Notes: Verified against the real CSV directly ($116,500 / 482 orders, matching the PRD) rather than visually in a browser, since this session has no browser access.

- **TASK-2: Data loading and basic structure**
  Load and parse the sales CSV into a usable DataFrame.
  - [x] Loads `data/sales-data.csv` and correctly parses date, numeric, and categorical columns
  - [x] Missing or malformed CSV is handled cleanly, without a crash
  - Commit: eac8080
  - Notes: Bare `pytest` couldn't import sales_data.py (ModuleNotFoundError) since the project had no config putting the project root on sys.path; root cause confirmed via `python -m pytest` vs. bare `pytest`. Fixed by adding pytest.ini (`pythonpath = .`), not part of the original plan. No test or implementation code changed.

- **TASK-1: Environment setup and project initialization**
  Set up the project structure, dependencies, and a minimal runnable Streamlit app.
  - [x] `streamlit run app.py` launches without errors and shows a page title
  - [x] Dependencies (streamlit, pandas, plotly) are declared and install cleanly
  - Commit: 9e80c55
  - Notes: First pass ran without stopping for per-step approval; redone in manual mode after a clean git reset, per request. Code itself (requirements.txt, app.py) was correct both times.
