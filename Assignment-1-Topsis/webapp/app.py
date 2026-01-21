from pathlib import Path
import os
import base64
import io

import numpy as np
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent


def encode_categorical_column(df: pd.DataFrame, col: str) -> pd.Series:
    """Map common ordinal words; otherwise factorize categories."""
    unique_vals = df[col].unique()
    ordinal_mappings = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "poor": 1,
        "average": 2,
        "good": 3,
        "excellent": 4,
        "bad": 1,
        "ok": 2,
        "great": 3,
        "small": 1,
        "large": 2,
        "yes": 1,
        "no": 0,
    }

    lowered = [str(v).lower() for v in unique_vals]
    if any(val in ordinal_mappings for val in lowered):
        mapping = {val: ordinal_mappings.get(str(val).lower(), 0) for val in unique_vals}
        return df[col].map(mapping)

    codes, _ = pd.factorize(df[col])
    return pd.Series(codes + 1, index=df.index)


def prepare_dataframe(df: pd.DataFrame):
    if len(df.columns) < 3:
        return None, "Input needs at least one identifier column and two criteria columns."

    working = df.copy()
    for col in working.columns[1:]:
        if not pd.api.types.is_numeric_dtype(working[col]):
            try:
                working[col] = pd.to_numeric(working[col])
            except Exception:
                try:
                    working[col] = encode_categorical_column(working, col)
                except Exception:
                    return None, f"Column '{col}' cannot be converted to numeric."
    return working, None


def parse_weights_impacts(weights_raw: str, impacts_raw: str, criteria_count: int):
    try:
        weights = [float(w.strip()) for w in weights_raw.split(",") if w.strip() != ""]
    except Exception:
        return None, None, "Weights must be numeric values separated by commas."

    try:
        impacts = [i.strip() for i in impacts_raw.split(",") if i.strip() != ""]
    except Exception:
        return None, None, "Impacts must be '+' or '-' separated by commas."

    if criteria_count <= 0:
        return None, None, "No criteria columns found."

    if len(weights) != criteria_count or len(impacts) != criteria_count:
        return None, None, f"Provide {criteria_count} weights and impacts."

    if not all(i in ["+", "-"] for i in impacts):
        return None, None, "Impacts must be '+' for benefit and '-' for cost criteria."

    return weights, impacts, None


def topsis(df: pd.DataFrame, weights, impacts):
    data = df.iloc[:, 1:].to_numpy(dtype=float)
    norms = np.sqrt((data ** 2).sum(axis=0))
    normalized = data / norms
    weighted = normalized * np.array(weights)

    impacts_arr = np.array(impacts)
    ideal_best = np.where(impacts_arr == "+", weighted.max(axis=0), weighted.min(axis=0))
    ideal_worst = np.where(impacts_arr == "+", weighted.min(axis=0), weighted.max(axis=0))

    dist_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    scores = dist_worst / (dist_best + dist_worst)
    ranks = scores.argsort()[::-1].argsort() + 1
    return scores, ranks


def dataframe_to_download(df: pd.DataFrame) -> str:
    csv_bytes = df.to_csv(index=False).encode()
    return base64.b64encode(csv_bytes).decode()


@app.route("/", methods=["GET", "POST"])
def index():
    errors = []
    result_html = None
    download_token = None
    suggested = {
        "weights": "1,1,1,1",
        "impacts": "+,+,-,+",
    }

    user_weights = ""
    user_impacts = ""

    if request.method == "POST":
        use_sample = request.form.get("use_sample") == "on"
        user_weights = request.form.get("weights", "")
        user_impacts = request.form.get("impacts", "")

        df = None
        if use_sample:
            sample_path = BASE_DIR.parent / "test_data.csv"
            if not sample_path.exists():
                errors.append("Sample dataset is missing (test_data.csv).")
            else:
                df = pd.read_csv(sample_path)
        else:
            uploaded = request.files.get("data_file")
            if uploaded and uploaded.filename:
                try:
                    df = pd.read_csv(io.BytesIO(uploaded.read()))
                except Exception:
                    errors.append("Could not read the uploaded CSV file.")
            else:
                errors.append("Upload a CSV file or toggle 'Use sample data'.")

        if df is not None:
            prepared, err = prepare_dataframe(df)
            if err:
                errors.append(err)
            else:
                criteria_count = len(prepared.columns) - 1
                weights, impacts, err = parse_weights_impacts(user_weights, user_impacts, criteria_count)
                if err:
                    errors.append(err)
                else:
                    scores, ranks = topsis(prepared, weights, impacts)
                    prepared["Topsis Score"] = np.round(scores, 3)
                    prepared["Rank"] = ranks
                    result_html = prepared.to_html(classes="result-table", index=False)
                    download_token = dataframe_to_download(prepared)
    return render_template(
        "index.html",
        errors=errors,
        result_html=result_html,
        download_token=download_token,
        suggested=suggested,
        user_weights=user_weights,
        user_impacts=user_impacts,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
