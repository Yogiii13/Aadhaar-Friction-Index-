"""
Aadhaar Friction Index (AFI) calculation module
Combines friction signals into a composite index
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from utils import (
    normalize_column, print_section_header, 
    save_csv, calculate_percentile_rank
)


# AFI component weights
WEIGHTS = {
    "UIS": 0.30,  # Update Intensity Score
    "RIS": 0.25,  # Repeat Interaction Score
    "BSS": 0.25,  # Biometric Stress Score
    "TSD": 0.20   # Temporal Deviation
}


def validate_signals(df: pd.DataFrame) -> bool:
    """
    Validate that all required signals are present
    
    Args:
        df: DataFrame with friction signals
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    required_columns = ['state', 'district', 'period', 'UIS', 'RIS', 'BSS', 'TSD']
    missing = set(required_columns) - set(df.columns)
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Check for negative values
    signal_cols = ['UIS', 'RIS', 'BSS', 'TSD']
    for col in signal_cols:
        if (df[col] < 0).any():
            raise ValueError(f"Negative values found in {col}")
    
    print("✓ Signal validation passed")
    return True


def calculate_afi_raw(df: pd.DataFrame, weights: Dict[str, float] = WEIGHTS) -> pd.DataFrame:
    """
    Calculate raw AFI score using weighted sum of signals
    
    Args:
        df: DataFrame with friction signals (UIS, RIS, BSS, TSD)
        weights: Dictionary of component weights
        
    Returns:
        DataFrame with AFI_raw column added
    """
    df = df.copy()
    
    # Verify weights sum to 1.0
    weight_sum = sum(weights.values())
    if not np.isclose(weight_sum, 1.0):
        raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
    
    # Calculate weighted sum
    df['AFI_raw'] = (
        weights['UIS'] * df['UIS'] +
        weights['RIS'] * df['RIS'] +
        weights['BSS'] * df['BSS'] +
        weights['TSD'] * df['TSD']
    )
    
    print(f"  Raw AFI range: {df['AFI_raw'].min():.2f} - {df['AFI_raw'].max():.2f}")
    
    return df


def normalize_afi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize AFI to 0-100 scale
    
    Args:
        df: DataFrame with AFI_raw column
        
    Returns:
        DataFrame with normalized AFI column
    """
    df = df.copy()
    
    # Get min and max for normalization
    afi_min = df['AFI_raw'].min()
    afi_max = df['AFI_raw'].max()
    
    # Normalize: AFI = 100 * (AFI_raw - min) / (max - min)
    df['AFI'] = 100 * (df['AFI_raw'] - afi_min) / (afi_max - afi_min)
    
    print(f"  Normalized AFI range: {df['AFI'].min():.2f} - {df['AFI'].max():.2f}")
    print(f"  Mean AFI: {df['AFI'].mean():.2f}, Median: {df['AFI'].median():.2f}")
    
    return df


def add_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add national and state-level rankings
    
    Args:
        df: DataFrame with AFI scores
        
    Returns:
        DataFrame with ranking columns added
    """
    df = df.copy()
    
    # National ranking (higher AFI = worse, so rank descending)
    df['national_rank'] = df['AFI'].rank(ascending=False, method='min').astype(int)
    
    # State-level ranking
    df['state_rank'] = df.groupby('state')['AFI'].rank(ascending=False, method='min').astype(int)
    
    # Percentile scores
    df['national_percentile'] = calculate_percentile_rank(df, 'AFI', ascending=False)
    
    print(f"  Added rankings: National and State-level")
    
    return df


def add_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize AFI scores into friction levels
    
    Args:
        df: DataFrame with AFI scores
        
    Returns:
        DataFrame with category column added
    """
    df = df.copy()
    
    # Define categories based on AFI score
    def categorize_afi(score):
        if score < 20:
            return "Very Low Friction"
        elif score < 40:
            return "Low Friction"
        elif score < 60:
            return "Moderate Friction"
        elif score < 80:
            return "High Friction"
        else:
            return "Very High Friction"
    
    df['friction_category'] = df['AFI'].apply(categorize_afi)
    
    # Count by category
    category_counts = df['friction_category'].value_counts()
    print(f"\n  Friction Distribution:")
    for category, count in category_counts.items():
        print(f"    {category}: {count} ({count/len(df)*100:.1f}%)")
    
    return df


def identify_top_friction_areas(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Identify areas with highest friction
    
    Args:
        df: DataFrame with AFI scores
        top_n: Number of top areas to return
        
    Returns:
        DataFrame with top friction areas
    """
    top_areas = df.nlargest(top_n, 'AFI')[
        ['state', 'district', 'period', 'AFI', 'UIS', 'RIS', 'BSS', 'TSD', 
         'national_rank', 'friction_category']
    ].copy()
    
    return top_areas


def analyze_components(df: pd.DataFrame) -> Dict:
    """
    Analyze which components contribute most to friction
    
    Args:
        df: DataFrame with AFI scores and components
        
    Returns:
        Dictionary with component analysis
    """
    analysis = {}
    
    # Calculate correlation between components and AFI
    components = ['UIS', 'RIS', 'BSS', 'TSD']
    correlations = {}
    
    for comp in components:
        corr = df[comp].corr(df['AFI'])
        correlations[comp] = corr
    
    # Find dominant component (highest correlation)
    dominant_component = max(correlations, key=correlations.get)
    
    # Calculate average contribution
    avg_contributions = {}
    for comp in components:
        avg_contributions[comp] = (df[comp] * WEIGHTS[comp]).mean()
    
    analysis = {
        'correlations': correlations,
        'dominant_component': dominant_component,
        'average_contributions': avg_contributions,
        'component_stats': df[components].describe().to_dict()
    }
    
    return analysis


def calculate_afi(signals_df: pd.DataFrame,
                  weights: Dict[str, float] = WEIGHTS,
                  output_dir: str = 'datasets/processed/index/') -> pd.DataFrame:
    """
    Complete AFI calculation pipeline
    
    Args:
        signals_df: DataFrame with friction signals
        weights: Component weights
        output_dir: Directory to save output files
        
    Returns:
        DataFrame with complete AFI scores and rankings
    """
    print_section_header("CALCULATING AADHAAR FRICTION INDEX (AFI)")
    
    # Validate input
    validate_signals(signals_df)
    
    print(f"\nInput: {len(signals_df)} records")
    print(f"Weights: UIS={weights['UIS']}, RIS={weights['RIS']}, "
          f"BSS={weights['BSS']}, TSD={weights['TSD']}")
    
    # Calculate raw AFI
    print("\nStep 1: Calculating raw AFI...")
    df = calculate_afi_raw(signals_df, weights)
    
    # Normalize AFI
    print("\nStep 2: Normalizing AFI to 0-100 scale...")
    df = normalize_afi(df)
    
    # Add rankings
    print("\nStep 3: Adding rankings...")
    df = add_rankings(df)
    
    # Add categories
    print("\nStep 4: Categorizing friction levels...")
    df = add_categories(df)
    
    # Analyze components
    print("\nStep 5: Analyzing components...")
    component_analysis = analyze_components(df)
    
    print(f"\n  Component Correlations with AFI:")
    for comp, corr in component_analysis['correlations'].items():
        print(f"    {comp}: {corr:.3f}")
    
    print(f"\n  Dominant Component: {component_analysis['dominant_component']}")
    
    # Sort by AFI (highest first)
    df = df.sort_values('AFI', ascending=False)
    
    # Save outputs
    print_section_header("SAVING OUTPUTS")
    
    # Full index with all columns
    save_csv(df, f"{output_dir}aadhaar_friction_index.csv")
    
    # Index with rankings
    ranked_df = df[['state', 'district', 'period', 'AFI', 'national_rank', 
                    'state_rank', 'national_percentile', 'friction_category']].copy()
    save_csv(ranked_df, f"{output_dir}aadhaar_friction_index_ranked.csv")
    
    # Index scores only
    index_only = df[['state', 'district', 'period', 'AFI']].copy()
    save_csv(index_only, f"{output_dir}aadhaar_friction_index_only.csv")
    
    # Display top friction areas
    print_section_header("TOP 10 HIGHEST FRICTION AREAS")
    top_10 = identify_top_friction_areas(df, 10)
    print(top_10.to_string(index=False))
    
    print_section_header("AFI CALCULATION COMPLETE")
    print(f"✓ Processed {len(df)} records")
    print(f"✓ AFI range: {df['AFI'].min():.2f} - {df['AFI'].max():.2f}")
    print(f"✓ Output files saved to {output_dir}")
    
    return df


def generate_summary_report(afi_df: pd.DataFrame) -> str:
    """
    Generate a summary report of AFI results
    
    Args:
        afi_df: DataFrame with AFI scores
        
    Returns:
        Formatted summary report as string
    """
    report = []
    report.append("=" * 60)
    report.append("AADHAAR FRICTION INDEX - SUMMARY REPORT")
    report.append("=" * 60)
    
    report.append(f"\nTotal Records: {len(afi_df)}")
    report.append(f"States Covered: {afi_df['state'].nunique()}")
    report.append(f"Districts Covered: {afi_df['district'].nunique()}")
    report.append(f"Time Periods: {afi_df['period'].nunique()}")
    
    report.append(f"\n{'AFI Statistics':-^60}")
    report.append(f"Minimum: {afi_df['AFI'].min():.2f}")
    report.append(f"Maximum: {afi_df['AFI'].max():.2f}")
    report.append(f"Mean: {afi_df['AFI'].mean():.2f}")
    report.append(f"Median: {afi_df['AFI'].median():.2f}")
    report.append(f"Std Dev: {afi_df['AFI'].std():.2f}")
    
    report.append(f"\n{'Top 5 States by Avg AFI':-^60}")
    top_states = afi_df.groupby('state')['AFI'].mean().sort_values(ascending=False).head()
    for state, afi in top_states.items():
        report.append(f"{state}: {afi:.2f}")
    
    report.append(f"\n{'Friction Category Distribution':-^60}")
    category_dist = afi_df['friction_category'].value_counts()
    for category, count in category_dist.items():
        pct = count / len(afi_df) * 100
        report.append(f"{category}: {count} ({pct:.1f}%)")
    
    report.append("\n" + "=" * 60)
    
    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    from preprocessing import preprocess_all
    from signal import calculate_all_signals
    
    # Load and preprocess data
    bio, demo, enrol = preprocess_all(
        'datasets/raw/api_data_aadhar_biometric_0_500000.csv',
        'datasets/raw/api_data_aadhar_demographic_0_500000.csv',
        'datasets/raw/api_data_aadhar_enrolment_0_500000.csv'
    )
    
    # Calculate friction signals
    signals = calculate_all_signals(bio, demo, enrol)
    
    # Calculate AFI
    afi = calculate_afi(signals)
    
    # Generate and print summary report
    report = generate_summary_report(afi)
    print(report)