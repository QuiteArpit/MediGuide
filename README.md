# MediGuide

**A Modular Symptom-Based Disease Screening and Personalized Diet Recommendation System**
Final Year Project | Team of 4 | Status: Phase 1 (foundation and data collection)

> **MediGuide is an educational screening tool. It does not diagnose any disease and is not a substitute for a healthcare professional.** Results show a *screening concern level* only. If you have chest pain, trouble breathing, fainting, or other emergency symptoms, call your local emergency number (India: 112 / 108) or go to the nearest hospital.

## What it does (MVP: cardiovascular)

1. **Screening:** the user answers a 25-question symptom and risk questionnaire. The system returns one of four care recommendations: *self-monitor*, *routine checkup*, *prompt consultation*, or *emergency care*, and explains why.
2. **Diet guidance:** for users already diagnosed with heart disease, it gives general dietary guidance, food-quantity advice and answers to food queries, with common Indian foods.
3. **Modular design:** disease modules (questions, rules, model, diet rules) are separate so other diseases can be added later.

**Safety design:** deterministic red-flag rules run first. The ML model can only add nuance and can never lower an emergency result.

## Repository structure

```
MediGuide/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/        project documents (charter, rules, questionnaire, inventory)
├── data/
│   ├── raw/         original downloaded datasets (read-only)
│   └── processed/   cleaned and merged data
├── notebooks/   exploration and inspection notebooks
├── src/         reusable code (data, triage, models, diet, app)
├── tests/       automated tests
└── reports/     results, figures, test scenarios
```

See `docs/02_repo_structure.md` for what belongs in each folder and why.

## Phase 1 deliverables

| # | File | Status |
|---|---|---|
| 1 | `docs/01_project_charter.md` | Draft |
| 2 | `docs/02_repo_structure.md` | Draft |
| 3 | `docs/03_dataset_inventory.xlsx`, `data/raw/DATA_SOURCES.md` | Draft (counts to verify after download) |
| 4 | `notebooks/01_data_inspection.ipynb` | To do |
| 5 | `docs/04_symptom_questionnaire.xlsx` | Draft |
| 6 | `docs/05_red_flag_rules.xlsx` | Draft (needs clinician review) |
| 7 | `docs/06_heart_diet_rules.xlsx` | Draft (needs clinician/dietitian review) |
| 8 | `reports/phase1_test_scenarios.xlsx` | Draft |
| 9 | `docs/07_phase1_checklist.md` | Draft |

## Getting started

```bash
git clone <your-repo-url> && cd MediGuide
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Download the datasets by following `data/raw/DATA_SOURCES.md`.

## Language rules for all outputs

Use "possible condition", "screening concern", "may suggest", "consult a healthcare professional". Never write "you have", "diagnosis", "you are safe" or "no risk".

## Team

| Role | Member |
|---|---|
| Project Lead & Safety/Medical Rules | _TBD_ |
| Data Engineer | _TBD_ |
| ML Engineer | _TBD_ |
| Application & Integration Engineer | _TBD_ |

## Data sources and licenses

UCI Heart Disease, IFCT 2017, USDA FoodData Central, Kaggle Disease Symptom Prediction, Open Food Facts. Licenses and terms are recorded in `docs/03_dataset_inventory.xlsx`. Please cite the sources if you reuse this work.
