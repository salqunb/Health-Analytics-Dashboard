# Power BI guide (step by step)

Power BI Desktop runs on Windows only. Use the web version (app.powerbi.com) or a Windows PC if needed.

## 1. Import the data
Get data -> **Text/CSV** -> `data/processed/health_clean.csv` -> **Load**.
(Optional: connect to `data/health.db` through an ODBC SQLite driver to show the SQL step. The CSV gives the same result.)

Check in **Data view** that numeric columns (`bmi`, `kcal`, `diet_weight`, ...) are typed as Decimal Number and text columns as Text.

## 2. Sorting helper columns
Text categories sort alphabetically, which is wrong for some of them. Add these columns (Modeling -> **New column**), then select the text column -> **Column tools -> Sort by column**:

```DAX
bmi_category_order =
SWITCH(health_clean[bmi_category], "Underweight", 1, "Normal", 2, "Overweight", 3, 4)

calorie_group_order =
SWITCH(health_clean[calorie_group], "Under 1500", 1, "1500-1999", 2, "2000-2499", 3, 4)

income_group_order =
SWITCH(LEFT(health_clean[income_group], 3), "Low", 1, "Mid", 2, 3)

education_order =
SWITCH(health_clean[education], "Less than 9th grade", 1, "9th-11th grade", 2,
       "High school / GED", 3, "Some college / AA", 4, 5)
```
`age_group` already sorts correctly (20-29 ... 70+).

## 3. Measures (Modeling -> **New measure**)
```DAX
Adults = COUNTROWS(health_clean)

Avg BMI = AVERAGE(health_clean[bmi])

Avg Age = AVERAGE(health_clean[age])

Avg Calories = AVERAGE(health_clean[kcal])

% Overweight or Obese =
DIVIDE(CALCULATE(COUNTROWS(health_clean), health_clean[bmi] >= 25), COUNTROWS(health_clean))

% Obese =
DIVIDE(CALCULATE(COUNTROWS(health_clean), health_clean[bmi] >= 30), COUNTROWS(health_clean))

Avg Fiber (g) = AVERAGE(health_clean[fiber_g])
Avg Sodium (mg) = AVERAGE(health_clean[sodium_mg])
Avg Sugar (% of kcal) = AVERAGE(health_clean[sugar_pct_kcal])

-- Survey-weighted versions (represent the US adult population)
Weighted Avg BMI =
DIVIDE(SUMX(health_clean, health_clean[bmi] * health_clean[diet_weight]),
       SUM(health_clean[diet_weight]))

Weighted % Overweight or Obese =
DIVIDE(CALCULATE(SUM(health_clean[diet_weight]), health_clean[bmi] >= 25),
       SUM(health_clean[diet_weight]))
```
Format the `%` measures as Percentage. Use the weighted measures for any statement about "US adults"; use the unweighted ones to describe this sample.

## 4. Page 1: Overview
| Visual | Fields |
|---|---|
| 4 **Card** visuals | Adults, Avg BMI, % Overweight or Obese, Avg Calories |
| **Donut** | Legend: `bmi_category`, Values: `Adults` |
| **Column** | X: `age_group`, Y: `Avg BMI` |
| **100% stacked bar** | Axis: `gender`, Legend: `bmi_category`, Values: `Adults` |
| **Slicers** | `gender`, `age_group`, `race_ethnicity` |

## 5. Page 2: Nutrition
| Visual | Fields |
|---|---|
| **Column** | X: `bmi_category`, Y: `Avg Fiber (g)` |
| **Column** | X: `bmi_category`, Y: `Avg Sodium (mg)` |
| **Column** | X: `bmi_category`, Y: `Avg Sugar (% of kcal)` |
| **Column** | X: `calorie_group`, Y: `Avg BMI` |
| **Line / column** | X: a binned `fiber_per_1000kcal` (right-click field -> New group -> Bin, size 5), Y: `Avg BMI` |
| **Slicers** | `gender`, `age_group`, `on_special_diet` |

## 6. Page 3 (optional): Context
`race_ethnicity` and `income_group` against `Avg BMI` and `% Obese`, plus `education`. Add a note on the page: these show associations in a survey sample, not causes.

## 7. Finishing
- Write a one-line takeaway under each page title from your **own** results.
- Use one consistent color per BMI category.
- Save as `dashboard/health_dashboard.pbix` and export screenshots into `dashboard/`.
