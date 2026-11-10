from virtual_lab.data_analyzer import (
    load_dataset,
    get_dataset_overview,
    calculate_statistics,
    calculate_correlations,
    radiation_analysis
)

df = load_dataset("sample_data/radiation_sample.csv")

print("\nDATASET OVERVIEW")
print(get_dataset_overview(df))

print("\nSTATISTICS")
print(calculate_statistics(df))

print("\nCORRELATIONS")
print(calculate_correlations(df))

print("\nRADIATION ANALYSIS")
print(
    radiation_analysis(
        df,
        "dose_gy",
        "survival_percentage"
    )
)