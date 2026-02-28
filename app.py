import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# ── MUST be first ────────────────────────────────────────────────
st.set_page_config(page_title="GridSense AI", layout="wide",
                   page_icon="⚡", initial_sidebar_state="auto")

if "dark_mode"      not in st.session_state: st.session_state.dark_mode = True
if "chat_history"   not in st.session_state: st.session_state.chat_history = []

from theme import (inject_theme, topbar, kpi_row, section_divider,
                   sidebar_brand, plotly_dark_layout, render_alert_row,
                   theme_toggle, chart_title, info_banner)
inject_theme()

from giip_page      import show_giip_page
from data_generator import generate_grid_data
from ml_models      import prepare_data
from gemini_engine  import get_feeder_recommendation, get_state_strategy, ask_gridsense

# ── Data ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:    df = pd.read_csv('grid_data.csv')
    except: df = generate_grid_data()
    return prepare_data(df)

df = load_data()

ctx = {
    'avg_loss':        df['loss_percentage'].mean(),
    'suspicious_count':int(df['is_suspicious'].sum()),
    'high_risk_count': int((df['risk_label'] == 'HIGH').sum()),
    'worst_state':     df.groupby('state')['loss_percentage'].mean().idxmax(),
    'best_state':      df.groupby('state')['loss_percentage'].mean().idxmin(),
    'revenue_loss':    round(df['loss_percentage'].mean() * 847 / 18, 0),
    'total_readings':  len(df),
    'last_updated':    datetime.now().strftime("%H:%M:%S"),
}

def col_name(candidates, df):
    for c in candidates:
        if c in df.columns: return c
    return None

# ── Sidebar ───────────────────────────────────────────────────────
sidebar_brand(total_readings=len(df), data_source="CSV")

# Navigation — clean dict mapping avoids icon/space matching bugs
PAGES = {
    "🏠 Dashboard":          "Dashboard",
    "🚨 Anomaly Detection":  "Anomaly",
    "🔧 Asset Risk":         "Risk",
    "🤖 AI Recommendations": "AI",
    "🏛️ GIIP Framework":     "GIIP",
    "💬 Ask GridSense AI":   "Chat",
}
page = PAGES[st.sidebar.radio("", list(PAGES.keys()), label_visibility="collapsed")]

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="padding:0 4px 4px">
  <div style="font-size:0.67rem;color:var(--text-muted);font-family:var(--font-mono);
              text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">System</div>
  <div class="status-row status-ok" style="margin-bottom:6px"><div class="status-dot"></div>ML models active</div>
  <div class="status-row status-ok" style="margin-bottom:6px"><div class="status-dot"></div>Gemini AI ready</div>
  <div class="status-row status-ok" style="margin-bottom:6px"><div class="status-dot"></div>{len(df):,} records loaded</div>
</div>""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

theme_toggle()

st.sidebar.markdown(f"""
<div style="font-family:var(--font-mono);font-size:0.64rem;color:var(--text-muted);padding:4px 0">
  Updated {datetime.now().strftime('%H:%M:%S')}
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ════════════════════════════════════════════════════════════════
if page == "Dashboard":
    topbar("Dashboard", "GridSense AI  /  Overview")

    kpi_row([
        {"label":"Avg T&D Loss",      "value":f"{df['loss_percentage'].mean():.1f}%",
         "delta":"↑ Target: 2%",         "color":"red",    "icon":"📉"},
        {"label":"Theft Suspects",    "value":str(int(df['is_suspicious'].sum())),
         "delta":"ML flagged",            "color":"orange", "icon":"🚨"},
        {"label":"High-Risk Assets",  "value":str(int((df['risk_label']=='HIGH').sum())),
         "delta":"Replace / maintain",    "color":"purple", "icon":"⚠️"},
        {"label":"Revenue Lost / yr", "value":f"₹{ctx['revenue_loss']:.0f}Cr",
         "delta":"Recoverable with GIIP", "color":"green",  "icon":"💰"},
        {"label":"Worst State",       "value":ctx['worst_state'],
         "delta":"Highest avg loss",      "color":"cyan",   "icon":"📍"},
    ])

    section_divider("Regional Analysis")
    col1, col2 = st.columns(2)

    with col1:
        # ── Title then chart in same column — no wrapping div needed ──
        chart_title("State-wise Average Loss %", "LIVE", "badge-live")
        state_data = (df.groupby('state')['loss_percentage']
                        .mean().reset_index()
                        .sort_values('loss_percentage', ascending=False))
        fig = px.bar(state_data, x='state', y='loss_percentage',
                     color='loss_percentage',
                     color_continuous_scale=["#00C87A","#F0B429","#E8304A"],
                     labels={"loss_percentage":"Loss %","state":""})
        fig.add_hline(y=2, line_dash="dash", line_color="#00C87A",
                      annotation_text="2030 Target", annotation_font_color="#00C87A")
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-25)
        plotly_dark_layout(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_title("National Loss Trend")
        date_col = col_name(['date'], df)
        if date_col:
            daily = df.groupby(date_col)['loss_percentage'].mean().reset_index()
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=daily[date_col], y=daily['loss_percentage'],
                mode='lines', fill='tozeroy',
                line=dict(color='#0099E6', width=2.5),
                fillcolor='rgba(0,153,230,0.08)'))
            fig2.add_hline(y=2, line_dash="dash", line_color="#00C87A",
                           annotation_text="Target", annotation_font_color="#00C87A")
        else:
            fig2 = px.histogram(df, x='loss_percentage', nbins=30,
                                color_discrete_sequence=['#0099E6'],
                                labels={"loss_percentage":"Loss %"})
            fig2.add_vline(x=2, line_dash="dash", line_color="#00C87A")
        plotly_dark_layout(fig2, 320)
        st.plotly_chart(fig2, use_container_width=True)

    section_divider("Coverage & Distribution")
    col3, col4 = st.columns(2)

    with col3:
        meter_col = col_name(['smart_meter_installed','smart_meter'], df)
        if meter_col:
            md = df[meter_col].value_counts().reset_index()
            md.columns = ['Installed','Count']
            md['Installed'] = md['Installed'].map(
                {True:'Smart Meter ✅', False:'No Smart Meter ❌',
                 1:'Smart Meter ✅',    0:'No Smart Meter ❌'})
            chart_title("Smart Meter Coverage")
            fig3 = px.pie(md, values='Count', names='Installed', color='Installed',
                          color_discrete_map={
                              'Smart Meter ✅':'#00C87A',
                              'No Smart Meter ❌':'#E8304A'}, hole=0.52)
            fig3.update_traces(textfont_color='#E8F0F8')
            plotly_dark_layout(fig3, 260)
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        chart_title("Loss % Distribution")
        fig4 = px.histogram(df, x='loss_percentage', nbins=30,
                            color_discrete_sequence=['#7B5EA7'],
                            labels={"loss_percentage":"Loss %"})
        fig4.add_vline(x=2, line_dash="dash", line_color="#00C87A",
                       annotation_text="2% Target", annotation_font_color="#00C87A")
        plotly_dark_layout(fig4, 260)
        st.plotly_chart(fig4, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE: Anomaly Detection
# ════════════════════════════════════════════════════════════════
elif page == "Anomaly":
    topbar("Anomaly Detection", "GridSense AI  /  Theft & Anomaly")
    info_banner("🤖 <strong>Isolation Forest</strong> ML model flags feeders with suspicious consumption patterns indicating possible theft or meter tampering.", "cyan")

    kpi_row([
        {"label":"Suspicious Feeders",
         "value":str(int(df['is_suspicious'].sum())),
         "delta":"ML flagged","color":"red","icon":"🚨"},
        {"label":"Normal Feeders",
         "value":str(int((~df['is_suspicious']).sum())),
         "delta":"Clean","color":"green","icon":"✅"},
        {"label":"Avg Loss (Suspicious)",
         "value":(f"{df[df['is_suspicious']]['loss_percentage'].mean():.1f}%"
                  if df['is_suspicious'].any() else "N/A"),
         "delta":"vs national avg","color":"orange","icon":"📊"},
        {"label":"Detection Model",
         "value":"IF","delta":"Isolation Forest","color":"cyan","icon":"🤖"},
    ])

    section_divider("Detection Scatter Plots")
    inj_col = col_name(['units_injected_kwh','units_injected'], df)
    age_col = col_name(['transformer_age_years','transformer_age'], df)
    col1, col2 = st.columns(2)

    with col1:
        if inj_col:
            chart_title("🔴 Red = Suspicious Feeders", "ML", "badge-ml")
            fig = px.scatter(df, x=inj_col, y='loss_percentage',
                             color='is_suspicious',
                             color_discrete_map={True:'#E8304A', False:'#00C87A'},
                             hover_data=['feeder_id','state'],
                             labels={inj_col:"Units Injected (kWh)",
                                     "loss_percentage":"Loss %",
                                     "is_suspicious":"Suspicious"})
            plotly_dark_layout(fig, 300)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if age_col and 'voltage_fluctuation' in df.columns:
            chart_title("Age vs Voltage Fluctuation")
            fig2 = px.scatter(df, x=age_col, y='voltage_fluctuation',
                              color='is_suspicious',
                              color_discrete_map={True:'#E8304A', False:'#00C87A'},
                              hover_data=['feeder_id','state'],
                              labels={age_col:"Transformer Age (yrs)",
                                      "voltage_fluctuation":"Voltage Fluctuation %"})
            plotly_dark_layout(fig2, 300)
            st.plotly_chart(fig2, use_container_width=True)

    section_divider("Suspicious Feeder List")
    base = ['feeder_id','state','loss_percentage']
    extra = [c for c in ['transformer_age_years','transformer_age',
                          'smart_meter_installed','smart_meter',
                          'voltage_fluctuation','risk_label'] if c in df.columns]
    susp_df = df[df['is_suspicious']][base+extra].sort_values('loss_percentage', ascending=False)
    st.dataframe(susp_df.head(20), use_container_width=True, hide_index=True)
    st.download_button("📥 Download Suspicious Feeders Report",
                       susp_df.to_csv(index=False), "suspicious_feeders.csv",
                       use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE: Asset Risk
# ════════════════════════════════════════════════════════════════
elif page == "Risk":
    topbar("Asset Risk", "GridSense AI  /  Predictive Maintenance")
    info_banner("🔧 <strong>Random Forest</strong> predicts transformer & line failure risk based on age, load factor, temperature, and historical outage patterns.", "purple")

    age_col = col_name(['transformer_age_years','transformer_age'], df)
    avg_age = f"{df[age_col].mean():.0f} yr" if age_col else "N/A"

    kpi_row([
        {"label":"High Risk",
         "value":str(int((df['risk_label']=='HIGH').sum())),
         "delta":"Replace soon","color":"red","icon":"🔴"},
        {"label":"Medium Risk",
         "value":str(int((df['risk_label']=='MEDIUM').sum())),
         "delta":"Monitor","color":"orange","icon":"🟠"},
        {"label":"Low Risk",
         "value":str(int((df['risk_label']=='LOW').sum())),
         "delta":"Healthy","color":"green","icon":"🟢"},
        {"label":"Avg Transformer Age",
         "value":avg_age,"delta":"Years in service","color":"cyan","icon":"🕐"},
    ])

    section_divider("Risk Charts")
    col1, col2 = st.columns(2)

    with col1:
        chart_title("Asset Risk Distribution")
        rc = df['risk_label'].value_counts().reset_index()
        rc.columns = ['Risk Level','Count']
        fig = px.pie(rc, values='Count', names='Risk Level', color='Risk Level',
                     color_discrete_map={'HIGH':'#E8304A','MEDIUM':'#FF8C42','LOW':'#00C87A'},
                     hole=0.55)
        fig.update_traces(textfont_color='#E8F0F8')
        plotly_dark_layout(fig, 280)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if age_col and 'failure_risk_score' in df.columns:
            chart_title("Transformer Age vs Failure Risk")
            fig2 = px.scatter(df, x=age_col, y='failure_risk_score',
                              color='risk_label',
                              color_discrete_map={
                                  'HIGH':'#E8304A','MEDIUM':'#FF8C42','LOW':'#00C87A'},
                              hover_data=['feeder_id','state'],
                              labels={age_col:"Age (yrs)","failure_risk_score":"Risk Score"})
            plotly_dark_layout(fig2, 280)
            st.plotly_chart(fig2, use_container_width=True)

    section_divider("High Risk Assets — Replace / Maintain Immediately")
    risk_cols = [c for c in ['feeder_id','state','transformer_age_years','transformer_age',
                              'failure_risk_score','loss_percentage',
                              'outage_hours_monthly','outage_hours'] if c in df.columns]
    hr = df[df['risk_label']=='HIGH'][risk_cols].sort_values('failure_risk_score', ascending=False)
    st.dataframe(hr.head(20), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
# PAGE: AI Recommendations
# ════════════════════════════════════════════════════════════════
elif page == "AI":
    topbar("AI Recommendations", "GridSense AI  /  Gemini AI Analysis")
    tab1, tab2 = st.tabs(["🔍  Feeder Analysis", "📋  State Strategy"])

    with tab1:
        st.markdown("#### Select a feeder for deep AI analysis")
        options = df[df['is_suspicious']]['feeder_id'].unique()[:30]
        selected = st.selectbox("Choose suspicious feeder:", options)
        if st.button("🔍 Analyse with Gemini AI", type="primary"):
            row = df[df['feeder_id']==selected].iloc[0].to_dict()
            with st.spinner("Gemini is analysing..."):
                result = get_feeder_recommendation(row)
            st.success("✅ Analysis Complete!")
            st.markdown(result)

    with tab2:
        st.markdown("#### Generate state-level 2030 strategy")
        states = df['state'].unique().tolist()
        sel_state = st.selectbox("Choose State:", states)
        if st.button("📋 Generate State Strategy"):
            sdf = df[df['state']==sel_state]
            with st.spinner(f"Building strategy for {sel_state}..."):
                strategy = get_state_strategy(
                    sel_state, sdf['loss_percentage'].mean(),
                    int(sdf['is_suspicious'].sum()),
                    int((sdf['risk_label']=='HIGH').sum()))
            st.success("✅ Strategy Ready!")
            st.markdown(strategy)


# ════════════════════════════════════════════════════════════════
# PAGE: GIIP Framework
# ════════════════════════════════════════════════════════════════
elif page == "GIIP":
    show_giip_page()


# ════════════════════════════════════════════════════════════════
# PAGE: Chat
# ════════════════════════════════════════════════════════════════
elif page == "Chat":
    topbar("Ask GridSense AI", "GridSense AI  /  AI Assistant")

    starters = [
        "Which state should we prioritize first?",
        "What is the main cause of losses right now?",
        "How much revenue can we recover this year?",
        "Which feeders need immediate field inspection?",
        "Suggest top 3 policy interventions for India",
        "What is the risk level of transformer assets?",
    ]
    st.markdown("**Quick questions — click to ask:**")
    qc = st.columns(3)
    for i, q in enumerate(starters):
        if qc[i % 3].button(q, key=f"qs_{i}"):
            st.session_state.chat_history.append({"role":"user","content":q})

    st.markdown("---")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask anything about grid losses, strategies, states...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_gridsense(user_input, ctx)
            st.markdown(response)
            st.session_state.chat_history.append({"role":"assistant","content":response})

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()