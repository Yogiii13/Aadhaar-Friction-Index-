"""
Friction signal calculation module
Computes UIS, RIS, BSS, and TSD components for Aadhaar Friction Index
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from utils import (
    normalize_column, print_section_header, 
    validate_dataframe, save_csv
)


def calculate_uis(biometric_df: pd.DataFrame, 
                  demographic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Update Intensity Score (UIS)
    Measures how frequently users need to update their Aadhaar information
    
    Args:
        biometric_df: Cleaned biometric updates data
        demographic_df: Cleaned demographic updates data
        
    Returns:
        DataFrame with UIS scores by state, district, period
    """
    print("\nCalculating Update Intensity Score (UIS)...")
    
    # Merge datasets
    merge_keys = ['state', 'district', 'period']
    df = pd.merge(biometric_df, demographic_df, on=merge_keys, how='outer', suffixes=('_bio', '_demo'))
    
    # Identify update columns (exclude merge keys)
    bio_update_cols = [col for col in biometric_df.columns if col not in merge_keys]
    demo_update_cols = [col for col in demographic_df.columns if col not in merge_keys]
    
    # Calculate total update frequency
    # Sum all biometric updates
    df['bio_updates'] = df[[col for col in df.columns if col.endswith('_bio') or col in bio_update_cols]].sum(axis=1)
    
    # Sum all demographic updates
    df['demo_updates'] = df[[col for col in df.columns if col.endswith('_demo') or col in demo_update_cols]].sum(axis=1)
    
    # Total updates (weighted: biometric updates are more friction-prone)
    df['total_updates'] = (df['bio_updates'] * 1.5) + df['demo_updates']
    
    # Calculate update rate per 1000 people (if population data available)
    # Otherwise use raw counts
    df['UIS'] = df['total_updates']
    
    # Normalize to 0-100 scale
    df['UIS'] = normalize_column(df['UIS'], 0, 100)
    
    # Select relevant columns
    result = df[merge_keys + ['UIS']].copy()
    
    print(f"  ✓ UIS calculated for {len(result)} records")
    print(f"    Range: {result['UIS'].min():.2f} - {result['UIS'].max():.2f}")
    print(f"    Mean: {result['UIS'].mean():.2f}, Median: {result['UIS'].median():.2f}")
    
    return result


def calculate_ris(biometric_df: pd.DataFrame, 
                  demographic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Repeat Interaction Score (RIS)
    Tracks repeated authentication attempts indicating system friction
    
    Args:
        biometric_df: Cleaned biometric updates data
        demographic_df: Cleaned demographic updates data
        
    Returns:
        DataFrame with RIS scores by state, district, period
    """
    print("\nCalculating Repeat Interaction Score (RIS)...")
    
    merge_keys = ['state', 'district', 'period']
    df = pd.merge(biometric_df, demographic_df, on=merge_keys, how='outer')
    
    # Calculate repeat interaction metrics
    # Assumption: Failed attempts require repeat interactions
    
    # Identify columns that indicate failures or retries
    failure_cols = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['fail', 'retry', 'reject', 'error', 'repeat'])]
    
    if failure_cols:
        df['repeat_interactions'] = df[failure_cols].sum(axis=1)
    else:
        # If no explicit failure columns, use update frequency as proxy
        update_cols = [col for col in df.columns if col not in merge_keys]
        df['repeat_interactions'] = df[update_cols].std(axis=1)
    
    # Calculate RIS
    df['RIS'] = df['repeat_interactions']
    
    # Normalize to 0-100 scale
    df['RIS'] = normalize_column(df['RIS'], 0, 100)
    
    result = df[merge_keys + ['RIS']].copy()
    
    print(f"  ✓ RIS calculated for {len(result)} records")
    print(f"    Range: {result['RIS'].min():.2f} - {result['RIS'].max():.2f}")
    print(f"    Mean: {result['RIS'].mean():.2f}, Median: {result['RIS'].median():.2f}")
    
    return result


def calculate_bss(biometric_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Biometric Stress Score (BSS)
    Quantifies biometric authentication failures and retries
    
    Args:
        biometric_df: Cleaned biometric updates data
        
    Returns:
        DataFrame with BSS scores by state, district, period
    """
    print("\nCalculating Biometric Stress Score (BSS)...")
    
    merge_keys = ['state', 'district', 'period']
    df = biometric_df.copy()
    
    # Identify biometric-related columns
    bio_cols = [col for col in df.columns if col not in merge_keys]
    
    # Calculate biometric stress indicators
    # Higher values indicate more stress/friction
    
    # 1. Total biometric transactions
    df['total_bio_transactions'] = df[bio_cols].sum(axis=1)
    
    # 2. Variance in biometric attempts (higher variance = more stress)
    df['bio_variance'] = df[bio_cols].var(axis=1)
    
    # 3. Maximum value (indicates peak stress)
    df['bio_max'] = df[bio_cols].max(axis=1)
    
    # Combine metrics with weights
    df['BSS_raw'] = (
        df['total_bio_transactions'] * 0.4 +
        df['bio_variance'] * 0.3 +
        df['bio_max'] * 0.3
    )
    
    # Normalize to 0-100 scale
    df['BSS'] = normalize_column(df['BSS_raw'], 0, 100)
    
    result = df[merge_keys + ['BSS']].copy()
    
    print(f"  ✓ BSS calculated for {len(result)} records")
    print(f"    Range: {result['BSS'].min():.2f} - {result['BSS'].max():.2f}")
    print(f"    Mean: {result['BSS'].mean():.2f}, Median: {result['BSS'].median():.2f}")
    
    return result


def calculate_tsd(biometric_df: pd.DataFrame, 
                  demographic_df: pd.DataFrame,
                  enrolment_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Temporal Deviation (TSD)
    Captures time-based variations in system performance
    
    Args:
        biometric_df: Cleaned biometric updates data
        demographic_df: Cleaned demographic updates data
        enrolment_df: Cleaned enrolment data
        
    Returns:
        DataFrame with TSD scores by state, district, period
    """
    print("\nCalculating Temporal Deviation (TSD)...")
    
    merge_keys = ['state', 'district', 'period']
    
    # Merge all datasets
    df = biometric_df.copy()
    df = pd.merge(df, demographic_df, on=merge_keys, how='outer', suffixes=('_bio', '_demo'))
    df = pd.merge(df, enrolment_df, on=merge_keys, how='outer')
    
    # Calculate temporal metrics
    # Group by state and district to calculate deviations over time
    
    all_value_cols = [col for col in df.columns if col not in merge_keys]
    df['total_activity'] = df[all_value_cols].sum(axis=1)
    
    # Calculate rolling statistics within each state-district group
    df = df.sort_values(merge_keys)
    
    # Calculate deviation from group mean
    df['group_mean'] = df.groupby(['state', 'district'])['total_activity'].transform('mean')
    df['deviation_from_mean'] = np.abs(df['total_activity'] - df['group_mean'])
    
    # Calculate month-over-month change (volatility)
    df['mom_change'] = df.groupby(['state', 'district'])['total_activity'].diff().abs()
    
    # Calculate coefficient of variation within group
    df['group_std'] = df.groupby(['state', 'district'])['total_activity'].transform('std')
    df['coefficient_of_variation'] = df['group_std'] / (df['group_mean'] + 1)  # +1 to avoid division by zero
    
    # Combine temporal deviation metrics
    df['TSD_raw'] = (
        df['deviation_from_mean'] * 0.4 +
        df['mom_change'].fillna(0) * 0.3 +
        df['coefficient_of_variation'] * 0.3
    )
    
    # Normalize to 0-100 scale
    df['TSD'] = normalize_column(df['TSD_raw'], 0, 100)
    
    result = df[merge_keys + ['TSD']].copy()
    
    print(f"  ✓ TSD calculated for {len(result)} records")
    print(f"    Range: {result['TSD'].min():.2f} - {result['TSD'].max():.2f}")
    print(f"    Mean: {result['TSD'].mean():.2f}, Median: {result['TSD'].median():.2f}")
    
    return result


def calculate_all_signals(biometric_df: pd.DataFrame,
                          demographic_df: pd.DataFrame,
                          enrolment_df: pd.DataFrame,
                          output_path: str = None) -> pd.DataFrame:
    """
    Calculate all friction signals (UIS, RIS, BSS, TSD)
    
    Args:
        biometric_df: Cleaned biometric data
        demographic_df: Cleaned demographic data
        enrolment_df: Cleaned enrolment data
        output_path: Optional path to save results
        
    Returns:
        DataFrame with all friction signals
    """
    print_section_header("CALCULATING FRICTION SIGNALS")
    
    merge_keys = ['state', 'district', 'period']
    
    # Calculate each signal
    uis_df = calculate_uis(biometric_df, demographic_df)
    ris_df = calculate_ris(biometric_df, demographic_df)
    bss_df = calculate_bss(biometric_df)
    tsd_df = calculate_tsd(biometric_df, demographic_df, enrolment_df)
    
    # Merge all signals
    print("\nMerging all signals...")
    signals = uis_df.copy()
    signals = pd.merge(signals, ris_df, on=merge_keys, how='outer')
    signals = pd.merge(signals, bss_df, on=merge_keys, how='outer')
    signals = pd.merge(signals, tsd_df, on=merge_keys, how='outer')
    
    # Fill any missing values with 0
    signals[['UIS', 'RIS', 'BSS', 'TSD']] = signals[['UIS', 'RIS', 'BSS', 'TSD']].fillna(0)
    
    print(f"\n✓ All friction signals calculated: {len(signals)} records")
    print(f"\nSignal Summary:")
    print(signals[['UIS', 'RIS', 'BSS', 'TSD']].describe().round(2))
    
    # Save if output path provided
    if output_path:
        save_csv(signals, output_path)
    
    return signals


if __name__ == "__main__":
    # Example usage
    from preprocessing import preprocess_all
    
    # Load and preprocess data
    bio, demo, enrol = preprocess_all(
        'datasets/raw/api_data_aadhar_biometric_0_500000.csv',
        'datasets/raw/api_data_aadhar_demographic_0_500000.csv',
        'datasets/raw/api_data_aadhar_enrolment_0_500000.csv'
    )
    
    # Calculate friction signals
    signals = calculate_all_signals(
        bio, demo, enrol,
        output_path='datasets/processed/signals/friction_signals.csv'
    )