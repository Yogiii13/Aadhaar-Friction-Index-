"""
Data preprocessing pipeline for Aadhaar datasets
Handles cleaning and preparation of biometric, demographic, and enrolment data
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
from utils import (
    load_csv, save_csv, check_missing_values, 
    validate_dataframe, print_section_header
)


def clean_common_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean common columns present in all datasets
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Standardize column names (lowercase, remove spaces)
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Clean state and district names
    if 'state' in df.columns:
        df['state'] = df['state'].str.strip().str.title()
    
    if 'district' in df.columns:
        df['district'] = df['district'].str.strip().str.title()
    
    # Standardize period format (YYYY-MM)
    if 'period' in df.columns:
        df['period'] = pd.to_datetime(df['period']).dt.strftime('%Y-%m')
    
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    
    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed} duplicate rows")
    
    return df


def preprocess_biometric(filepath: str, output_path: str = None) -> pd.DataFrame:
    """
    Preprocess biometric updates data
    
    Args:
        filepath: Path to raw biometric CSV
        output_path: Optional path to save cleaned data
        
    Returns:
        Cleaned biometric DataFrame
    """
    print_section_header("PREPROCESSING BIOMETRIC DATA")
    
    # Load data
    df = load_csv(filepath)
    
    # Check missing values
    check_missing_values(df, "Raw Biometric Data")
    
    # Clean common columns
    df = clean_common_columns(df)
    
    # Expected columns for biometric data
    numeric_cols = [col for col in df.columns if col not in ['state', 'district', 'period']]
    
    # Handle missing values in numeric columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            # Fill missing with median for that state/district
            df[col] = df.groupby(['state', 'district'])[col].transform(
                lambda x: x.fillna(x.median())
            )
            # If still missing, fill with overall median
            df[col].fillna(df[col].median(), inplace=True)
    
    # Remove negative values (data quality issue)
    for col in numeric_cols:
        if (df[col] < 0).any():
            print(f"  ⚠ Removing {(df[col] < 0).sum()} negative values in {col}")
            df[col] = df[col].clip(lower=0)
    
    # Remove outliers (values > 99th percentile)
    for col in numeric_cols:
        threshold = df[col].quantile(0.99)
        outliers = df[col] > threshold
        if outliers.sum() > 0:
            print(f"  ⚠ Capping {outliers.sum()} outliers in {col}")
            df.loc[outliers, col] = threshold
    
    print(f"\n✓ Biometric preprocessing complete: {len(df)} rows, {len(df.columns)} columns")
    
    # Save if output path provided
    if output_path:
        save_csv(df, output_path)
    
    return df


def preprocess_demographic(filepath: str, output_path: str = None) -> pd.DataFrame:
    """
    Preprocess demographic updates data
    
    Args:
        filepath: Path to raw demographic CSV
        output_path: Optional path to save cleaned data
        
    Returns:
        Cleaned demographic DataFrame
    """
    print_section_header("PREPROCESSING DEMOGRAPHIC DATA")
    
    # Load data
    df = load_csv(filepath)
    
    # Check missing values
    check_missing_values(df, "Raw Demographic Data")
    
    # Clean common columns
    df = clean_common_columns(df)
    
    # Expected columns for demographic data
    numeric_cols = [col for col in df.columns if col not in ['state', 'district', 'period']]
    
    # Handle missing values
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            # Fill with state/district median
            df[col] = df.groupby(['state', 'district'])[col].transform(
                lambda x: x.fillna(x.median())
            )
            df[col].fillna(df[col].median(), inplace=True)
    
    # Data validation
    for col in numeric_cols:
        # Remove negative values
        if (df[col] < 0).any():
            print(f"  ⚠ Removing {(df[col] < 0).sum()} negative values in {col}")
            df[col] = df[col].clip(lower=0)
        
        # Cap extreme outliers
        threshold = df[col].quantile(0.99)
        outliers = df[col] > threshold
        if outliers.sum() > 0:
            print(f"  ⚠ Capping {outliers.sum()} outliers in {col}")
            df.loc[outliers, col] = threshold
    
    print(f"\n✓ Demographic preprocessing complete: {len(df)} rows, {len(df.columns)} columns")
    
    # Save if output path provided
    if output_path:
        save_csv(df, output_path)
    
    return df


def preprocess_enrolment(filepath: str, output_path: str = None) -> pd.DataFrame:
    """
    Preprocess enrolment data
    
    Args:
        filepath: Path to raw enrolment CSV
        output_path: Optional path to save cleaned data
        
    Returns:
        Cleaned enrolment DataFrame
    """
    print_section_header("PREPROCESSING ENROLMENT DATA")
    
    # Load data
    df = load_csv(filepath)
    
    # Check missing values
    check_missing_values(df, "Raw Enrolment Data")
    
    # Clean common columns
    df = clean_common_columns(df)
    
    # Expected columns for enrolment data
    numeric_cols = [col for col in df.columns if col not in ['state', 'district', 'period']]
    
    # Handle missing values
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df.groupby(['state', 'district'])[col].transform(
                lambda x: x.fillna(x.median())
            )
            df[col].fillna(df[col].median(), inplace=True)
    
    # Data validation
    for col in numeric_cols:
        # Remove negative values
        if (df[col] < 0).any():
            print(f"  ⚠ Removing {(df[col] < 0).sum()} negative values in {col}")
            df[col] = df[col].clip(lower=0)
        
        # Cap outliers
        threshold = df[col].quantile(0.99)
        outliers = df[col] > threshold
        if outliers.sum() > 0:
            print(f"  ⚠ Capping {outliers.sum()} outliers in {col}")
            df.loc[outliers, col] = threshold
    
    print(f"\n✓ Enrolment preprocessing complete: {len(df)} rows, {len(df.columns)} columns")
    
    # Save if output path provided
    if output_path:
        save_csv(df, output_path)
    
    return df


def merge_datasets(biometric_df: pd.DataFrame, 
                   demographic_df: pd.DataFrame, 
                   enrolment_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge all three cleaned datasets
    
    Args:
        biometric_df: Cleaned biometric data
        demographic_df: Cleaned demographic data
        enrolment_df: Cleaned enrolment data
        
    Returns:
        Merged DataFrame
    """
    print_section_header("MERGING DATASETS")
    
    merge_keys = ['state', 'district', 'period']
    
    # Validate merge keys exist
    for df_name, df in [('Biometric', biometric_df), 
                        ('Demographic', demographic_df), 
                        ('Enrolment', enrolment_df)]:
        validate_dataframe(df, merge_keys, df_name)
    
    # Merge biometric and demographic
    merged = pd.merge(
        biometric_df, 
        demographic_df, 
        on=merge_keys, 
        how='outer',
        suffixes=('_bio', '_demo')
    )
    
    print(f"  Merged Biometric + Demographic: {len(merged)} rows")
    
    # Merge with enrolment
    merged = pd.merge(
        merged, 
        enrolment_df, 
        on=merge_keys, 
        how='outer',
        suffixes=('', '_enrol')
    )
    
    print(f"  Final merged dataset: {len(merged)} rows")
    
    # Check for missing values after merge
    check_missing_values(merged, "Merged Dataset")
    
    return merged


def preprocess_all(biometric_path: str,
                   demographic_path: str,
                   enrolment_path: str,
                   output_dir: str = 'datasets/processed/') -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run complete preprocessing pipeline for all datasets
    
    Args:
        biometric_path: Path to raw biometric CSV
        demographic_path: Path to raw demographic CSV
        enrolment_path: Path to raw enrolment CSV
        output_dir: Directory to save cleaned files
        
    Returns:
        Tuple of (biometric_df, demographic_df, enrolment_df)
    """
    print_section_header("AADHAAR DATA PREPROCESSING PIPELINE")
    
    # Preprocess each dataset
    biometric_clean = preprocess_biometric(
        biometric_path, 
        f"{output_dir}biometric_updates_cleaned.csv"
    )
    
    demographic_clean = preprocess_demographic(
        demographic_path,
        f"{output_dir}demographic_updates_cleaned.csv"
    )
    
    enrolment_clean = preprocess_enrolment(
        enrolment_path,
        f"{output_dir}enrolment_cleaned.csv"
    )
    
    print_section_header("PREPROCESSING COMPLETE")
    print("✓ All datasets cleaned and saved")
    print(f"  - Biometric: {len(biometric_clean)} rows")
    print(f"  - Demographic: {len(demographic_clean)} rows")
    print(f"  - Enrolment: {len(enrolment_clean)} rows")
    
    return biometric_clean, demographic_clean, enrolment_clean


if __name__ == "__main__":
    # Example usage
    bio, demo, enrol = preprocess_all(
        biometric_path='datasets/raw/api_data_aadhar_biometric_0_500000.csv',
        demographic_path='datasets/raw/api_data_aadhar_demographic_0_500000.csv',
        enrolment_path='datasets/raw/api_data_aadhar_enrolment_0_500000.csv'
    )