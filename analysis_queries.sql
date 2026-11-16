-- Q1: Headline KPIs
SELECT COUNT(*)                                  AS total_adults,
       ROUND(AVG(age), 1)                        AS avg_age,
       ROUND(AVG(bmi), 1)                        AS avg_bmi,
       ROUND(100.0 * SUM(CASE WHEN bmi >= 25 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_overweight_or_obese,
       ROUND(AVG(kcal), 0)                       AS avg_kcal
FROM health_data;

-- Q2: BMI category distribution
SELECT bmi_category,
       COUNT(*) AS people,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM health_data
GROUP BY bmi_category
ORDER BY MIN(bmi);

-- Q3: BMI by age group
SELECT age_group,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi,
       ROUND(100.0 * SUM(CASE WHEN bmi >= 25 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_overweight_or_obese
FROM health_data
GROUP BY age_group
ORDER BY MIN(age);

-- Q4: BMI by gender
SELECT gender,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi,
       ROUND(100.0 * SUM(CASE WHEN bmi >= 25 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_overweight_or_obese
FROM health_data
GROUP BY gender;

-- Q5: Average daily intake by BMI category (day-1 recall)
SELECT bmi_category,
       COUNT(*) AS people,
       ROUND(AVG(kcal), 0)        AS avg_kcal,
       ROUND(AVG(sugar_g), 1)     AS avg_sugar_g,
       ROUND(AVG(fiber_g), 1)     AS avg_fiber_g,
       ROUND(AVG(sodium_mg), 0)   AS avg_sodium_mg,
       ROUND(AVG(protein_g), 1)   AS avg_protein_g
FROM health_data
GROUP BY bmi_category
ORDER BY MIN(bmi);

-- Q6: Calorie group and BMI
SELECT calorie_group,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi,
       ROUND(100.0 * SUM(CASE WHEN bmi >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_obese
FROM health_data
GROUP BY calorie_group
ORDER BY MIN(kcal);

-- Q7: Fiber intake quartiles (per 1000 kcal) and BMI  [uses a window function]
WITH ranked AS (
    SELECT bmi, fiber_per_1000kcal,
           NTILE(4) OVER (ORDER BY fiber_per_1000kcal) AS fiber_quartile
    FROM health_data
)
SELECT fiber_quartile,
       COUNT(*) AS people,
       ROUND(MIN(fiber_per_1000kcal), 1) AS min_fiber_per_1000kcal,
       ROUND(MAX(fiber_per_1000kcal), 1) AS max_fiber_per_1000kcal,
       ROUND(AVG(bmi), 1) AS avg_bmi
FROM ranked
GROUP BY fiber_quartile
ORDER BY fiber_quartile;

-- Q8: Sugar share of calories (quartiles) and BMI
WITH ranked AS (
    SELECT bmi, sugar_pct_kcal,
           NTILE(4) OVER (ORDER BY sugar_pct_kcal) AS sugar_quartile
    FROM health_data
)
SELECT sugar_quartile,
       COUNT(*) AS people,
       ROUND(MIN(sugar_pct_kcal), 1) AS min_sugar_pct,
       ROUND(MAX(sugar_pct_kcal), 1) AS max_sugar_pct,
       ROUND(AVG(bmi), 1) AS avg_bmi
FROM ranked
GROUP BY sugar_quartile
ORDER BY sugar_quartile;

-- Q9: Race / ethnicity and BMI
SELECT race_ethnicity,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi,
       ROUND(100.0 * SUM(CASE WHEN bmi >= 30 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_obese
FROM health_data
GROUP BY race_ethnicity
ORDER BY people DESC;

-- Q10: Household income group and BMI (people with a reported income ratio)
SELECT income_group,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi,
       ROUND(AVG(kcal), 0) AS avg_kcal
FROM health_data
WHERE income_group IS NOT NULL
GROUP BY income_group
ORDER BY MIN(income_poverty_ratio);

-- Q11: On a special diet vs not
SELECT on_special_diet,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi,
       ROUND(AVG(kcal), 0) AS avg_kcal
FROM health_data
WHERE on_special_diet IS NOT NULL
GROUP BY on_special_diet;

-- Q12: Survey-weighted average BMI by gender (weights make results represent the US population)
SELECT gender,
       ROUND(SUM(bmi * diet_weight) / SUM(diet_weight), 1) AS weighted_avg_bmi,
       ROUND(AVG(bmi), 1) AS unweighted_avg_bmi
FROM health_data
GROUP BY gender;

-- Q13: Average BMI by age group and gender
SELECT age_group, gender,
       COUNT(*) AS people,
       ROUND(AVG(bmi), 1) AS avg_bmi
FROM health_data
GROUP BY age_group, gender
ORDER BY MIN(age), gender;
