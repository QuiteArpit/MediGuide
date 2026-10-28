# MediGuide — Project Charter

**Title:** MediGuide: A Modular Symptom-Based Disease Screening and Personalized Diet Recommendation System
**Version:** 0.1 (Phase 1 draft) | **Team size:** 4 | **Status:** For team review

---

## 1. Problem Statement

Many people with possible heart-related symptoms (chest discomfort, breathlessness, palpitations, swelling) do not know how urgent their situation is. Some delay care when they should go to an emergency room; others worry unnecessarily. Separately, people already diagnosed with heart disease often struggle to translate general dietary advice ("eat less salt and fat") into daily food choices, especially with Indian foods and portion sizes, which most diet tools handle poorly.

MediGuide addresses both gaps with a transparent, rule-supported screening tool that suggests *how urgently to seek care*, and a diet guidance module for heart patients that is aware of Indian food habits.

**MediGuide is a screening and education aid. It does not diagnose, treat, or replace a healthcare professional.**

## 2. Objectives

1. Build a symptom questionnaire that captures cardiovascular symptoms and risk factors in 20–25 questions.
2. Produce a **screening concern level** and **care recommendation**: self-monitor, routine checkup, prompt consultation, or emergency care.
3. Explain every recommendation (which answers and rules led to it).
4. Guarantee that red-flag emergency symptoms *always* produce an emergency-care message, regardless of any ML output.
5. Provide personalized diet guidance, food-quantity advice, and food-query answers for users already diagnosed with heart disease.
6. Design the system as modular so other diseases can be added later without rewriting the core.
7. Evaluate the system against a documented set of 30–50 test scenarios.

## 3. MVP Scope and Non-Goals

### In scope (MVP)
- Cardiovascular/heart disease screening only
- Questionnaire input (symptoms + basic health information)
- Hybrid logic: safety rules (red flags) first, then a data-driven risk component
- Four-level care recommendation with a plain-language explanation
- Heart-diet module: sodium, saturated/trans fat, fiber, refined carbs, alcohol, portions, common Indian foods
- Food query answering (e.g., "Can I eat paneer?" "How much rice is okay?")
- Basic web interface, and a dataset/test-scenario foundation for evaluation

### Non-goals
- No diagnosis, no claim of detecting or confirming any disease
- No medication advice, dosing, or changes to prescribed treatment
- No replacement for ECG, blood tests, or clinical examination
- No emergency-service integration or real-time monitoring
- No other diseases in the MVP (architecture only prepares for them)
- No storage of identifiable personal health data beyond what is needed for demo/testing
- No pediatric or pregnancy-specific guidance
- Not a certified medical device

## 4. Target Users

| User group | Need | Primary module |
|---|---|---|
| General adults with possible heart symptoms | Know how urgently to seek care | Screening |
| Adults with cardiovascular risk factors (hypertension, diabetes, smoking, family history) | Understand when to see a doctor | Screening |
| Patients already diagnosed with heart disease | Daily diet guidance and food-query answers | Diet |
| Project evaluators / faculty | See transparent, safe, explainable behavior | Both |

*Secondary stakeholders:* clinicians or dietitians who may be consulted to review rules (recommended).

## 5. System Modules

| # | Module | Responsibility |
|---|---|---|
| M1 | Questionnaire & Input Validation | Collect and validate user answers; consistent coding of responses |
| M2 | Red-Flag Triage Engine | Deterministic rules; emergency overrides everything else |
| M3 | Risk Scoring Model | ML/statistical concern score trained on UCI Heart Disease features, used *after* red-flag check |
| M4 | Recommendation & Explanation Engine | Maps outputs to one of four care levels; generates "why" explanation and disclaimers |
| M5 | Food Knowledge Base | Cleaned nutrition data from IFCT 2017, USDA FDC, Open Food Facts, with Indian food mapping |
| M6 | Heart-Diet Rules Engine | Applies diet rules to foods/portions; answers food queries |
| M7 | User Interface | Questionnaire flow, results page, diet chat/query screen |
| M8 | Evaluation & Safety Testing | Test scenarios, safety checks, metrics, reports |
| M9 | Extensibility Layer | Disease "plug-in" structure (questions, rules, model, diet rules per disease) |

**Core design principle:** safety rules (M2) run before the model (M3), and the model can never downgrade an emergency result.

## 6. Team Roles (4 Members)

*Replace placeholders with names. Everyone reviews each other's work and contributes to the report.*

| Role | Owner | Main responsibilities | Backup |
|---|---|---|---|
| **R1: Project Lead & Safety/Medical Rules** | _Member 1_ | Charter, milestones, triage rules, questionnaire, safety disclaimers, clinician consultation, test scenarios | R4 |
| **R2: Data Engineer** | _Member 2_ | Dataset download/inspection, inventory, cleaning pipelines, food knowledge base (IFCT, USDA, Open Food Facts) | R3 |
| **R3: ML Engineer** | _Member 3_ | Risk model on UCI data, symptom dataset experiments, model evaluation, explainability | R2 |
| **R4: Application & Integration Engineer** | _Member 4_ | Repo setup, CI, backend/UI, recommendation engine integration, diet query module | R1 |

Meetings: one weekly sync (30–45 min), a shared task board (GitHub Projects), and PR review by at least one other member before merging.

## 7. Weekly Milestones

*Assumes a ~16-week plan; adjust dates to your college calendar. Phase 1 = Weeks 1–3.*

| Week | Milestone | Deliverable |
|---|---|---|
| 1 | Foundation | Charter approved, repo created, roles assigned, dataset download started |
| 2 | Data collected | All 5 datasets downloaded and documented, dataset inventory complete |
| 3 | Safety foundation | Questionnaire v1, red-flag triage rules v1, heart-diet rules v1, 30–50 test scenarios (**Phase 1 complete**) |
| 4 | Data cleaning | Cleaned UCI dataset, symptom dataset analysis, food data schema |
| 5 | Baseline model | Baseline heart risk model + metrics |
| 6 | Food knowledge base | Unified food table with Indian food mapping |
| 7 | Triage engine | Rule engine implemented and unit-tested against test scenarios |
| 8 | Recommendation + explanation | End-to-end screening flow (CLI/API) |
| 9 | Clinician/dietitian review | Rules reviewed, feedback incorporated |
| 10 | Diet module | Diet rules engine + food queries working |
| 11 | UI v1 | Web interface for screening and diet |
| 12 | Integration | Full system integration, bug fixing |
| 13 | Evaluation | Full test-scenario run, safety audit, metrics report |
| 14 | Extensibility demo | Second disease stub added to prove modular design |
| 15 | Documentation | Final report, user guide, limitations section |
| 16 | Demo & submission | Presentation, demo video, final repo release |

## 8. Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | System seen as giving a diagnosis | Medium | High | Fixed approved wording; disclaimer on every result; wording tests in test suite |
| 2 | Missed emergency (false negative) | Low–Med | Critical | Deterministic red-flag rules before ML; emergency test scenarios must pass 100%; err toward higher urgency |
| 3 | UCI dataset is small, old, and not symptom-questionnaire shaped | High | Medium | Use as one component only; document limitations; rely on rule-based triage for safety |
| 4 | Kaggle symptom dataset is synthetic/unrealistic | High | Medium | Treat as exploratory only; do not use as clinical evidence; state this in the report |
| 5 | Dataset licenses restrict use (IFCT PDF, Open Food Facts ODbL, Kaggle terms) | Medium | Medium | Record license per dataset in inventory; attribute properly; verify before redistributing data |
| 6 | IFCT is a PDF — table extraction is error-prone | High | Medium | Manual spot-checks; extract only needed foods first; log data-quality issues |
| 7 | No medical expertise on team | High | High | Base rules on published guidelines; seek review from a doctor/dietitian; label rules "v1 — pending review" |
| 8 | Unsafe or inappropriate diet advice (e.g., for kidney disease, diabetes, medication interactions) | Medium | High | Keep advice general; add "follow your doctor's/dietitian's plan"; no medication advice |
| 9 | Privacy of health data | Medium | Medium | No real patient data collection; synthetic/anonymous inputs for testing; no accounts in MVP |
| 10 | Team bottlenecks / uneven workload | Medium | Medium | Weekly sync, task board, backup owners, PR reviews |
| 11 | Scope creep into other diseases | Medium | Medium | Strict MVP boundary; extensibility only through architecture, not features |
| 12 | Time pressure with exams/placements | High | Medium | Buffer in Weeks 14–16; prioritize must-haves (triage + explanation) over nice-to-haves |

## 9. Success Criteria

**Safety (must-have)**
- 100% of clear emergency scenarios produce emergency-care advice
- No output ever states or implies a confirmed diagnosis
- Every result shows a disclaimer and "consult a healthcare professional"

**Functionality**
- Questionnaire (20–25 questions) completes in under ~5 minutes
- System returns one of the four care levels with a readable explanation for every case
- Diet module gives guidance for the defined rule categories and answers common Indian food queries

**Quality**
- ≥ 90% agreement between system output and expected care level on the test scenarios (target; emergencies 100%)
- Risk model results documented with appropriate metrics (e.g., recall/sensitivity emphasized) and limitations stated
- All datasets documented in the inventory with source, license, and cleaning notes

**Engineering and documentation**
- Reproducible repo (README setup steps, tests passing)
- Modular design demonstrated by adding a stub for a second disease
- Final report, demo, and Phase deliverables completed on schedule

## 10. Safety Disclaimers

**Standard disclaimer (show on every result screen):**
> MediGuide is an educational screening tool. It cannot diagnose any disease. The result shows a *screening concern level* based on the information you entered and is not a medical opinion. Please consult a healthcare professional for evaluation and advice.

**Emergency message (always shown for red-flag symptoms):**
> Your answers include symptoms that may need urgent medical attention. Seek emergency care now. Call your local emergency number (in India: 112 or 108) or go to the nearest hospital. Do not wait for further online guidance, and do not drive yourself if you feel unwell.

**Diet disclaimer:**
> Dietary suggestions are general guidance for people with heart conditions. They do not replace the plan from your doctor or dietitian. Do not change or stop prescribed medicines because of this tool. If you have other conditions (kidney disease, diabetes, etc.) or take blood thinners, ask your healthcare provider about your diet.

**Language rules for all outputs:**
- Use: "possible condition," "screening concern," "may suggest," "consult a healthcare professional"
- Avoid: "you have," "you are diagnosed with," "this confirms," "you do not have," "you are safe"
- A low concern result must never say "no risk"; use "low screening concern based on your answers; seek care if symptoms change or worsen."
- Emergency rules override all other logic.

---

*Approval:* ☐ Member 1 ☐ Member 2 ☐ Member 3 ☐ Member 4 ☐ Faculty guide (optional)
