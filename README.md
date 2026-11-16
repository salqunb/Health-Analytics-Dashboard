# Health Analytics Dashboard

An end-to-end analytics project on **BMI, age, and dietary intake** of US adults, built from the CDC's NHANES 2021-2023 survey.

**Stack:** Python (pandas) -> SQL (SQLite) -> Power BI

## Data
[NHANES 2021-2023](https://wwwn.cdc.gov/nchs/nhanes/) (National Health and Nutrition Examination Survey, CDC/NCHS). Public US government data.

| File | Content | Rows |
|---|---|---|
| `DEMO_L` | Demographics, survey weights | 11,933 |
| `BMX_L` | Body measures (weight, height, BMI, waist) | 8,860 |
| `DR1TOT_L` | Day-1 24-hour dietary recall, nutrient totals | 8,860 |
| `DBQ_L` | Diet behavior questionnaire | 11,933 |

`DBQ_L` is read (its row count is checked) but **not merged**: in this cycle it covers infant feeding, school meals, and meal-planning roles rather than adult eating habits, so dietary habits come from the dietary recall (`DR1TOT_L`).

## Project structure
```
data/raw/                       # the four .xpt files from CDC
data/processed/health_clean.csv # output of step 1, used by Power BI
src/01_prepare_nhanes.py        # read, merge, filter, clean, derive columns
src/02_load_to_sqlite.py        # load into SQLite (data/health.db)
src/03_run_queries.py           # run sql/analysis_queries.sql
sql/analysis_queries.sql        # 13 analysis queries
docs/powerbi_guide.md           # dashboard steps + DAX measures
dashboard/index.html              # interactive web dashboard (open in a browser)
dashboard/                      # .pbix and screenshots
```

## How to run
```bash
pip install -r requirements.txt
python src/01_prepare_nhanes.py
python src/02_load_to_sqlite.py
python src/03_run_queries.py
```
Then follow `docs/powerbi_guide.md`.

## Cleaning steps and sample size
1. Merge DEMO + BMX + DR1TOT on `SEQN`: **8,860** people
2. Keep adults (age 20+): **6,064**
3. Keep people with a measured BMI: **5,970**
4. Keep reliable day-1 dietary recalls (recall status = 1): **4,748**
5. Remove implausible energy intake (outside 500-5,000 kcal): **4,635** final adults

New columns: `bmi_category` (WHO adult cutoffs), `age_group`, `calorie_group`, `income_group` (from the income-to-poverty ratio), macronutrient shares of calories, `fiber_per_1000kcal`, and `plain_water_l`. Missing values are left blank, not imputed.

## Dashboard
An interactive web dashboard is in `dashboard/index.html` (open it in any browser; it works on GitHub Pages too). It shows the real NHANES results with a gender filter.

_Add screenshots here (and of your Power BI version):_ `![Overview](dashboard/overview.png)`

## Key findings
_Write 3-5 bullets from your own query results and dashboard, with numbers. Prefer the survey-weighted measures for statements about US adults._

## Limitations
- Dietary intake is a **single 24-hour recall**, which is self-reported and does not represent usual intake.
- Results are **associations**, not causes. For example, people who are heavier may also be more likely to change how they eat or to be on a special diet.
- The unweighted sample skews older than the US adult population. Use `diet_weight` (see Q12 and the DAX measures) for population-level statements; unweighted numbers describe the sample only.
- BMI is a screening measure and does not distinguish muscle from fat.
- This project does not account for the full NHANES complex survey design (strata/PSU), so no confidence intervals are reported.

## Possible next steps
- Add a Jupyter notebook with exploratory charts.
- Use the second dietary day (`DR2TOT`) to average two recalls.
- Model BMI or obesity from diet and demographics with survey weights.
