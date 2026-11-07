# Data Files - Not Included in Repository

The following data files are required to run the project but are **NOT included in this repository** due to:
1. File size (35+ MB total)
2. Microburbs proprietary data (hackathon use only)
3. GitHub file size limits

## Required Data Files

Place these files in the `data/` directory:

- `rents-past-leases-city-of-sydney.csv` (17 MB) - Historical rental listings
- `rents-input-flats-city-of-sydney.csv` (12 MB) - Properties requiring predictions
- `blocks-homes-and-people-2021-2026.csv` (135 KB) - Mesh block demographics

## Where to Get the Data

These files were provided by Microburbs for hackathon participants. If you're participating:
1. Check your email from David Bailey (Microburbs)
2. Download from: https://www.microburbs.com.au/p/hackathon-getting-started
3. Extract the zip files to the `data/` directory

## Generated Files (Also Not Included)

After running the training pipeline, these files are generated:

- `saved_models/*.pkl` - Trained models (~60 MB total)
- `saved_models/*.pth` - Neural network weights
- `rents_said.csv` - Final predictions output

## Running Without Data

To run the project:

```bash
# 1. Obtain the data files from Microburbs
# 2. Place them in data/
# 3. Run the training pipeline
python src/pipeline.py --data-path ./data

# 4. Launch the web app
cd src/streamlit_app && streamlit run app.py
```

## Note on Data Privacy

The Microburbs data is proprietary and licensed for hackathon use only. **Do not republish or redistribute** the data files.

---

For questions about data access, contact: microburbs.com.au
