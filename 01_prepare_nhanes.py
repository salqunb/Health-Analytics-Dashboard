"""
Step 1: read the NHANES 2021-2023 SAS transport (.xpt) files, merge them on SEQN,
clean them, and write one tidy CSV for SQL and Power BI.

Files used (data/raw/):
  DEMO_L    demographics (age, gender, race/ethnicity, education, income ratio, survey design)
  BMX_L     body measures (weight, height, BMI, waist)
  DR1TOT_L  dietary recall, day 1 totals (calories, nutrients, water)
  DBQ_L     diet behavior questionnaire - loaded and checked, but not merged (see README)
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "health_clean.csv"


def read_xpt(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_sas(RAW / f"{name}.xpt", format="xport", encoding="utf-8")
    df["SEQN"] = df["SEQN"].astype(int)
    return df if columns is None else df[["SEQN"] + columns]


# 1) Load only the columns we need
demo = read_xpt("DEMO_L", ["RIAGENDR", "RIDAGEYR", "RIDRETH3", "DMDEDUC2", "INDFMPIR",
                           "WTMEC2YR", "SDMVSTRA", "SDMVPSU"])
bmx = read_xpt("BMX_L", ["BMXWT", "BMXHT", "BMXBMI", "BMXWAIST"])
diet = read_xpt("DR1TOT_L", ["WTDRD1", "DR1DRSTZ", "DRQSDIET", "DR1TNUMF", "DR1TKCAL",
                             "DR1TPROT", "DR1TCARB", "DR1TSUGR", "DR1TFIBE", "DR1TTFAT",
                             "DR1TSFAT", "DR1TCHOL", "DR1TSODI", "DR1TPOTA", "DR1TCAFF",
                             "DR1TALCO", "DR1_320Z"])
dbq = read_xpt("DBQ_L")
print(f"DEMO_L {len(demo)} | BMX_L {len(bmx)} | DR1TOT_L {len(diet)} | DBQ_L {len(dbq)} rows")

# 2) Merge: keep people who have demographics + body measures + a dietary recall
df = demo.merge(bmx, on="SEQN", how="inner").merge(diet, on="SEQN", how="inner")
print(f"After merging DEMO + BMX + DR1TOT: {len(df)} people")

# 3) Filters (each one printed so the README can document them)
n = len(df)
df = df[df["RIDAGEYR"] >= 20]
print(f"Adults (age 20+): {len(df)} (dropped {n - len(df)})"); n = len(df)
df = df[df["BMXBMI"].notna()]
print(f"With a measured BMI: {len(df)} (dropped {n - len(df)})"); n = len(df)
df = df[df["DR1DRSTZ"] == 1]  # 1 = reliable recall that met minimum criteria
print(f"With a reliable day-1 dietary recall: {len(df)} (dropped {n - len(df)})"); n = len(df)
# Remove implausible one-day energy intakes (a common NHANES rule of thumb: 500-5000 kcal)
df = df[df["DR1TKCAL"].between(500, 5000)].reset_index(drop=True)
print(f"With plausible calories (500-5000 kcal): {len(df)} (dropped {n - len(df)})")

# 4) Rename to friendly names
df = df.rename(columns={
    "SEQN": "person_id", "RIDAGEYR": "age", "BMXWT": "weight_kg", "BMXHT": "height_cm",
    "BMXBMI": "bmi", "BMXWAIST": "waist_cm", "INDFMPIR": "income_poverty_ratio",
    "DR1TNUMF": "foods_reported", "DR1TKCAL": "kcal", "DR1TPROT": "protein_g",
    "DR1TCARB": "carbs_g", "DR1TSUGR": "sugar_g", "DR1TFIBE": "fiber_g", "DR1TTFAT": "fat_g",
    "DR1TSFAT": "sat_fat_g", "DR1TCHOL": "cholesterol_mg", "DR1TSODI": "sodium_mg",
    "DR1TPOTA": "potassium_mg", "DR1TCAFF": "caffeine_mg", "DR1TALCO": "alcohol_g",
    "DR1_320Z": "plain_water_g", "WTDRD1": "diet_weight", "WTMEC2YR": "exam_weight",
    "SDMVSTRA": "strata", "SDMVPSU": "psu",
})

# 5) Decode categories (codes from the NHANES 2021-2023 documentation)
df["gender"] = df["RIAGENDR"].map({1: "Male", 2: "Female"})
df["race_ethnicity"] = df["RIDRETH3"].map({
    1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
    4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other / Multiracial"})
df["education"] = df["DMDEDUC2"].map({
    1: "Less than 9th grade", 2: "9th-11th grade", 3: "High school / GED",
    4: "Some college / AA", 5: "College graduate or above"})  # 7 and 9 (refused / don't know) -> missing
df["on_special_diet"] = df["DRQSDIET"].map({1: "Yes", 2: "No"})
df = df.drop(columns=["RIAGENDR", "RIDRETH3", "DMDEDUC2", "DRQSDIET", "DR1DRSTZ"])

# 6) Derived columns
df["bmi_category"] = pd.cut(df["bmi"], bins=[0, 18.5, 25, 30, 1000], right=False,
                            labels=["Underweight", "Normal", "Overweight", "Obese"]).astype(str)
df["age_group"] = pd.cut(df["age"], bins=[19, 29, 39, 49, 59, 69, 120],
                         labels=["20-29", "30-39", "40-49", "50-59", "60-69", "70+"]).astype(str)
df["calorie_group"] = pd.cut(df["kcal"], bins=[0, 1500, 2000, 2500, 1e6], right=False,
                             labels=["Under 1500", "1500-1999", "2000-2499", "2500+"]).astype(str)
df["income_group"] = pd.cut(df["income_poverty_ratio"], bins=[-1, 1.3, 3.5, 100],
                            labels=["Low (ratio up to 1.3)", "Middle (1.3-3.5)", "Higher (above 3.5)"]).astype(str)
df["income_group"] = df["income_group"].replace("nan", np.nan)
# share of calories from each macronutrient (protein and carbs 4 kcal/g, fat 9 kcal/g)
df["protein_pct_kcal"] = (df["protein_g"] * 4 / df["kcal"] * 100).round(1)
df["carbs_pct_kcal"] = (df["carbs_g"] * 4 / df["kcal"] * 100).round(1)
df["fat_pct_kcal"] = (df["fat_g"] * 9 / df["kcal"] * 100).round(1)
df["sugar_pct_kcal"] = (df["sugar_g"] * 4 / df["kcal"] * 100).round(1)
df["fiber_per_1000kcal"] = (df["fiber_g"] / df["kcal"] * 1000).round(1)
df["age"] = df["age"].astype(int)
df["plain_water_l"] = (df["plain_water_g"] / 1000).round(2)  # 1 g of water ~ 1 mL
df = df.drop(columns=["plain_water_g"])

# 7) Quality checks and save
cols = ["person_id", "age", "age_group", "gender", "race_ethnicity", "education", "income_poverty_ratio",
        "income_group", "weight_kg", "height_cm", "bmi", "bmi_category", "waist_cm", "kcal", "calorie_group",
        "protein_g", "carbs_g", "sugar_g", "fiber_g", "fat_g", "sat_fat_g", "cholesterol_mg", "sodium_mg",
        "potassium_mg", "caffeine_mg", "alcohol_g", "plain_water_l", "foods_reported", "on_special_diet",
        "protein_pct_kcal", "carbs_pct_kcal", "fat_pct_kcal", "sugar_pct_kcal", "fiber_per_1000kcal",
        "diet_weight", "exam_weight", "strata", "psu"]
df = df[cols]
missing = df.isna().sum()
print("\nColumns with missing values (kept as blank, not filled in):")
print(missing[missing > 0].to_string() if missing.sum() else "none")
print("\nBMI summary (unweighted):")
print(df["bmi"].describe().round(1).to_string())
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"\nSaved {len(df)} rows x {df.shape[1]} columns to {OUT}")
