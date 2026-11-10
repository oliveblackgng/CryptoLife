
import pandas as pd
import numpy as np


# ---------------------------------------
# 1. LOAD CSV OR EXCEL DATASET
# ---------------------------------------

def load_dataset(file_path):

    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)

    elif file_path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported file format. Upload CSV or Excel."
        )

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    # Remove completely empty rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    if df.empty:
        raise ValueError("The dataset contains no usable data.")

    return df


# ---------------------------------------
# 2. DATASET OVERVIEW
# ---------------------------------------

def get_dataset_overview(df):

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "missing_values": {
            str(column): int(count)
            for column, count in df.isnull().sum().items()
        },
        "numeric_columns": list(
            df.select_dtypes(include=np.number).columns
        )
    }


# ---------------------------------------
# 3. DESCRIPTIVE STATISTICS
# ---------------------------------------

def calculate_statistics(df):

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.empty:
        raise ValueError(
            "No numeric columns were found in this dataset."
        )

    statistics = numeric_df.describe().round(3)

    return statistics.to_dict()


# ---------------------------------------
# 4. CORRELATION ANALYSIS
# ---------------------------------------

def calculate_correlations(df):

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] < 2:
        return {}

    correlations = numeric_df.corr().round(3)

    return correlations.to_dict()


# ---------------------------------------
# 5. RADIATION TOLERANCE ANALYSIS
# ---------------------------------------



def radiation_analysis(df, dose_column, survival_column):

    if dose_column not in df.columns:
        raise ValueError("Radiation dose column not found.")

    if survival_column not in df.columns:
        raise ValueError("Activity column not found.")

    dose = pd.to_numeric(df[dose_column], errors="coerce")
    activity = pd.to_numeric(df[survival_column], errors="coerce")

    data = pd.DataFrame({
        "dose": dose,
        "activity": activity
    }).dropna()

    if len(data) < 3:
        raise ValueError("At least three valid observations are required.")

    if (data["dose"] < 0).any():
        raise ValueError("Radiation dose cannot be negative.")

    # Convert proportions into percentages
    if data["activity"].max() <= 1:
        data["activity"] = data["activity"] * 100

    if not data["activity"].between(0, 100).all():
        raise ValueError("Activity must be between 0 and 100.")

    data = data.sort_values("dose")

    correlation = data["dose"].corr(data["activity"])

    return {
        "observations": int(len(data)),
        "mean_dose": round(float(data["dose"].mean()), 3),
        "mean_activity": round(float(data["activity"].mean()), 2),
        "correlation": round(float(correlation), 4),
        "dose_column": dose_column,
        "activity_column": survival_column,

        # Data required by Chart.js
        "chart_labels": data["dose"].tolist(),
        "chart_values": data["activity"].tolist()
    }
