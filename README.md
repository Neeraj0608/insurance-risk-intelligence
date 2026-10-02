# Insurance Risk Intelligence

**RiskIntel** is a macro-prudential intelligence and predictive analytics platform for the insurance sector. Powered by Machine Learning, this system analyzes IRDAI (Insurance Regulatory and Development Authority of India) data to provide actionable forecasting, automated anomaly detection, and explainable AI insights for executives and actuaries.

## 🌟 Key Features

* **🔮 Multi-Horizon Premium Forecasting:** Uses an XGBoost ensemble to predict 6-month rolling forward trends in premium collections, adjusting for market seasonality and macro-economic factors.
* **🚨 Statistical Anomaly Detection:** Automated surveillance system flagging unusual spikes or drops in claim outlays and premium volumes using Z-Score bounds.
* **🧠 Explainable AI (SHAP):** Transparent AI that explains the global and local drivers of every prediction to maintain regulatory auditability.
* **🗺️ Geographic Risk Mapping:** High-fidelity regional concentration heatmap to visualize state-level loss ratios.
* **📊 Executive Dashboard:** A beautiful, responsive glassmorphism UI built with Streamlit for real-time risk monitoring.

## 🏗️ Architecture Stack

* **Frontend:** Streamlit, Plotly (Interactive Maps & Charts)
* **Backend:** FastAPI, Uvicorn
* **Machine Learning:** Scikit-Learn, XGBoost, SHAP
* **Data Processing:** Pandas, NumPy
* **Experiment Tracking:** MLflow

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Neeraj0608/insurance-risk-intelligence.git
cd insurance-risk-intelligence
```

### 2. Environment Setup
Create a virtual environment and install dependencies:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Dataset Download (Required)
This project requires real-world IRDAI data to run accurately. The dataset is intentionally omitted from the repository. 
Please refer to the [data/raw/README.md](data/raw/README.md) file for instructions on downloading the dataset and placing it in the `data/raw/` directory before running the application.

### 4. Running the Application

You need two terminal windows to run both the backend and frontend simultaneously.

**Terminal 1: Start the FastAPI Backend Engine**
```bash
uvicorn api.main:app --reload
```
*Runs on http://localhost:8000*

**Terminal 2: Start the Executive Console (Dashboard)**
```bash
streamlit run dashboard/app.py
```
*Runs on http://localhost:8501*

---
*Disclaimer: This is an analytical tool built for educational and demonstrative purposes based on public IRDAI disclosures.*
