# Aadhaar Friction Index (AFI)

<p align="center">
  <img src="https://img.shields.io/badge/Hackathon-UIDAI%20Hackathon-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Python-Data%20Analysis-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

## Overview

The **Aadhaar Friction Index (AFI)** quantifies and visualizes friction points in India's Aadhaar authentication system through data-driven analysis. It combines statistical analysis, interactive visualizations, and actionable insights to identify where the digital identity system creates barriers for citizens.

**Key Capabilities:**
- Quantitative friction measurement across states and districts
- Root cause analysis through signal decomposition
- Interactive dashboards for real-time monitoring
- Exportable reports and trend analysis

## Key Features

- **Friction Index Calculation** - 4 weighted signal components on 0-100 scale
- **Advanced Analytics** - Demographic, geographic, and temporal analysis
- **Interactive Visualizations** - 8 specialized dashboard pages with drill-down capabilities
- **Multiple Output Formats** - Jupyter notebooks, Streamlit app, CSV/Excel/Parquet/SQLite
- **Production-Ready** - Data caching, error handling, automated reports

## Project Structure

```
AADHAAR-FRICTION-INDEX/
├── datasets/
│   ├── raw/                    # Raw Aadhaar API data
│   ├── processed/              # Cleaned data
│   └── index/                  # AFI outputs
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_friction_signal.ipynb
│   ├── 03_aadhaar_friction_index_construction.ipynb
│   └── 04_visualization.ipynb
├── outputs/
│   ├── plots/                  # PNG and HTML visualizations
│   └── tables/                 # CSV, Excel, Parquet, SQLite
├── src/
│   ├── preprocessing.py
│   ├── signal.py
│   ├── index.py
│   └── utils.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

## Installation

```bash
# Clone repository
git clone https://github.com/Yogiii13/Aadhaar-Friction-Index-.git
cd Aadhaar-Friction-Index-

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Requirements:** Python 3.8+, 4GB RAM, 500MB disk space

## Usage

### Option A: Jupyter Notebooks

```bash
# Launch Jupyter
jupyter notebook

# Run notebooks in sequence:
# 1. 01_exploration.ipynb - Data exploration & cleaning
# 2. 02_friction_signal.ipynb - Signal engineering
# 3. 03_aadhaar_friction_index_construction.ipynb - AFI calculation
# 4. 04_visualization.ipynb - Generate all visualizations
```

### Option B: Streamlit Dashboard

```bash
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

**Dashboard Pages:**
- 📈 Dashboard Overview - Executive summary
- 🔥 High-Risk Districts - Intervention targets
- ⚙️ Friction Signal Analysis - Root causes
- ⚠️ Hidden Risk Detection - Overlooked problems
- 📋 State Comparison - Regional analysis
- 📅 Trends & Timeline - Progress tracking
- 📊 Detailed Tables - Deep data exploration
- ℹ️ About & Methodology - Documentation

## Key Metrics

### AFI (Aadhaar Friction Index)

**Formula:**
```
AFI = (0.30 × UIS) + (0.25 × RIS) + (0.25 × BSS) + (0.20 × TSD)
Normalized to 0-100 scale
```

**Classification:**
- 🟢 Low Friction: 0-40
- 🟡 Medium Friction: 40-70
- 🔴 High Friction: 70-100

### Component Signals

| Signal | Weight | Meaning |
|--------|--------|---------|
| UIS | 30% | Update Intensity - Frequency of user updates |
| RIS | 25% | Repeat Interaction - Problems in resolution process |
| BSS | 25% | Biometric Stress - Authentication failures |
| TSD | 20% | Temporal Deviation - Time-based variations |

## Data Sources

**Source:** UIDAI Public API (aggregate statistics, no PII)  
**Coverage:** 28 states + 8 union territories, 700+ districts  
**Time Period:** 2025-01 onwards (monthly updates)

**Three Primary Datasets:**
1. Biometric Updates - Fingerprint/iris authentication data
2. Demographic Updates - Address, name, DOB changes
3. Enrolment Data - New registrations and demographics

## Output Files

**Visualizations:**
- Static charts (PNG, 300 DPI)
- Interactive charts (HTML, Plotly)
- Streamlit dashboard

**Tables:**
- `afi_summary_by_district.csv` - District rankings
- `afi_summary_by_state.csv` - State comparisons
- `friction_signal_summary.csv` - Signal breakdown
- `hidden_risk_table.csv` - Risk detection
- `monthly_afi_trends.csv` - Time series
- Excel, Parquet, and SQLite formats available

## Deployment

```bash
# Local
streamlit run streamlit_app.py

# Streamlit Cloud
# Push to GitHub, connect at https://streamlit.io/cloud

# Docker
docker build -t afi-dashboard .
docker run -p 8501:8501 afi-dashboard
```

## Customization

**Modify friction thresholds** in `streamlit_app.py`:
```python
def classify_friction(afi):
    if afi >= 70: return "🔴 High Friction"
    elif afi >= 40: return "🟡 Medium Friction"
    else: return "🟢 Low Friction"
```

**Change AFI weights** in `src/index.py`:
```python
weights = {'UIS': 0.30, 'RIS': 0.25, 'BSS': 0.25, 'TSD': 0.20}
```

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make changes following PEP 8
4. Submit a pull request

**Priority areas:** Additional signals, predictive modeling, performance optimization, multi-language support

## Use Cases

### For Government Agencies
- Identify districts needing support
- Allocate resources efficiently
- Monitor system performance
- Track improvement initiatives

### For Researchers
- Study digital identity barriers
- Analyze demographic disparities
- Predict failure patterns
- Benchmark system performance

### For Policy Makers
- Evidence-based decision making
- Regional prioritization
- Budget allocation justification
- Progress monitoring

### For Citizens
- Understand where problems occur
- Advocate for improvements
- Participate in feedback
- Track system evolution

## Project Statistics

| Metric | Value |
|--------|-------|
| Lines of Code | 3000+ |
| Notebooks | 4 |
| Dashboard Pages | 8 |
| Visualizations | 15+ |
| CSV Tables | 8 |
| Data Points | 500,000+ |
| States Covered | 28 + 8 UT |
| Districts Covered | 700+ |
| Time Series Months | 12+ |

## Acknowledgments

### Contributors & Support
- **UIDAI** - Public API access
- **Data Contributors** - Providing anonymized datasets
- **Community Members** - Feedback and suggestions
- **Open Source Community** - Libraries and tools

### Libraries Used
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations
- **Streamlit** - Web framework
- **Matplotlib/Seaborn** - Static charts
- **Jupyter** - Interactive notebooks
- **NumPy** - Numerical computing

## Contact

- 👤 **Project Lead:** [@Yogiii13](https://github.com/Yogiii13)
- 👤 **Contributor:** [@Sojwal27](https://github.com/sojwal27)
- 📧 **Email:** yogeshyadav14434@gmail.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/Yogiii13/Aadhaar-Friction-Index-/issues)

## License

MIT License - see [LICENSE](LICENSE) file

---

**Made with ❤️ for a more transparent and accessible digital India**

⭐ Star this repository | 💬 Share feedback | 🐛 Report bugs | 🎁 Contribute
