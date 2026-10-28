# MediGuide Dataset Inventory

| Dataset Name | Source / URL | Format / Path | Primary Purpose | Key Fields | Dynamic / Static |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UCI Heart Disease** | UCI ML Repository | `.data` CSV format <br>`data/raw/uci_heart/` | ML Baseline Model training & rule validation | `age`, `sex`, `cp` (chest pain), `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, `thal`, `num` (target) | Static |
| **Kaggle Disease-Symptom** | Kaggle | CSV <br>`data/raw/kaggle_symptoms/` | Symptom taxonomy & severity weighting | `Disease`, `Symptom_1` to `Symptom_17`, `Symptom`, `weight` | Static |
| **IFCT 2017** | ICMR - NIN India | PDF <br>`data/raw/nutrition/ifct/` | Core Indian cooked & raw food nutritional profile | Food code, Name, Energy (kcal), Protein, Sodium, Saturated Fat, Fiber | Static |
| **USDA FDC** | USDA | JSON/CSV <br>`data/raw/nutrition/usda_fdc/` | Standard ingredient nutrient values | FDC ID, description, nutrients (sodium, fats, fiber, carbs) | Static |
| **Open Food Facts** | Open Food Facts | REST API | On-demand packaged food nutrient lookup & barcode verification | Barcode, product_name, nutriments (salt, sodium, sugars, saturated fat) | Dynamic API |

## 1. UCI Heart Disease
*   **Source:** UCI Machine Learning Repository
*   **Format:** CSV / Data file
*   **Purpose:** Training/testing the baseline ML model; validating concern score rules.
*   **Status:** Downloaded

## 2. Kaggle Disease-Symptom Description
*   **Source:** Kaggle
*   **Format:** CSV
*   **Purpose:** Extracting and standardizing cardiovascular symptom terminology for the questionnaire.
*   **Status:** Downloaded

## 3. Nutritional Databases (IFCT 2017, USDA, Open Food Facts)
*   **Source:** NIN India, USDA, Open Food Facts
*   **Format:** PDF / CSV
*   **Purpose:** Building the core nutritional database for the diet engine's food-query and meal-plan features.
*   **Status:** Downloaded

## Cleaning & Normalization Plan
1. **UCI Heart:** Clean missing values marked as `?` in `ca` and `thal`. Binarize target `num` (0 = no disease, 1-4 = presence of heart disease) for initial baseline, or keep multiclass for severity.
2. **Kaggle Symptoms:** Strip leading/trailing whitespaces, convert underscores to standard lowercase, and map cardiovascular symptoms (`chest_pain`, `breathlessness`, `palpitations`, `dizziness`, etc.) to our symptom dictionary.
3. **IFCT 2017 / USDA:** Extract relevant heart-sensitive fields (Sodium, Saturated Fat, Dietary Fiber, Potassium, Calories) for starter items.
