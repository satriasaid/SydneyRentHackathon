# 🎬 Microburbs Hackathon 2026 - Demo Video Script
## Sydney Rent Prediction System
**Team:** Said | **Duration:** 2:30 | **Task:** 4 - Rent Prediction

---

## 📝 SCRIPT

### [0:00-0:15] OPENING - The Problem (15 seconds)

**[SCREEN: Show Excel/data files]**

> "Predicting rental prices is hard. Parking adds $0 to some properties but $200 to others. Traditional models miss this complexity."

**[SCREEN: Transition to project logo/title]**

> "I built a machine learning system that predicts Sydney rents WITH and WITHOUT parking - capturing the context that matters."

---

### [0:15-0:45] THE DATA (30 seconds)

**[SCREEN: Show terminal with data loading]**

> "The system trains on 112,000 historical rental listings from City of Sydney, filtered to July 31st, 2026 as required."

**[SCREEN: Show data exploration output]**

> "95,000 records have known parking status - that's our training set. We also incorporate mesh block demographics: population, housing density, and growth rates from 2021 to 2026."

**[SCREEN: Show feature engineering code snippet]**

> "I engineered 45 features including a key innovation: parking interaction terms. The model learns that parking value scales with property size - studios get $5-15/week, but 3-bedroom apartments in the CBD? $50-150/week."

---

### [0:45-1:15] THE MODELS (30 seconds)

**[SCREEN: Show training pipeline running]**

> "Here's where it gets interesting. I don't train just one model - I train SIX."

**[SCREEN: Show model comparison table appearing]**

> "XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, and a PyTorch Neural Network. All GPU-accelerated, training completes in 3 minutes."

**[SCREEN: Highlight XGBoost winning]**

> "XGBoost wins with a mean absolute error of $111 per week, R-squared of 0.782, and 60% of predictions within $100. That beats the hackathon baseline."

**[SCREEN: Show feature importance graph]**

> "The model reveals something interesting: bathrooms are MORE predictive than bedrooms. Location explains 25% of the variance. And our parking interaction term? Critical for accuracy."

---

### [1:15-1:50] THE APPLICATIONS (35 seconds)

**[SCREEN: Launch Streamlit app]**

> "The system has two interfaces. First, this Streamlit web app."

**[SCREEN: Input property details]**

> "I'll configure a 2-bedroom apartment in Surry Hills, floor 5, 50 flats in the building..."

**[SCREEN: Click Calculate]**

> "And instantly: $875 per week without parking, $905 with parking. A $30 premium for this specific property."

**[SCREEN: Show the chart]**

> "The visualization makes it clear. Different property? Different premium."

**[SCREEN: Switch to FastAPI docs]**

> "Second interface: a REST API with interactive documentation. Perfect for integrating into real estate platforms, Chrome extensions, or mobile apps."

**[SCREEN: Make API request, show JSON response]**

> "POST a property, get predictions in milliseconds."

---

### [1:50-2:15] THE ENGINEERING (25 seconds)

**[SCREEN: Show file structure]**

> "This is production-grade code. Modular architecture: features module, models module, API, and UI - all separate."

**[SCREEN: Show Git LFS]**

> "All six trained models are version-controlled with Git LFS. The 54MB Random Forest? No problem."

**[SCREEN: Show README]**

> "Complete documentation: setup scripts, quick-start guide, training results, deployment summary. Anyone can reproduce this."

**[SCREEN: Show requirements.txt]**

> "One command installs everything. Another command trains all models. Another launches the app."

---

### [2:15-2:30] CLOSING - The Impact (15 seconds)

**[SCREEN: Show predictions CSV file]**

> "The system generated predictions for all 65,777 properties in the required format."

**[SCREEN: Show summary stats]**

> "Average parking premium: $23 per week. But the range? $0 to $1,615. That's the insight - context matters."

**[SCREEN: Show GitHub repo]**

> "Tenants can negotiate better. Landlords can price accurately. Investors can estimate yield."

**[SCREEN: End card with repo link]**

> "Sydney Rent Prediction - six models, two interfaces, production-ready. Code on GitHub. Thank you."

**[FADE OUT]**

---

## 🎯 VISUAL CHECKLIST

### Must Show:
- ✅ Training pipeline running (with time)
- ✅ Model comparison table
- ✅ Streamlit app making a prediction
- ✅ FastAPI docs interface
- ✅ Git LFS for large files
- ✅ Final predictions CSV
- ✅ GitHub repository

### Avoid:
- ❌ Long pauses or silent moments
- ❌ Reading error messages
- ❌ Fumbling with commands
- ❌ Apologizing or explaining problems

---

## 📹 RECORDING TIPS

### Preparation:
1. **Have everything open in tabs:**
   - Terminal (project directory)
   - Streamlit app (running)
   - FastAPI docs (http://localhost:8000/docs)
   - VS Code (showing file structure)
   - GitHub repo page
   - Excel/CSV with results

2. **Terminal commands ready to paste:**
   ```bash
   # Show data loading
   python src/pipeline.py --data-path ./data | head -50
   
   # Show predictions
   head rents_said.csv
   wc -l rents_said.csv
   ```

3. **Record in 1920x1080 minimum**

4. **Test audio levels** - your voice should be clear

### During Recording:
- **Speak confidently** - no filler words ("um", "uh")
- **Use transitions** - "Now let's look at...", "Here's the interesting part..."
- **Keep moving** - don't linger on any screen too long
- **Point with cursor** - highlight what you're talking about

### Editing:
- **Cut dead air** - keep it tight
- **Speed up** slow parts (1.2-1.5x)
- **Add text overlays** for key metrics
- **Background music** - subtle, not distracting

---

## ⏱️ TIMING BREAKDOWN

| Section | Time | Purpose |
|---------|------|---------|
| Problem | 0:15 | Hook the viewer |
| Data | 0:30 | Show depth of work |
| Models | 0:30 | Technical credibility |
| Applications | 0:35 | Demonstrate usability |
| Engineering | 0:25 | Show professionalism |
| Impact | 0:15 | Close with value |
| **TOTAL** | **2:30** | **Under limit** |

---

## 🎤 TONE & STYLE

**Be:** Confident, technical, clear
**Sound like:** An engineer presenting to peers, not selling a product
**Pace:** Quick but not rushed - you have a lot to show
**Energy:** Enthusiastic about the technical work, not hyping

---

## 💡 KEY MESSAGES

1. **"Six models, not one"** - Shows thoroughness
2. **"GPU-accelerated, 3 minutes"** - Shows technical skill
3. **"Parking premium varies 100×"** - Shows insight
4. **"Production-ready code"** - Shows professionalism
5. **"Beats the baseline"** - Shows results

---

## 🏆 WHAT MAKES THIS STRONG

Judges will see:
- ✅ Multiple models compared (most teams: 1-2)
- ✅ Professional UI (most teams: basic Streamlit)
- ✅ REST API (most teams: just notebooks)
- ✅ Complete documentation (most teams: minimal)
- ✅ Git LFS for models (most teams: ignore this)
- ✅ GPU optimization (shows advanced skills)

---

## 📋 PRE-RECORDING CHECKLIST

- [ ] All models trained and saved
- [ ] Streamlit app working on localhost:8501
- [ ] FastAPI running on localhost:8000
- [ ] rents_said.csv exists with 65,777 rows
- [ ] GitHub repo pushed and visible
- [ ] Screen recording software tested
- [ ] Microphone tested
- [ ] Browser tabs prepared
- [ ] Script printed/on second screen
- [ ] Coffee/water ready
- [ ] Phone on silent

---

## 🎬 ALTERNATIVE: SHORTER VERSION (2:00)

If you need to cut 30 seconds:
- Reduce Data section from 30s to 20s (skip mesh block details)
- Reduce Engineering section from 25s to 15s (just show structure, skip Git LFS)
- Keep everything else the same

---

## 🚀 AFTER RECORDING

1. **Export as MP4** (H.264 codec)
2. **Under 95 MB** (compress if needed)
3. **Name:** `sydney_rent_prediction_demo_said.mp4`
4. **Upload to:** Hackathon submission portal
5. **Backup copy** on Google Drive/Dropbox

---

## 💬 OPENING LINES (Choose One)

**Option A (Problem-focused):**
> "Predicting rental prices is hard. Traditional models use fixed parking premiums, but that's wrong. I built a system that learns parking value is contextual."

**Option B (Data-focused):**
> "I trained six machine learning models on 112,000 rental listings to predict Sydney rents. Here's why it beats the baseline."

**Option C (Result-focused):**
> "This system predicts rent for 65,777 properties in under 5 seconds. Mean absolute error: $111 per week. Let me show you how."

**Recommended: Option A** (most engaging hook)

---

## 🎯 CLOSING LINES (Choose One)

**Option A (Impact):**
> "Sydney Rent Prediction. Helping tenants negotiate, landlords price, and investors decide. Code on GitHub. Thank you."

**Option B (Technical):**
> "Six models, 95,000 training records, production-ready code. All on GitHub. Thanks for watching."

**Option C (Results):**
> "Mean absolute error: $111. R-squared: 0.782. 60% within $100. Beats the baseline. Thank you."

**Recommended: Option A** (best for hackathon judges)

---

**Good luck! You've got this! 🚀**
