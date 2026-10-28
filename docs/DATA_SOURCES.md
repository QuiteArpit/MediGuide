# Raw Data: Sources and Download Steps

Rules: files here are **original and read-only**. Never edit them. Cleaned versions go to `data/processed/`.
Do not commit very large files. Add them to `.gitignore` and keep this document plus checksums instead.

After every download, run (from repo root):

```bash
# Linux / macOS / Git Bash
sha256sum data/raw/<folder>/* >> data/raw/CHECKSUMS.txt
# Windows PowerShell:  Get-FileHash data\raw\<folder>\* -Algorithm SHA256
```

## DS-01 UCI Heart Disease -> `data/raw/uci_heart/`

```bash
mkdir -p data/raw/uci_heart && cd data/raw/uci_heart
curl -L -o heart_disease.zip https://archive.ics.uci.edu/static/public/45/heart+disease.zip
unzip heart_disease.zip
```
Alternative: use the "Download" button on https://archive.ics.uci.edu/dataset/45/heart+disease.
Keep the four `processed.*.data` files and `heart-disease.names`.

## DS-02 IFCT 2017 -> `data/raw/ifct/`

```bash
mkdir -p data/raw/ifct && cd data/raw/ifct
curl -L -o IFCT2017.pdf https://www.nin.res.in/ebooks/IFCT2017.pdf
```
If the download is blocked, open the link in a browser and save the PDF into this folder. Read the copyright/terms page in the PDF and copy it into the inventory.

## DS-03 USDA FoodData Central -> `data/raw/usda_fdc/`

1. Open https://fdc.nal.usda.gov/download-datasets (the "Download Data" section of the site).
2. Download the **CSV** versions of **Foundation Foods** and **SR Legacy** (add FNDDS only if needed).
3. Unzip each into its own subfolder, e.g. `data/raw/usda_fdc/sr_legacy/`.
4. Record the release date shown on the page in the inventory.

## DS-04 Kaggle Disease Symptom Prediction -> `data/raw/kaggle_symptoms/`

Requires a free Kaggle account.

```bash
pip install kaggle
# Put your kaggle.json API token in ~/.kaggle/ (Kaggle > Settings > API > Create New Token)
kaggle datasets download -d itachi9604/disease-symptom-description-dataset -p data/raw/kaggle_symptoms --unzip
```
Or download manually from https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset and unzip into the folder.
Expected files: `dataset.csv`, `Symptom-severity.csv`, `symptom_Description.csv`, `symptom_precaution.csv`.

## DS-05 Open Food Facts -> `data/raw/open_food_facts/`

**Do not download the full dump** (it is many GB). Take an India subset instead:

- Go to https://world.openfoodfacts.org/data and read the data terms.
- Option A: download the CSV/Parquet export once, then filter to `countries_tags` containing `en:india` and save only that subset as `off_india_subset.csv`.
- Option B: use the search API with the country filter for India and save results to the same file.

Record the extraction date and filter used in the inventory, since this database changes daily.

## After downloading

- [ ] Update "Download status" and record counts in `docs/03_dataset_inventory.xlsx`
- [ ] Add the licence text or link for each dataset
- [ ] Commit this file and the checksums (not large raw files)
