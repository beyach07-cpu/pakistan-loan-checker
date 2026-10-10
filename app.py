import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ---------------------------------------------------------
# Page Configuration & Global Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="PakFinance | Islamic vs Conventional Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern, Executive UI/UX
st.markdown("""
<style>
    /* Global Typography & Background adjustments */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Card Container */
    .finance-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Metric Callout Badges */
    .metric-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-success { background-color: #d1fae5; color: #065f46; }
    .badge-warning { background-color: #fef3c7; color: #92400e; }
    .badge-danger { background-color: #fee2e2; color: #991b1b; }

    /* Custom Header Subtitle */
    .sub-heading {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: -12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation & Quick Presets
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏛️ **PakFinance Portal**")
    st.caption("State Bank Prudential & Shariah Benchmarking")
    st.markdown("---")
    
    page = st.radio(
        "Navigation Menu",
        [
            "📊 Eligibility & Comparison",
            "🏢 Bank Directory & Products",
            "📅 Amortization Matrix",
            "📖 Shariah vs Conventional Guide"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("#### ⚡ Quick Presets")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🚗 Auto (Car)", use_container_width=True):
            st.session_state["preset_price"] = 3500000
            st.session_state["preset_down"] = 30
            st.session_state["preset_tenure"] = 3
    with col_p2:
        if st.button("🏠 Home Fin.", use_container_width=True):
            st.session_state["preset_price"] = 12000000
            st.session_state["preset_down"] = 25
            st.session_state["preset_tenure"] = 7

    st.markdown("---")
    st.caption("All figures follow prevailing SBP Consumer Financing DBR thresholds (40%–50% net income cap).")

# Default values handler
if "preset_price" not in st.session_state:
    st.session_state["preset_price"] = 2500000
if "preset_down" not in st.session_state:
    st.session_state["preset_down"] = 20
if "preset_tenure" not in st.session_state:
    st.session_state["preset_tenure"] = 3

# ==============================================================================
# PAGE 1: ELIGIBILITY & COMPARISON DASHBOARD
# ==============================================================================
if page == "📊 Eligibility & Comparison":
    st.title("Loan Eligibility & Financing Assessment")
    st.markdown('<p class="sub-heading">Evaluate Debt-Burden Ratio (DBR) and compare Islamic Ijarah/Musharakah against conventional borrowing.</p>', unsafe_allow_html=True)

    col_inputs, col_visuals = st.columns([1, 1], gap="large")

    with col_inputs:
        with st.container():
            st.markdown("#### 1. Applicant Background")
            monthly_income = st.slider("Monthly Net Income (PKR)", 30000, 1500000, 120000, step=10000, format="PKR %d")
            
            c_app1, c_app2 = st.columns(2)
            with c_app1:
                age = st.number_input("Age (Years)", 18, 65, 30)
                job_type = st.selectbox(
                    "Employment Status",
                    ["Permanent Private Job", "Government Service", "Business Owner", "Contractual / Freelance"]
                )
            with c_app2:
                credit_status = st.selectbox(
                    "e-CIB Track Record",
                    ["Clean / Excellent", "Satisfactory / Good", "Average", "Overdue / Poor"]
                )
                facility_purpose = st.selectbox(
                    "Purpose",
                    ["Car Financing (Ijarah)", "Housing Facility", "Personal Loan", "SME / Commercial"]
                )

        with st.container():
            st.markdown("#### 2. Financing Structure")
            asset_val = st.number_input(
                "Total Asset Cost / Price (PKR)",
                min_value=200000,
                value=st.session_state["preset_price"],
                step=100000
            )
            down_pct = st.slider(
                "Down Payment / Advance Equity (%)",
                min_value=5,
                max_value=80,
                value=st.session_state["preset_down"],
                step=5
            )
            
            equity_val = asset_val * (down_pct / 100)
            net_borrowing = asset_val - equity_val
            tenure = st.slider("Facility Tenure (Years)", 1, 7, st.session_state["preset_tenure"], step=1)

            st.markdown(
                f"""
                <div style="background-color: #f1f5f9; padding: 10px 16px; border-radius: 8px; font-size: 0.9rem;">
                    <b>Down Payment:</b> PKR {equity_val:,.0f} &nbsp;|&nbsp; 
                    <b>Net Loan Capital:</b> PKR {net_borrowing:,.0f}
                </div>
                """,
                unsafe_allow_html=True
            )

    # -----------------------------
    # Logic Engine
    # -----------------------------
    score = 0
    if monthly_income >= 120000:
        score += 30
    elif monthly_income >= 60000:
        score += 20
    elif monthly_income >= 35000:
        score += 10

    score += 20 if 25 <= age <= 50 else 10
    
    job_scores = {
        "Government Service": 25,
        "Permanent Private Job": 20,
        "Business Owner": 15,
        "Contractual / Freelance": 5
    }
    score += job_scores.get(job_type, 0)

    cred_scores = {
        "Clean / Excellent": 25,
        "Satisfactory / Good": 15,
        "Average": 10,
        "Overdue / Poor": 0
    }
    score += cred_scores.get(credit_status, 0)
    score = min(score, 96)

    # Pricing Models (Indicative Benchmark spreads)
    islamic_annual_rate = 0.205
    conv_annual_rate = 0.235
    total_months = tenure * 12

    islamic_total_markup = net_borrowing * islamic_annual_rate * tenure
    conv_total_interest = net_borrowing * conv_annual_rate * tenure

    islamic_emi = (net_borrowing + islamic_total_markup) / total_months
    conv_emi = (net_borrowing + conv_total_interest) / total_months

    dbr_pct = (islamic_emi / monthly_income) * 100

    # -----------------------------
    # Outputs Section
    # -----------------------------
    with col_visuals:
        st.markdown("#### 3. Real-Time Eligibility & Metrics")

        # Top Metric Cards
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Eligibility Score", f"{score}/100")
        with m2:
            st.metric("Debt-Burden (DBR)", f"{dbr_pct:.1f}%")
        with m3:
            monthly_delta = conv_emi - islamic_emi
            st.metric("Est. Monthly Saving", f"PKR {monthly_delta:,.0f}")

        # Status Banner
        if score >= 70 and dbr_pct <= 45:
            st.markdown('<span class="metric-badge badge-success">✓ ELIGIBLE (High Probability of Approval)</span>', unsafe_allow_html=True)
            st.success("Your financial indicators satisfy the State Bank of Pakistan Consumer DBR threshold (under 45%).")
        elif score >= 50 or dbr_pct <= 50:
            st.markdown('<span class="metric-badge badge-warning">⚠ BORDERLINE (Conditional Approval Expected)</span>', unsafe_allow_html=True)
            st.warning("Acceptable score, but DBR is approaching the regulatory limit. Consider increasing your down payment.")
        else:
            st.markdown('<span class="metric-badge badge-danger">✕ LOW APPROVAL PROBABILITY</span>', unsafe_allow_html=True)
            st.error("Monthly installment exceeds debt-capacity standards. Extending tenure or lowering facility size is advised.")

        # Interactive Gauge
        fig_score = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 28}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0ea5e9"},
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#d1fae5"}
                ],
                "threshold": {"line": {"color": "#0284c7", "width": 4}, "thickness": 0.8, "value": score}
            }
        ))
        fig_score.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_score, use_container_width=True)

        # Tabbed Output
        tab_table, tab_chart = st.tabs(["📋 Installment Comparison", "📊 Cost Breakdown Chart"])
        
        with tab_table:
            summary_table = pd.DataFrame({
                "Parameter": ["Monthly Installment (Qist)", "Financed Principal", "Total Cost / Markup", "Total Outflow"],
                "Islamic Structure": [f"PKR {islamic_emi:,.0f}", f"PKR {net_borrowing:,.0f}", f"PKR {islamic_total_markup:,.0f}", f"PKR {(net_borrowing + islamic_total_markup):,.0f}"],
                "Conventional Loan": [f"PKR {conv_emi:,.0f}", f"PKR {net_borrowing:,.0f}", f"PKR {conv_total_interest:,.0f}", f"PKR {(net_borrowing + conv_total_interest):,.0f}"]
            })
            st.dataframe(summary_table, hide_index=True, use_container_width=True)

        with tab_chart:
            fig_bar = go.Figure(data=[
                go.Bar(name='Principal', x=['Islamic', 'Conventional'], y=[net_borrowing, net_borrowing], marker_color='#0284c7'),
                go.Bar(name='Markup / Interest', x=['Islamic', 'Conventional'], y=[islamic_total_markup, conv_total_interest], marker_color='#94a3b8')
            ])
            fig_bar.update_layout(barmode='stack', height=240, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

# ==============================================================================
# PAGE 2: BANK DIRECTORY & PRODUCTS
# ==============================================================================
elif page == "🏢 Bank Directory & Products":
    st.title("Pakistani Banking Institutions & Product Matrix")
    st.markdown('<p class="sub-heading">Compare dedicated Islamic windows against leading conventional scheduled banks.</p>', unsafe_allow_html=True)

    t_islamic, t_conv, t_docs = st.tabs(["🌙 Islamic Institutions", "🏢 Conventional Banks", "📑 Mandatory Documentation"])

    with t_islamic:
        st.markdown("#### Primary Islamic Banks")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            **Meezan Bank Limited**
            - **Auto Scheme:** Car Ijarah (Ownership transfer upon lease conclusion)
            - **Home Finance:** Easy Home (Diminishing Musharakah)
            - **Charity Fund:** Delinquency fines routed exclusively to audited charity accounts.
            """)
        with c2:
            st.markdown("""
            **BankIslami Pakistan Limited**
            - **Auto Scheme:** Auto Ijarah
            - **Home Finance:** Muskun Home Financing
            - **Shariah Governance:** Dual Shariah Supervisory Board oversight.
            """)

    with t_conv:
        st.markdown("#### Leading Commercial Institutions")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""
            **Habib Bank Limited (HBL)**
            - **Auto Loan:** Fixed and floating KIBOR-linked auto installment plans.
            - **Home Loan:** HBL GharAasani.
            """)
        with c4:
            st.markdown("""
            **United Bank Limited (UBL)**
            - **Auto Loan:** UBL Drive (Flexible balloon payment options).
            - **Consumer Loans:** CashLine revolving facilities.
            """)

    with t_docs:
        st.markdown("#### SBP Regulatory Checklist")
        st.info("Ensure all files are attested before applying to expedite e-CIB verification.")
        st.markdown("""
        * **Salaried Personnel:** CNIC copy, original salary slips (last 3 months), 6-month certified bank statement, employment letter.
        * **Business / Self-Employed:** Valid NTN Certificate, verified Tax Returns (last 2 years), active bank statement (12 months), company registration proof.
        """)

# ==============================================================================
# PAGE 3: AMORTIZATION MATRIX
# ==============================================================================
elif page == "📅 Amortization Matrix":
    st.title("Interactive Repayment Schedule")
    st.markdown('<p class="sub-heading">View how balance reduction and interest/markup distributions evolve over the selected facility lifespan.</p>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        p_amount = st.number_input("Capital Amount (PKR)", value=1500000, step=50000)
    with f2:
        p_years = st.slider("Repayment Years", 1, 10, 3)
    with f3:
        p_rate = st.slider("Indicative Annual Flat Markup (%)", 12.0, 32.0, 21.0, step=0.5)

    p_annual_markup = p_amount * (p_rate / 100)
    p_annual_principal = p_amount / p_years
    total_installment_annual = p_annual_principal + p_annual_markup

    balance = p_amount
    data = []

    for yr in range(1, p_years + 1):
        prev_balance = balance
        balance -= p_annual_principal
        data.append({
            "Year": f"Year {yr}",
            "Opening Capital (PKR)": f"{prev_balance:,.0f}",
            "Principal Settled (PKR)": f"{p_annual_principal:,.0f}",
            "Markup Incurred (PKR)": f"{p_annual_markup:,.0f}",
            "Total Annual Outflow (PKR)": f"{total_installment_annual:,.0f}",
            "Outstanding Capital (PKR)": f"{max(0, balance):,.0f}"
        })

    df_schedule = pd.DataFrame(data)
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)

    csv_export = df_schedule.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Amortization Schedule (CSV)",
        data=csv_export,
        file_name="pakistan_repayment_schedule.csv",
        mime="text/csv"
    )

# ==============================================================================
# PAGE 4: SHARIAH VS CONVENTIONAL GUIDE
# ==============================================================================
elif page == "📖 Shariah vs Conventional Guide":
    st.title("Conceptual & Regulatory Differences")
    st.markdown('<p class="sub-heading">Understanding underlying mechanisms, risk distribution, and legal structures.</p>', unsafe_allow_html=True)

    col_sh1, col_sh2 = st.columns(2)

    with col_sh1:
        st.markdown("""
        <div class="finance-card">
            <h4>🌙 Islamic Banking Architecture</h4>
            <ul>
                <li><b>Asset Backed:</b> Currency cannot generate earnings on itself. Funding is tied to tangible underlying assets.</li>
                <li><b>No Compounding Interest (Riba):</b> Delinquent repayments incur predefined late fees routed directly to charitable funds.</li>
                <li><b>Equitable Risk-Sharing:</b> Bank retains asset risk until complete transfer of legal title.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_sh2:
        st.markdown("""
        <div class="finance-card">
            <h4>🏢 Conventional Banking Architecture</h4>
            <ul>
                <li><b>Lender-Borrower Setup:</b> Money operates as a commodity rented out for a markup rate.</li>
                <li><b>Compounding Penalties:</b> Payment defaults accumulate interest-on-interest, adding to the principal liability.</li>
                <li><b>Pure Financial Risk Transfer:</b> Risk is transferred directly to the borrower upon capital disbursement.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Key Islamic Financial Modes Explained")
    st.markdown("""
    | Model | Contract Type | Practical Banking Application |
    | :--- | :--- | :--- |
    | **Ijarah** | Rental / Usufruct Transfer | Automobile procurement (Bank owns vehicle; customer pays rental units) |
    | **Diminishing Musharakah** | Declining Partnership | Home financing (Bank & customer co-own property; customer buys bank shares) |
    | **Murabaha** | Cost-Plus Sale | Corporate inventory, raw material, and equipment purchases |
    """)