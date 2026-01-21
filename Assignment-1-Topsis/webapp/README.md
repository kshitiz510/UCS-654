---
title: TOPSIS Studio
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.30"
app_file: streamlit_app.py
pinned: false
---

# TOPSIS Studio

A lightweight Streamlit app for running TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) on CSV datasets.

## Quick Start (Local)

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:

   ```bash
   streamlit run streamlit_app.py
   ```

3. Open http://localhost:8501 in your browser

## Features

- 📤 Upload CSV files with criteria data
- ⚖️ Set custom weights and impacts for each criterion
- 📊 View TOPSIS rankings and scores in real-time
- 📥 Download results as CSV
- 🎯 Automatic categorical-to-numeric conversion

## How It Works

1. **Normalization** – Scale criteria to comparable range
2. **Weighted Normalization** – Apply importance weights
3. **Ideal & Anti-Ideal Solutions** – Determine best/worst values
4. **Separation Measures** – Calculate Euclidean distances
5. **TOPSIS Score** – Compute relative closeness (0–1)
6. **Ranking** – Sort alternatives by score

## Input Format

- **First column**: Alternative names/IDs
- **Remaining columns**: Numeric criteria (or categorical - will be auto-converted)
- **Weights**: Comma-separated numbers (one per criterion)
- **Impacts**: '+' for benefit criteria, '-' for cost criteria

Example:

```csv
Model,Price,Storage,Camera,Looks
M1,250,16,12,5
M2,200,16,8,3
M3,300,32,16,4
```

## Deploy to Streamlit Community Cloud

1. **Push to GitHub**:

   ```bash
   git add .
   git commit -m "Add Streamlit TOPSIS webapp"
   git push origin main
   ```

2. **Deploy**:
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub account
   - Select your repository
   - Set **Main file path**: `Assignment-1-Topsis/webapp/streamlit_app.py`
   - Click "Deploy"

3. **Done!** Your app will be live at `https://share.streamlit.io/[username]/[repo]/main`

## Notes

- Higher TOPSIS score (closer to 1) = better alternative
- The app handles non-numeric columns by converting ordinal values (low/medium/high) or using label encoding
- Sample data can be loaded using the checkbox if `test_data.csv` exists in the parent directory

## Course Information

**Course**: UCS654 - Predictive Analytics using Statistics  
**Author**: Kshitiz (Roll No: 102303748)
