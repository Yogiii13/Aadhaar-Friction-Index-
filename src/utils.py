"""
Utility functions for Aadhaar Friction Index project
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load CSV file with error handling
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        DataFrame with loaded data
    """
    try:
        df = pd.read_csv(filepath)
        print(f"✓ Loaded {filepath}: {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        print(f"✗ Error: File not found - {filepath}")
        raise
    except Exception as e:
        print(f"✗ Error loading {filepath}: {str(e)}")
        raise


def save_csv(df: pd.DataFrame, filepath: str) -> None:
    """
    Save DataFrame to CSV with confirmation
    
    Args:
        df: DataFrame to save
        filepath: Output file path
    """
    try:
        df.to_csv(filepath, index=False)
        print(f"✓ Saved to {filepath}: {len(df)} rows")
    except Exception as e:
        print(f"✗ Error saving to {filepath}: {str(e)}")
        raise


def check_missing_values(df: pd.DataFrame, name: str = "Dataset") -> Dict:
    """
    Check for missing values in DataFrame
    
    Args:
        df: DataFrame to check
        name: Name for reporting
        
    Returns:
        Dictionary with missing value statistics
    """
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing': missing.values,
        'Percentage': missing_pct.values
    })
    
    missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False)
    
    if len(missing_df) > 0:
        print(f"\n⚠ Missing values in {name}:")
        print(missing_df.to_string(index=False))
    else:
        print(f"✓ No missing values in {name}")
    
    return {
        'total_missing': missing.sum(),
        'columns_with_missing': len(missing_df),
        'details': missing_df
    }


def normalize_column(series: pd.Series, min_val: float = 0, max_val: float = 100) -> pd.Series:
    """
    Normalize a series to a specified range (default 0-100)
    
    Args:
        series: Pandas Series to normalize
        min_val: Minimum value of output range
        max_val: Maximum value of output range
        
    Returns:
        Normalized series
    """
    series_min = series.min()
    series_max = series.max()
    
    if series_max == series_min:
        return pd.Series([min_val] * len(series), index=series.index)
    
    normalized = min_val + (series - series_min) * (max_val - min_val) / (series_max - series_min)
    return normalized


def validate_dataframe(df: pd.DataFrame, required_columns: List[str], name: str = "Dataset") -> bool:
    """
    Validate that DataFrame contains required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        name: Dataset name for reporting
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    missing_cols = set(required_columns) - set(df.columns)
    
    if missing_cols:
        raise ValueError(f"✗ {name} missing required columns: {missing_cols}")
    
    print(f"✓ {name} validation passed")
    return True


def aggregate_by_geography(df: pd.DataFrame, 
                          value_cols: List[str],
                          group_cols: List[str] = ['state', 'district', 'period'],
                          agg_func: str = 'mean') -> pd.DataFrame:
    """
    Aggregate data by geographic and temporal dimensions
    
    Args:
        df: DataFrame to aggregate
        value_cols: Columns to aggregate
        group_cols: Columns to group by
        agg_func: Aggregation function (mean, sum, etc.)
        
    Returns:
        Aggregated DataFrame
    """
    agg_dict = {col: agg_func for col in value_cols}
    
    aggregated = df.groupby(group_cols, as_index=False).agg(agg_dict)
    
    print(f"✓ Aggregated from {len(df)} to {len(aggregated)} rows")
    return aggregated


def calculate_percentile_rank(df: pd.DataFrame, column: str, ascending: bool = False) -> pd.Series:
    """
    Calculate percentile rank for a column
    
    Args:
        df: DataFrame containing the data
        column: Column name to rank
        ascending: If True, lower values get higher ranks
        
    Returns:
        Series with percentile ranks (0-100)
    """
    return df[column].rank(pct=True, ascending=ascending) * 100


def detect_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Detect outliers in a series using IQR or Z-score method
    
    Args:
        series: Data series
        method: 'iqr' or 'zscore'
        threshold: Threshold for outlier detection (1.5 for IQR, 3 for Z-score)
        
    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (series < lower_bound) | (series > upper_bound)
        
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        outliers = z_scores > threshold
        
    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'")
    
    outlier_count = outliers.sum()
    if outlier_count > 0:
        print(f"⚠ Detected {outlier_count} outliers ({outlier_count/len(series)*100:.2f}%)")
    
    return outliers


def create_time_features(df: pd.DataFrame, period_col: str = 'period') -> pd.DataFrame:
    """
    Create time-based features from period column (YYYY-MM format)
    
    Args:
        df: DataFrame with period column
        period_col: Name of period column
        
    Returns:
        DataFrame with added time features
    """
    df = df.copy()
    
    # Convert period to datetime
    df['date'] = pd.to_datetime(df[period_col], format='%Y-%m')
    
    # Extract features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['month_name'] = df['date'].dt.strftime('%B')
    
    # Calculate time-based metrics
    df['months_since_start'] = (df['date'] - df['date'].min()).dt.days / 30.44
    
    print(f"✓ Created time features from {period_col}")
    return df


def summary_statistics(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Generate comprehensive summary statistics
    
    Args:
        df: DataFrame to summarize
        columns: Specific columns to summarize (None = all numeric)
        
    Returns:
        DataFrame with summary statistics
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    summary = df[columns].describe().T
    summary['missing'] = df[columns].isnull().sum()
    summary['missing_pct'] = (summary['missing'] / len(df)) * 100
    summary['skewness'] = df[columns].skew()
    summary['kurtosis'] = df[columns].kurtosis()
    
    return summary.round(2)


def print_section_header(title: str, width: int = 60) -> None:
    """
    Print a formatted section header
    
    Args:
        title: Section title
        width: Total width of header
    """
    print("\n" + "=" * width)
    print(f" {title} ".center(width))
    print("=" * width + "\n")