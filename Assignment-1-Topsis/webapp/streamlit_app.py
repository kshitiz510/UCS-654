import base64
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="TOPSIS Studio", page_icon="📊", layout="wide")

BASE_DIR = Path(__file__).resolve().parent

# Initialize session state
if "result_df" not in st.session_state:
    st.session_state.result_df = None


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


def send_email(recipient_email: str, result_df: pd.DataFrame) -> tuple[bool, str]:
    """Send TOPSIS results via email with HTML formatting."""
    try:
        # Get email credentials from Streamlit secrets
        sender_email = st.secrets.get("EMAIL_USER")
        sender_password = st.secrets.get("EMAIL_PASSWORD")
        
        if not sender_email or not sender_password:
            return False, "❌ Email service not configured. Admin needs to set EMAIL_USER and EMAIL_PASSWORD in Streamlit Secrets."
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "📊 Your TOPSIS Analysis Results"
        
        # Get top alternative
        top_alt = result_df.iloc[result_df["Rank"].idxmin()]
        top_name = top_alt.iloc[0]
        top_score = top_alt['Topsis Score']
        
        # HTML email body with styling
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; border-radius: 8px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
                    .content {{ background: white; padding: 30px; }}
                    .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
                    .stat-box {{ background: #f0f4ff; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; }}
                    .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
                    .stat-value {{ font-size: 20px; font-weight: bold; color: #667eea; }}
                    .top-alternative {{ background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); padding: 20px; border-radius: 6px; margin: 20px 0; color: white; text-align: center; }}
                    .top-alternative h3 {{ margin: 0 0 10px 0; font-size: 14px; opacity: 0.9; }}
                    .top-alternative .name {{ font-size: 28px; font-weight: bold; margin: 10px 0; }}
                    .top-alternative .score {{ font-size: 16px; opacity: 0.95; }}
                    .table-section {{ margin-top: 25px; }}
                    .table-section h3 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                    th {{ background: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }}
                    td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
                    tr:hover {{ background: #f5f5f5; }}
                    .rank-1 {{ background: #ffd700; font-weight: bold; }}
                    .footer {{ background: #f0f4ff; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
                    .footer a {{ color: #667eea; text-decoration: none; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 TOPSIS Analysis Complete</h1>
                        <p>Your multi-criteria decision analysis results are ready</p>
                    </div>
                    
                    <div class="content">
                        <p>Hello,</p>
                        <p>Your TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) analysis has been completed successfully!</p>
                        
                        <div class="stats">
                            <div class="stat-box">
                                <div class="stat-label">Total Alternatives</div>
                                <div class="stat-value">{len(result_df)}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-label">Criteria Analyzed</div>
                                <div class="stat-value">{len(result_df.columns) - 3}</div>
                            </div>
                        </div>
                        
                        <div class="top-alternative">
                            <h3>🏆 Top Ranked Alternative</h3>
                            <div class="name">{top_name}</div>
                            <div class="score">TOPSIS Score: {top_score:.3f}</div>
                        </div>
                        
                        <div class="table-section">
                            <h3>Top 5 Rankings</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Rank</th>
                                        <th>Alternative</th>
                                        <th>TOPSIS Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {"".join([f'<tr><td class="rank-{int(row["Rank"])}" style="{"font-weight: bold; background: #fffacd;" if int(row["Rank"]) == 1 else ""}">{int(row["Rank"])}</td><td>{row.iloc[0]}</td><td>{row["Topsis Score"]:.3f}</td></tr>' for _, row in result_df.nsmallest(5, 'Rank').iterrows()])}
                                </tbody>
                            </table>
                        </div>
                        
                        <p style="margin-top: 25px; color: #666;">
                            The complete results with all alternatives and scores are attached as a CSV file for your records.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Generated by <strong>TOPSIS Studio</strong></p>
                        <p>For questions or support, contact your administrator.</p>
                        <p style="margin-top: 10px; font-size: 11px;">© 2026 TOPSIS Studio | All rights reserved</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach CSV
        csv_data = result_df.to_csv(index=False).encode('utf-8')
        attachment = MIMEApplication(csv_data, _subtype='csv')
        attachment.add_header('Content-Disposition', 'attachment', filename='topsis_results.csv')
        msg.attach(attachment)
        
        # Send email via Gmail SMTP with explicit error handling
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable TLS encryption
            server.login(sender_email, sender_password)  # Login with app password
            server.send_message(msg)
        
        return True, f"✅ Email sent successfully to {recipient_email}!"
    
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Authentication failed. Check EMAIL_USER and EMAIL_PASSWORD in Streamlit Secrets. Use Gmail App Password, not your regular password."
    except smtplib.SMTPException as e:
        return False, f"❌ SMTP error: {str(e)}"
    except Exception as e:
        return False, f"❌ Error sending email: {str(e)}"


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
        
        # Store in session state so it persists across reruns
        st.session_state.result_df = result_df
        
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

# Show email section if results exist in session state
if st.session_state.result_df is not None:
    with st.expander("📧 Email Results"):
        st.markdown("Send the analysis results directly to your email")
        user_email = st.text_input("Enter your email address", placeholder="example@email.com", key="email_input")
        
        if st.button("Send Email", type="secondary", key="send_btn"):
            if user_email and "@" in user_email and "." in user_email:
                with st.spinner("Sending email..."):
                    success, message = send_email(user_email, st.session_state.result_df)
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Please enter a valid email address")

elif prepared is not None:
    st.info("👈 Configure weights and impacts, then click 'Compute TOPSIS'")
    
    with st.expander("📋 Preview uploaded data"):
        st.dataframe(df, use_container_width=True, hide_index=True)
