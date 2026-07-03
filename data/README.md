# Data Folder

This folder is used to organize the datasets for the project.

The raw data used for this analysis is not included in this public GitHub repository. This is intentional because the original file contains customer-level and transaction-level information from a practice business dataset.

The project was developed using the KPMG/Sprocket Central customer analytics practice dataset, which includes customer demographic information, customer addresses, transaction records, and a new customer list.

## Folder Structure

```text
data/
├── raw/
│   └── .gitkeep
├── processed/
│   └── .gitkeep
└── README.md
```

## Description

* `raw/`: This folder is intended for the original dataset before cleaning.
* `processed/`: This folder is intended for cleaned or transformed datasets created during the analysis.
* `.gitkeep`: This is an empty placeholder file that allows GitHub to display empty folders.

## Why the Data Is Not Included

The raw dataset is excluded from this repository to avoid publishing customer-level data. The analysis results, visualizations, summary tables, and project workflow are included so that the business problem, analytical process, and insights can still be reviewed.

## How to Reproduce the Analysis

To reproduce the analysis locally:

1. Place the original dataset inside the `data/raw/` folder.
2. Open the notebook in the `notebooks/` folder.
3. Run the notebook step by step.
4. Cleaned outputs can be saved into the `data/processed/` folder.

The notebook and source code show the full data cleaning, analysis, and visualization workflow.
