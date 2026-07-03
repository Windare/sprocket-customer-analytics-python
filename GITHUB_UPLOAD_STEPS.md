# GitHub upload steps

From inside the project folder, run:

```bash
git init
git add .
git commit -m "Initial commit: Sprocket Central customer analytics project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/kpmg-sprocket-customer-analysis.git
git push -u origin main
```

Before pushing, check what Git will include:

```bash
git status
```

The raw Excel workbook in `data/raw/` is ignored by default. This is intentional, because datasets may have redistribution restrictions.
