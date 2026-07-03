# Data folder

Place the source Excel workbook in:

```text
data/raw/Mentor_KPMG_Sprocket_Project_Dataset.xlsx
```

This project uses the Sprocket Central practice dataset from a KPMG-style customer analytics exercise. The raw Excel file is included in this local package so the notebook can run immediately, but `.gitignore` is configured to keep Excel files in `data/raw/` out of GitHub by default.

Before making the dataset public, confirm that you are allowed to redistribute it. If not, keep the workbook local and explain in the repository README how another user can obtain or replace the dataset.

Aggregate summary tables are saved in `reports/tables/`. Row-level cleaned outputs are generated locally in `data/processed/` and are ignored by Git by default because they can still contain customer-level records.
