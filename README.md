# Aadhaar Friction Index

A data-driven analysis tool that quantifies and visualizes the friction points in India's Aadhaar authentication system. This project analyzes demographic patterns, failure rates, and system inefficiencies to identify where the digital identity system creates barriers for citizens.

## Overview

The Aadhaar Friction Index project provides comprehensive analysis of authentication failures, demographic disparities, and system performance issues in India's Aadhaar digital identity infrastructure. Through statistical analysis and interactive visualizations, it reveals critical insights about accessibility challenges faced by different population segments.

## Key Features

- **Friction Index Calculation**: Quantitative measure combining failure rates, demographic impact, and system inefficiencies
- **Demographic Analysis**: Age and gender-based breakdown of authentication challenges
- **State-wise Comparisons**: Geographic analysis of Aadhaar system performance
- **Trend Visualization**: Time-series analysis of authentication patterns
- **Interactive Dashboards**: Explore data through dynamic charts and graphs
- **Statistical Modeling**: Correlation analysis and predictive insights

## Project Structure

```text
AADHAAR-FRICTION-INDEX/
│
├── datasets/                           # Data layers
│   ├── raw/                            # Raw Aadhaar API data
│   │   ├── api_data_aadhaar_biometric_*.csv
│   │   ├── api_data_aadhaar_demographic_*.csv
│   │   └── api_data_aadhaar_enrolment_*.csv
│   │
│   ├── processed/                      # Cleaned datasets
│   │   ├── biometric_updates_cleaned.csv
│   │   ├── demographic_updates_cleaned.csv
│   │   └── enrolment_cleaned.csv
│   │
│   └── index/                          # AFI core outputs
│       ├── aadhaar_friction_index.csv
│       └── aadhaar_friction_index_ranked.csv
│
├── notebooks/                          # Analysis notebooks
│   ├── 01_exploration.ipynb            # Data exploration & validation
│   ├── 02_friction_signal.ipynb        # Signal engineering logic
│   └── 03_visualization.ipynb          # Charts & tables generation
│
├── outputs/                            # Final analytical outputs
│   │
│   ├── plots/                          # Visual insights (PNG)
│   │   ├── afi_heatmap_district_time.png
│   │   ├── afi_trend_selected_districts.png
│   │   ├── hidden_risk_scatter.png
│   │   └── lifecycle_flow_imbalance.png
│   │
│   ├── tables/                         # Decision-ready tables
│   │   ├── excel/
│   │   │   └── afi_analysis_tables.xlsx
│   │   │
│   │   ├── parquet/
│   │   │   ├── afi_summary_by_district.parquet
│   │   │   ├── afi_summary_by_state.parquet
│   │   │   ├── friction_signal_summary.parquet
│   │   │   └── hidden_risk.parquet
│   │   │
│   │   ├── sqlite/
│   │   │   └── aadhaar_friction_tables.db
│   │   │
│   │   ├── afi_summary_by_district.csv
│   │   ├── afi_summary_by_state.csv
│   │   ├── district_friction_typology.csv
│   │   ├── friction_signal_summary.csv
│   │   ├── hidden_risk_table.csv
│   │   ├── lifecycle_imbalance_table.csv
│   │   ├── monthly_afi_trends.csv
│   │   └── top_100_high_friction_records.csv
│
├── src/                                # Core business logic
│   ├── __init__.py
│   ├── preprocessing.py               # Data cleaning & normalization
│   ├── signal.py                      # Friction signal computation
│   ├── index.py                       # Aadhaar Friction Index (AFI) logic
│   └── utils.py                       # Reusable helpers (IO, paths, math)
│
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Ignore venv, cache, temp files
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Jupyter Notebook (optional, for interactive analysis)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Yogiii13/Aadhaar-Friction-Index-.git
   cd Aadhaar-Friction-Index-
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

#### Running the Complete Pipeline

```python
# Step 1: Clean and preprocess raw data
from src.preprocessing import preprocess_biometric, preprocess_demographic, preprocess_enrolment

biometric_clean = preprocess_biometric('datasets/raw/api_data_aadhar_biometric_0_500000.csv')
demographic_clean = preprocess_demographic('datasets/raw/api_data_aadhar_demographic_0_500000.csv')
enrolment_clean = preprocess_enrolment('datasets/raw/api_data_aadhar_enrolment_0_500000.csv')

# Step 2: Calculate friction signals
from src.signal import calculate_friction_signals

friction_signals = calculate_friction_signals(biometric_clean, demographic_clean, enrolment_clean)

# Step 3: Compute Aadhaar Friction Index
from src.index import calculate_afi

afi_scores = calculate_afi(friction_signals)
afi_ranked = afi_scores.sort_values('AFI', ascending=False)

print(afi_ranked.head(10))  # Top 10 highest friction areas
```

#### Using Jupyter Notebooks

Launch Jupyter and open the notebooks in sequence:

```bash
jupyter notebook
```

Navigate to the `notebooks/` directory and run in order:

1. `01_exploration.ipynb` - Explore raw data and understand patterns
2. `02_friction_signal.ipynb` - Calculate UIS, RIS, BSS, and TSD components
3. `03_aadhaar_friction_index_construction.ipynb` - Build and validate the AFI

## Key Metrics

The Aadhaar Friction Index (AFI) is calculated using four weighted components:

1. **Update Intensity Score (UIS)** - 30% weight: Measures how frequently users need to update their Aadhaar information
2. **Repeat Interaction Score (RIS)** - 25% weight: Tracks repeated authentication attempts indicating system friction
3. **Biometric Stress Score (BSS)** - 25% weight: Quantifies biometric authentication failures and retries
4. **Temporal Deviation (TSD)** - 20% weight: Captures time-based variations in system performance

**Formula**:

```python
AFI_raw = (0.30 × UIS) + (0.25 × RIS) + (0.25 × BSS) + (0.20 × TSD)
AFI = 100 × (AFI_raw - AFI_min) / (AFI_max - AFI_min)  # Normalized to 0-100 scale
```

The final AFI score ranges from 0 (lowest friction) to 100 (highest friction), providing a standardized measure across states, districts, and time periods.

## Data Sources

This project analyzes three primary datasets from UIDAI's public API (500,000 records each):

- **Biometric Updates**: Fingerprint and iris authentication data, failure rates, and biometric stress indicators
- **Demographic Updates**: Changes to address, name, and other demographic information in Aadhaar records
- **Enrolment Data**: New Aadhaar registrations and enrollment patterns across states and districts

The data spans multiple time periods (2025-01 onwards) and covers geographic levels from state down to district.

**Data Format**: All datasets contain columns for state, district, period (YYYY-MM), and various metrics used in AFI calculation.

*Note: Data is sourced from publicly available government APIs and is used for analytical purposes only.*

## Example Output

The analysis generates:

- State and district-level AFI rankings (normalized 0-100 scale)
- Monthly time-series analysis of friction patterns (2025-01 onwards)
- Top 10 highest friction areas identified
- Component breakdown showing which factors (UIS, RIS, BSS, TSD) contribute most to friction
- Comparative analysis across geographic regions

## Contributing

We welcome contributions! Here's how you can help:

- Report bugs or suggest features via [Issues](https://github.com/Yogiii13/Aadhaar-Friction-Index-/issues)
- Submit pull requests for bug fixes or enhancements
- Improve documentation or add examples
- Share datasets (ensuring proper anonymization)

Please read our contribution guidelines before submitting PRs.

## Support and Documentation

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/Yogiii13/Aadhaar-Friction-Index-/issues)
- **Discussions**: Ask questions and share ideas in [GitHub Discussions](https://github.com/Yogiii13/Aadhaar-Friction-Index-/discussions)
- **Documentation**: See the `docs/` folder for detailed methodology and API reference

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this project in your research or reporting, please cite:

```bibtex
@software{aadhaar_friction_index,
  author = {Yogiii13},
  title = {Aadhaar Friction Index: Analyzing Digital Identity System Barriers},
  year = {2024},
  url = {https://github.com/Yogiii13/Aadhaar-Friction-Index-}
}
```

## Maintainers

- [@Yogiii13](https://github.com/Yogiii13) - Project Creator and Lead Maintainer

## Acknowledgments

- UIDAI for publishing authentication statistics
- Open data contributors and researchers in the digital identity space
- Community members who provided feedback and suggestions

## Disclaimer

This is an independent analysis project. It is not affiliated with, endorsed by, or connected to UIDAI or the Government of India. The findings represent analytical interpretations of publicly available data.

---

**Status**: Active Development | **Version**: 1.0.0 | **Last Updated**: January 2026
