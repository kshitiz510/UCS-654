import base64
import io
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="TOPSIS Studio", page_icon="📊", layout="wide")

BASE_DIR = Path(__file__).resolve().parent


def encode_categorical_column(df: pd.DataFrame, col: str) -> pd.Series:
    """Map common ordinal words; otherwise factorize categories."""
    unique_vals = df[col].unique()
    ordinal_mappings = {
        "low": 1, "medium": 2, "high": 3,
        "poor": 1, "average": 2, "good": 3, "excellent": 4,
        "bad": 1, "ok": 2, "great": 3,
        "small": 1, "large": 2,
        "yes": 1, "no": 0,
    }

    lowered = [str(v).lower() for v in unique_vals]
    if any(val in ordinal_mappings for val in lowered):
        mapping = {val: ordinal_mappings.get(str(val).lower(), 0) for val in unique_vals}
        return df[col].map(mapping)

    codes, _ = pd.factorize(df[col])
    return pd.Series(codes + 1, index=df.index)


def prepare_dataframe(df: pd.DataFrame):
    """Convert non-numeric columns to numeric."""
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
    """Parse and validate weights and impacts."""
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
    """Perform TOPSIS analysis."""
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


# Page header
st.markdown("### 📊 TOPSIS Studio")
st.markdown("**Multi-Criteria Decision Lab** — Upload CSV, set weights & impacts, see ranked alternatives.")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Configuration")
    
    use_sample = st.checkbox("Use sample data (test_data.csv)", value=False)
    
    if use_sample:
        sample_path = BASE_DIR.parent / "test_data.csv"
        if sample_path.exists():
            uploaded_file = sample_path
            df = pd.read_csv(sample_path)
        else:
            st.error("Sample dataset missing (test_data.csv)")
            uploaded_file = None
            df = None
    else:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"], help="First column: identifier, rest: criteria")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            df = None
    
    if df is not None:
        prepared, err = prepare_dataframe(df)
        if err:
            st.error(err)
            prepared = None
        else:
            criteria_count = len(prepared.columns) - 1
            st.success(f"✓ Loaded {len(prepared)} alternatives with {criteria_count} criteria")
            
            weights_input = st.text_input(
                "Weights", 
                value="1,1,1,1" if criteria_count == 4 else ",".join(["1"] * criteria_count),
                help="Comma-separated numbers, one per criterion"
            )
            
            impacts_input = st.text_input(
                "Impacts", 
                value="+,+,-,+" if criteria_count == 4 else ",".join(["+"] * criteria_count),
                help="'+' for benefit, '-' for cost"
            )
            
            compute = st.button("🚀 Compute TOPSIS", type="primary", use_container_width=True)
    else:
        prepared = None
        compute = False

# Main content area
if df is None:
    st.info("👈 Upload a CSV file or toggle 'Use sample data' to get started.")
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Normalization** – Scale criteria to comparable range
        2. **Weighted Normalization** – Apply importance weights
        3. **Ideal & Anti-Ideal Solutions** – Determine best/worst values
        4. **Separation Measures** – Calculate distances
        5. **TOPSIS Score** – Compute relative closeness (0–1)
        6. **Ranking** – Sort alternatives by score
        
        **Input Format:**
        - First column: Alternative names/IDs
        - Remaining columns: Numeric criteria
        - Weights: comma-separated numbers
        - Impacts: '+' (benefit) or '-' (cost)
        """)

elif prepared is not None and compute:
    weights, impacts, err = parse_weights_impacts(weights_input, impacts_input, criteria_count)
    
    if err:
        st.error(f"❌ {err}")
    else:
        scores, ranks = topsis(prepared, weights, impacts)
        result_df = prepared.copy()
        result_df["Topsis Score"] = np.round(scores, 3)
        result_df["Rank"] = ranks
        
        st.success("✅ TOPSIS computation complete!")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Ranking Results")
        with col2:
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="topsis_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        
        # Quick insights
        top_alt = result_df.iloc[result_df["Rank"].idxmin()]
        st.metric(
            label=f"🏆 Top Alternative",
            value=top_alt.iloc[0],
            delta=f"Score: {top_alt['Topsis Score']}"
        )

elif prepared is not None:
    st.info("👈 Configure weights and impacts, then click 'Compute TOPSIS'")
    
    with st.expander("📋 Preview uploaded data"):
        st.dataframe(df, use_container_width=True, hide_index=True)
