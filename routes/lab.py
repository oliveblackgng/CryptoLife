
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    current_app
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from virtual_lab.calculations import (
    simulate_cryptobiosis,
    simulate_space_conditions,
    simulate_combined
)

from virtual_lab.data_analyzer import (
    load_dataset,
    get_dataset_overview,
    calculate_statistics,
    calculate_correlations,
    radiation_analysis
)


lab = Blueprint("lab", __name__)


# ---------------------------------------
# VIRTUAL LAB HOME
# ---------------------------------------

@lab.route("/virtual-lab")
@login_required
def home():
    return render_template("virtual_lab.html")


# ---------------------------------------
# SIMULATION API
# ---------------------------------------

@lab.route("/api/lab/simulate", methods=["POST"])
@login_required
def run_simulation():

    data = request.get_json(silent=True) or {}

    try:
        mode = data.get("mode")

        if mode == "cryptobiosis":
            result = simulate_cryptobiosis(
                data.get("humidity", 50),
                data.get("temperature", 20),
                data.get("state", "active")
            )

        elif mode == "space":
            result = simulate_space_conditions(
                data.get("radiation", 5),
                data.get("vacuum", 0.5),
                data.get("temperature", -50),
                data.get("microgravity", False)
            )

        elif mode == "combined":
            result = simulate_combined(
                data.get("humidity", 50),
                data.get("biological_temperature", 20),
                data.get("state", "tun"),
                data.get("radiation", 5),
                data.get("vacuum", 0.5),
                data.get("space_temperature", -50),
                data.get("microgravity", False)
            )

        else:
            return {"error": "Invalid experiment mode."}, 400

        return result

    except (TypeError, ValueError):
        return {
            "error": "Please enter valid experimental values."
        }, 400


# ---------------------------------------
# RESEARCH DATA ANALYZER - FILE UPLOAD
# ---------------------------------------

@lab.route("/virtual-lab/upload", methods=["POST"])
@login_required
def upload_dataset():

    uploaded_file = request.files.get("dataset")

    if not uploaded_file or not uploaded_file.filename:
        return render_template(
            "virtual_lab.html",
            analyzer_error="Please select a file to upload."
        )

    original_name = secure_filename(uploaded_file.filename)
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in [".csv", ".xlsx", ".xls"]:
        return render_template(
            "virtual_lab.html",
            analyzer_error="Only CSV and Excel files are supported."
        )

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    saved_filename = f"dataset_{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(upload_folder, saved_filename)

    try:
        uploaded_file.save(file_path)

        df = load_dataset(file_path)

        overview = get_dataset_overview(df)
        statistics = calculate_statistics(df)
        correlations = calculate_correlations(df)

        return render_template(
            "virtual_lab.html",
            dataset_name=original_name,
            dataset_file=saved_filename,
            columns=df.columns.tolist(),
            overview=overview,
            statistics=statistics,
            correlations=correlations,
            preview=df.head(10).to_dict(orient="records"),
            numeric_columns=overview["numeric_columns"]
        )

    except Exception as error:

        if os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception(
            "Dataset upload or analysis failed"
        )

        return render_template(
            "virtual_lab.html",
            analyzer_error=str(error)
        )


# ---------------------------------------
# RADIATION TOLERANCE ANALYSIS
# ---------------------------------------

@lab.route(
    "/virtual-lab/radiation-analysis",
    methods=["POST"]
)
@login_required
def analyze_radiation():

    saved_filename = request.form.get("dataset_file", "")
    dose_column = request.form.get("dose_column", "")
    survival_column = request.form.get("survival_column", "")

    # Validate uploaded dataset filename
    if (
        not saved_filename.startswith("dataset_")
        or os.path.basename(saved_filename) != saved_filename
        or os.path.splitext(saved_filename)[1].lower()
        not in [".csv", ".xlsx", ".xls"]
    ):
        return render_template(
            "virtual_lab.html",
            analyzer_error="Invalid dataset reference."
        )

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, saved_filename)

    if not os.path.isfile(file_path):
        return render_template(
            "virtual_lab.html",
            analyzer_error="Dataset not found. Please upload it again."
        )

    try:
        # Reload the uploaded dataset
        df = load_dataset(file_path)

        # General dataset analysis
        overview = get_dataset_overview(df)
        statistics = calculate_statistics(df)
        correlations = calculate_correlations(df)

        # Validate selected columns
        if dose_column not in df.columns:
            raise ValueError("Please select a valid radiation dose column.")

        if survival_column not in df.columns:
            raise ValueError("Please select a valid animal activity column.")

        # Perform radiation analysis
        result = radiation_analysis(
            df,
            dose_column,
            survival_column
        )

        # Return all dataset and radiation results to the template
        return render_template(
            "virtual_lab.html",

            dataset_name=saved_filename,
            dataset_file=saved_filename,

            columns=df.columns.tolist(),
            numeric_columns=overview["numeric_columns"],

            overview=overview,
            statistics=statistics,
            correlations=correlations,

            preview=df.head(10).to_dict(orient="records"),

            radiation_result=result,

            selected_dose=dose_column,
            selected_survival=survival_column,

            radiation_chart_labels=result["chart_labels"],
            radiation_chart_values=result["chart_values"]
        )

    except Exception as error:

        current_app.logger.exception(
            "Radiation analysis failed"
        )

        return render_template(
            "virtual_lab.html",
            analyzer_error=str(error)
        )
