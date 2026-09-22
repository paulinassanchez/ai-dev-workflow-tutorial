# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard described in `prd/ecommerce-analytics.md`.

## Definition of Done

Before any milestone moves to Done, all of the following must be true:
- Acceptance criteria for the milestone are met
- App runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the commit message

## To Do

- **TASK-2: Data loading and basic structure**
  Load and parse the sales CSV into a usable DataFrame.
  - [ ] Loads `data/sales-data.csv` and correctly parses date, numeric, and categorical columns
  - [ ] Missing or malformed CSV is handled cleanly, without a crash
  - Commit:

- **TASK-3: KPI cards implementation**
  Display the two headline metrics at the top of the dashboard.
  - [ ] Total Sales shown as formatted currency ($X,XXX,XXX)
  - [ ] Total Orders shown as a formatted count
  - Commit:

- **TASK-4: Sales trend chart**
  Add a line chart showing sales over time.
  - [ ] Line chart plots sales by date (daily or monthly) with correct values
  - [ ] Interactive tooltips show exact values on hover
  - Commit:

- **TASK-5: Category and region breakdowns**
  Add bar charts for sales by category and by region.
  - [ ] Category bar chart shows all categories, sorted highest to lowest
  - [ ] Region bar chart shows all regions, sorted highest to lowest
  - [ ] Both charts have interactive tooltips with exact values
  - Commit:

- **TASK-6: Testing and refinement**
  Validate correctness and polish the dashboard for stakeholder review.
  - [ ] Dashboard runs with no errors or warnings and matches the PRD's Expected Output (~$116,500 total sales, 482 orders)
  - [ ] Appearance is professional and suitable for an executive presentation
  - Commit:

- **TASK-7: Deployment to Streamlit Community Cloud**
  Publish the dashboard to a public URL for stakeholder access.
  - [ ] App is deployed to Streamlit Community Cloud and reachable via a public URL
  - [ ] Deployed app matches local behavior (no errors, correct data)
  - Commit:

## In Progress

- **TASK-1: Environment setup and project initialization**
  Set up the project structure, dependencies, and a minimal runnable Streamlit app.
  - [ ] `streamlit run app.py` launches without errors and shows a page title
  - [ ] Dependencies (streamlit, pandas, plotly) are declared and install cleanly
  - Commit:

## Done
