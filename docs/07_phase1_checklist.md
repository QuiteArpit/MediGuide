# Phase 1 Completion Checklist

Tick each item only when the *check* is true. Review it together at the end of week 3.

## 1.1 Project Charter
- [ ] All ten charter sections are complete (`docs/01_project_charter.md`)
- [ ] Each member has a named role and a backup
- [ ] Every member has read and approved the charter
- [ ] Safety disclaimers and language rules are agreed

## 1.2 Repository
- [ ] GitHub repository created, all 4 members have access
- [ ] Folders exist: `docs/`, `data/raw/`, `data/processed/`, `notebooks/`, `src/`, `tests/`, `reports/`
- [ ] `README.md`, `.gitignore`, `requirements.txt` committed
- [ ] Branch + Pull Request rule agreed
- [ ] Check: can a new member clone, install and understand where things go?

## 1.3 Datasets downloaded and documented
- [ ] UCI Heart Disease in `data/raw/uci_heart/`
- [ ] IFCT 2017 PDF in `data/raw/ifct/`
- [ ] USDA FoodData Central CSVs in `data/raw/usda_fdc/`
- [ ] Kaggle symptom files in `data/raw/kaggle_symptoms/`
- [ ] Open Food Facts India subset in `data/raw/open_food_facts/`
- [ ] Checksums recorded; raw files untouched
- [ ] `docs/03_dataset_inventory.xlsx` updated with real record counts and licenses (no "VERIFY" left)
- [ ] Check: for every dataset, we can state why it is needed and which fields will be used

## 1.4 Data inspection
- [ ] `notebooks/01_data_inspection.ipynb` runs end to end
- [ ] Per dataset: rows/columns, column meanings, missing values, duplicates, target, data types, class balance
- [ ] One-page summary per dataset (5 in total)

## 1.5 Questionnaire
- [ ] `docs/04_symptom_questionnaire.xlsx`: 25 questions, red flags separated (Section A)
- [ ] 3-5 non-medical volunteers answered it with no help; confusing items rewritten

## 1.6 Red-flag rules
- [ ] `docs/05_red_flag_rules.xlsx` reviewed by the whole team
- [ ] Every emergency scenario leads to emergency advice even if other answers are normal
- [ ] Sources checked against the real documents (`source_verified?` updated)
- [ ] Doctor or clinician review requested (date: ______)

## 1.7 Heart-diet rules
- [ ] `docs/06_heart_diet_rules.xlsx`: every rule has condition, recommendation, limit (if applicable) and source
- [ ] All "team proposal, pending review" limits listed for a dietitian/doctor
- [ ] Dietitian/clinician review requested (date: ______)

## 1.8 Test scenarios
- [ ] `reports/phase1_test_scenarios.xlsx`: at least 10 per category (56 now)
- [ ] Emergency cases clearly separated from routine consultation cases
- [ ] Expected levels match the current rule sheet

## Safety sign-off
- [ ] No document says the system diagnoses disease
- [ ] All result text uses "possible condition", "screening concern", "consult a healthcare professional"
- [ ] Emergency symptoms always trigger emergency-care advice (rule GR-001)

## Phase 1 is complete when
All boxes above are ticked, files are merged into `main`, and the team lead has recorded the date: ______
