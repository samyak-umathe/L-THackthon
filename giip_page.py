import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime

GIIP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&family=DM+Sans:ital,wght@0,400;0,500;1,400&display=swap');
* { box-sizing: border-box; }
.giip-badge {
    display: inline-block; background: #7B5EA7; color: white;
    font-family: 'Space Grotesk', sans-serif; font-size: 11px;
    font-weight: 700; letter-spacing: 2px; padding: 6px 16px;
    border-radius: 4px; margin-bottom: 12px;
}
.giip-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 800; color: #0D1B2A; margin: 0 0 6px 0; }
.giip-subtitle { font-size: 1rem; color: #5A6072; font-style: italic; margin-bottom: 24px; }
.step-header { display: flex; align-items: center; gap: 14px; padding: 14px 20px; border-radius: 8px 8px 0 0; margin-bottom: 0; }
.step-num { display: inline-flex; align-items: center; justify-content: center; width: 38px; height: 38px; border-radius: 6px; font-family: 'Outfit', sans-serif; font-size: 16px; font-weight: 700; color: #0D1B2A; flex-shrink: 0; }
.step-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px; }
.step-layer { font-size: 0.78rem; font-style: italic; opacity: 0.75; margin-left: auto; white-space: nowrap; }
.sensor-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 12px 0; }
.sensor-card { background: #0D1B2A; border-radius: 8px; padding: 14px; border-left: 3px solid; position: relative; overflow: hidden; }
.sensor-pulse { position: absolute; top: 10px; right: 10px; width: 8px; height: 8px; border-radius: 50%; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(1.4)} }
.alert-card { display: flex; align-items: flex-start; gap: 12px; background: #0D1B2A; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; border-left: 4px solid; }
.alert-badge { margin-left: auto; padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 700; white-space: nowrap; flex-shrink: 0; }
.action-card { background: #0D1B2A; border-radius: 8px; padding: 14px 16px; margin-bottom: 8px; border: 1px solid #1E3A5F; display: flex; justify-content: space-between; align-items: center; }
.action-status { padding: 4px 12px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.policy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 12px 0; }
.policy-card { background: #0D1B2A; border-radius: 8px; padding: 16px; border-top: 3px solid; text-align: center; }
.policy-val { font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.policy-label { font-size: 0.75rem; color: #8A9BB0; text-transform: uppercase; letter-spacing: 1px; }
.policy-trend { font-size: 0.78rem; margin-top: 4px; }
.flow-arrow { text-align: center; font-size: 1.8rem; color: #00C896; margin: 4px 0; animation: bounce 1.5s infinite; }
@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(4px)} }
.loop-bar { background: #0D1B2A; border: 1px solid #1E3A5F; border-top: 3px solid #7B5EA7; padding: 14px 20px; border-radius: 8px; text-align: center; margin-top: 8px; }
.loop-text { color: #8A9BB0; font-style: italic; font-size: 0.88rem; }
.loop-text span { color: #00C896; font-weight: 600; }
.live-dot { display: inline-block; width: 8px; height: 8px; background: #00C896; border-radius: 50%; margin-right: 6px; animation: pulse 1.5s infinite; }
</style>
"""

def get_live_db_data():
    try:
        from database import GridDatabase
        from ml_models import prepare_data
        db = GridDatabase("gridsense.db")
        raw = db.get_latest_per_feeder()
        if raw is not None and len(raw) > 0:
            df = prepare_data(raw)
            alerts = db.get_unresolved_alerts(limit=10)
            total  = db.get_total_readings()
            return df, alerts, total, db
    except Exception:
        pass
    return None, None, 0, None

def sim_sensor_reading(feeder_id="FEEDER_001", state="Maharashtra"):
    loss = random.uniform(5, 32)
    inj  = random.uniform(300, 2000)
    return {
        "feeder_id": feeder_id, "state": state,
        "loss_percentage": round(loss, 2),
        "voltage": round(random.uniform(218, 243), 1),
        "current_amp": round(random.uniform(10, 120), 1),
        "power_kw": round(random.uniform(50, 400), 1),
        "units_injected": round(inj, 1),
        "units_billed": round(inj * (1 - loss / 100), 1),
        "temperature": round(random.uniform(18, 44), 1),
        "load_factor": round(random.uniform(0.45, 0.95), 2),
        "voltage_fluctuation": round(random.uniform(0.5, 9.5), 1),
        "transformer_age": random.randint(2, 28),
        "smart_meter": random.choice([True, False]),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }

def generate_detections(df):
    detections = []
    if df is not None and len(df) > 0:
        for _, row in df[df['is_suspicious']].head(3).iterrows():
            detections.append({"type":"THEFT","severity":"CRITICAL" if row['loss_percentage']>28 else "HIGH","feeder":row['feeder_id'],"state":row.get('state','N/A'),"detail":f"Loss {row['loss_percentage']:.1f}% — anomalous consumption pattern","icon":"🚨"})
        for _, row in df[df['risk_label']=='HIGH'].head(2).iterrows():
            detections.append({"type":"HARDWARE","severity":"HIGH","feeder":row['feeder_id'],"state":row.get('state','N/A'),"detail":f"Transformer age {int(row.get('transformer_age',0))}yr — predicted failure in 3-6 wks","icon":"⚠️"})
    if not detections:
        detections = [
            {"type":"THEFT","severity":"CRITICAL","feeder":"FEEDER_007","state":"UP","detail":"Loss 31.2% — illegal hooking suspected","icon":"🚨"},
            {"type":"HARDWARE","severity":"HIGH","feeder":"FEEDER_023","state":"Bihar","detail":"Transformer age 24yr — predicted failure in 4 wks","icon":"⚠️"},
            {"type":"OVERLOAD","severity":"MEDIUM","feeder":"FEEDER_041","state":"Rajasthan","detail":"Load factor 0.94 — overload risk during peak hours","icon":"🔶"},
            {"type":"THEFT","severity":"HIGH","feeder":"FEEDER_015","state":"Maharashtra","detail":"Billing gap Rs2.1L/month — meter tampering suspected","icon":"🚨"},
            {"type":"VOLTAGE","severity":"MEDIUM","feeder":"FEEDER_033","state":"Tamil Nadu","detail":"Voltage fluctuation 8.3% — affecting downstream quality","icon":"⚡"},
        ]
    return detections

def generate_actions(detections):
    actions = []
    for d in detections:
        if d["type"] == "THEFT":
            actions.append({"title":f"Field inspection — {d['feeder']} ({d['state']})","detail":"Anti-theft team dispatched with meter audit kit","eta":f"{random.randint(1,4)}h","status":"DISPATCHED","color":"#dc2626"})
        elif d["type"] == "HARDWARE":
            actions.append({"title":f"Transformer replacement — {d['feeder']}","detail":"Maintenance crew scheduled, spare unit reserved","eta":f"{random.randint(1,5)}d","status":"SCHEDULED","color":"#f59e0b"})
        elif d["type"] in ("OVERLOAD","VOLTAGE"):
            actions.append({"title":f"Load balancing — {d['feeder']}","detail":"Auto-switching rerouting load to adjacent feeder","eta":"AUTO","status":"IN PROGRESS","color":"#7B5EA7"})
    return actions[:5]

def show_giip_page():
    st.markdown(GIIP_CSS, unsafe_allow_html=True)
    df, db_alerts, total_readings, db_obj = get_live_db_data()

    st.markdown('<div class="giip-badge">03 · RECOMMENDED SOLUTION — THE BIG IDEA</div>', unsafe_allow_html=True)
    st.markdown('<div class="giip-title">GIIP: GridZero Integrated Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="giip-subtitle">One closed-loop platform where real-time data feeds AI, AI drives hardware action, and policy sustains it all</div>', unsafe_allow_html=True)

    data_src = "Live DB" if df is not None else "Simulated"
    st.caption(f"Data source: **{data_src}**  •  {datetime.now().strftime('%H:%M:%S')}")
    if st.button("Refresh Flow"):
        st.rerun()
    st.markdown("---")

    # ── SENSE ─────────────────────────────────────────────────────
    st.markdown('<div class="step-header" style="background:#00C89618;border-left:4px solid #00C896;"><div class="step-num" style="background:#00C896;">01</div><div><div class="step-title" style="color:#00C896;">SENSE</div><div style="font-size:0.8rem;color:#8A9BB0;font-style:italic;">Data Layer — AMI · Smart Meters · IoT Sensors · SCADA</div></div><div class="step-layer" style="color:#8A9BB0;">Every watt tracked in real-time</div></div>', unsafe_allow_html=True)

    feeders_to_show = ["FEEDER_001","FEEDER_007","FEEDER_015","FEEDER_023","FEEDER_033","FEEDER_041"]
    sensors = []
    if df is not None and len(df) >= 6:
        for _, row in df.head(6).iterrows():
            sensors.append({"feeder_id":row.get("feeder_id","N/A"),"state":row.get("state","N/A"),"loss_percentage":row.get("loss_percentage",0),"voltage":row.get("voltage",230),"current_amp":row.get("current_amp",50),"power_kw":row.get("power_kw",100),"units_injected":row.get("units_injected",500),"units_billed":row.get("units_billed",450),"temperature":row.get("temperature",30),"load_factor":row.get("load_factor",0.7),"voltage_fluctuation":row.get("voltage_fluctuation",2.0),"transformer_age":row.get("transformer_age",10),"smart_meter":row.get("smart_meter",True),"timestamp":datetime.now().strftime("%H:%M:%S")})
    else:
        sensors = [sim_sensor_reading(fid,s) for fid,s in zip(feeders_to_show,["Maharashtra","UP","Bihar","Gujarat","Tamil Nadu","Rajasthan"])]

    colors = ["#00C896","#00BCD4","#F5A623","#7B5EA7","#dc2626","#16a34a"]
    icons  = ["⚡","🔌","🌡️","📊","⚙️","📡"]
    html_sensors = '<div class="sensor-grid">'
    for i, s in enumerate(sensors):
        c  = colors[i % len(colors)]
        lc = "#dc2626" if s["loss_percentage"] > 25 else ("#f59e0b" if s["loss_percentage"] > 15 else "#00C896")
        html_sensors += f'<div class="sensor-card" style="border-color:{c}"><div class="sensor-pulse" style="background:{c}"></div><div style="font-size:1.3rem">{icons[i]}</div><div style="font-size:0.7rem;color:#8A9BB0;text-transform:uppercase;letter-spacing:1px">{s["feeder_id"]} · {s["state"]}</div><div style="font-family:Outfit,sans-serif;font-size:1.4rem;font-weight:700;color:{lc}">{s["loss_percentage"]:.1f}%</div><div style="font-size:0.7rem;color:#8A9BB0">T&D Loss</div><div style="margin-top:8px;display:grid;grid-template-columns:1fr 1fr;gap:4px;"><div><div style="font-size:0.65rem;color:#8A9BB0">VOLTAGE</div><div style="font-size:0.8rem;color:#E2EAF0;font-weight:600">{s["voltage"]}V</div></div><div><div style="font-size:0.65rem;color:#8A9BB0">LOAD</div><div style="font-size:0.8rem;color:#E2EAF0;font-weight:600">{s["load_factor"]}</div></div><div><div style="font-size:0.65rem;color:#8A9BB0">POWER</div><div style="font-size:0.8rem;color:#E2EAF0;font-weight:600">{s["power_kw"]}kW</div></div><div><div style="font-size:0.65rem;color:#8A9BB0">TEMP</div><div style="font-size:0.8rem;color:#E2EAF0;font-weight:600">{s["temperature"]}°C</div></div></div><div style="margin-top:8px;font-size:0.65rem;color:#8A9BB0">🕐 {s["timestamp"]} · Smart: {"✅" if s["smart_meter"] else "❌"}</div></div>'
    html_sensors += '</div>'
    st.markdown(html_sensors, unsafe_allow_html=True)

    sense_df = pd.DataFrame(sensors)[["feeder_id","loss_percentage"]]
    fig_s = px.bar(sense_df, x="feeder_id", y="loss_percentage", color="loss_percentage", color_continuous_scale=["#00C896","#f59e0b","#dc2626"], height=200, labels={"loss_percentage":"Loss %","feeder_id":""})
    fig_s.add_hline(y=2, line_dash="dash", line_color="#00C896", annotation_text="2% Target", annotation_font_color="#00C896")
    fig_s.update_layout(margin=dict(t=10,b=10,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#C8D4E0", coloraxis_showscale=False, xaxis=dict(tickfont=dict(size=10)))
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

    # ── DETECT ────────────────────────────────────────────────────
    st.markdown('<div class="step-header" style="background:#00BCD418;border-left:4px solid #00BCD4;"><div class="step-num" style="background:#00BCD4;">02</div><div><div class="step-title" style="color:#00BCD4;">DETECT</div><div style="font-size:0.8rem;color:#8A9BB0;font-style:italic;">Intelligence Layer — Isolation Forest · Random Forest · Gemini AI</div></div><div class="step-layer" style="color:#8A9BB0;">Flags theft · Predicts failures 3-6 weeks ahead</div></div>', unsafe_allow_html=True)

    detections = generate_detections(df)
    sev_c = {"CRITICAL":"#dc2626","HIGH":"#f59e0b","MEDIUM":"#7B5EA7"}
    sev_b = {"CRITICAL":"#dc262622","HIGH":"#f59e0b22","MEDIUM":"#7B5EA722"}
    html_det = ""
    for d in detections:
        sc = sev_c.get(d["severity"],"#8A9BB0"); sb = sev_b.get(d["severity"],"#1E3A5F")
        html_det += f'<div class="alert-card" style="border-color:{sc}"><div style="font-size:1.3rem;flex-shrink:0;margin-top:2px">{d["icon"]}</div><div style="flex:1"><div style="font-family:Outfit,sans-serif;font-weight:700;font-size:0.9rem;color:#E2EAF0">{d["type"]} DETECTED — {d["feeder"]} ({d["state"]})</div><div style="font-size:0.8rem;color:#8A9BB0;margin-top:2px">{d["detail"]}</div></div><div class="alert-badge" style="background:{sb};color:{sc};border:1px solid {sc}">{d["severity"]}</div></div>'
    st.markdown(html_det, unsafe_allow_html=True)

    if df is not None and len(df) > 5:
        fig_d = px.scatter(df, x="units_injected", y="loss_percentage", color="is_suspicious", color_discrete_map={True:"#dc2626",False:"#00C896"}, hover_data=["feeder_id","state"], height=220)
    else:
        np.random.seed(42); n=50
        sim = pd.DataFrame({"units_injected":np.random.uniform(300,2000,n),"loss_percentage":np.concatenate([np.random.uniform(5,18,40),np.random.uniform(25,35,10)]),"is_suspicious":[False]*40+[True]*10})
        fig_d = px.scatter(sim, x="units_injected", y="loss_percentage", color="is_suspicious", color_discrete_map={True:"#dc2626",False:"#00C896"}, height=220)
    fig_d.update_layout(margin=dict(t=10,b=10,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#C8D4E0")
    fig_d.update_xaxes(gridcolor="#1E3A5F"); fig_d.update_yaxes(gridcolor="#1E3A5F")
    st.plotly_chart(fig_d, use_container_width=True)

    st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

    # ── ACT ───────────────────────────────────────────────────────
    st.markdown('<div class="step-header" style="background:#7B5EA718;border-left:4px solid #7B5EA7;"><div class="step-num" style="background:#7B5EA7;color:white;">03</div><div><div class="step-title" style="color:#9B7EC8;">ACT</div><div style="font-size:0.8rem;color:#8A9BB0;font-style:italic;">Execution Layer — Auto-switching · Field Dispatch · ROI-ranked Upgrades</div></div><div class="step-layer" style="color:#8A9BB0;">From insight to action in minutes</div></div>', unsafe_allow_html=True)

    actions = generate_actions(detections)
    sc_map = {"DISPATCHED":("#dc2626","#dc262622"),"IN PROGRESS":("#f59e0b","#f59e0b22"),"SCHEDULED":("#7B5EA7","#7B5EA722"),"AUTO":("#00C896","#00C89622")}
    html_act = ""
    for a in actions:
        sc, sb = sc_map.get(a["status"],("#8A9BB0","#1E3A5F22"))
        html_act += f'<div class="action-card"><div style="flex:1"><div style="font-family:Outfit,sans-serif;font-weight:700;font-size:0.9rem;color:#E2EAF0">{a["title"]}</div><div style="font-size:0.78rem;color:#8A9BB0;margin-top:3px">{a["detail"]} · ETA: <strong style="color:#E2EAF0">{a["eta"]}</strong></div></div><div class="action-status" style="background:{sb};color:{sc};border:1px solid {sc}">{a["status"]}</div></div>'
    st.markdown(html_act, unsafe_allow_html=True)

    if actions:
        act_df = pd.DataFrame([{"action":(a["title"][:28]+"…" if len(a["title"])>28 else a["title"]),"roi_cr":round(random.uniform(0.5,8.0),1)} for a in actions])
        fig_a = px.bar(act_df, x="action", y="roi_cr", color="roi_cr", color_continuous_scale=["#7B5EA7","#00C896"], labels={"roi_cr":"Est. ROI (Rs Cr)","action":""}, height=200)
        fig_a.update_layout(margin=dict(t=10,b=10,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#C8D4E0", coloraxis_showscale=False, xaxis=dict(tickfont=dict(size=9)))
        fig_a.update_yaxes(gridcolor="#1E3A5F")
        st.plotly_chart(fig_a, use_container_width=True)

    st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

    # ── SUSTAIN ───────────────────────────────────────────────────
    st.markdown('<div class="step-header" style="background:#F5A62318;border-left:4px solid #F5A623;"><div class="step-num" style="background:#F5A623;">04</div><div><div class="step-title" style="color:#F5A623;">SUSTAIN</div><div style="font-size:0.8rem;color:#8A9BB0;font-style:italic;">Policy Layer — Performance Tariffs · Carbon Credits · Feeder P&L</div></div><div class="step-layer" style="color:#8A9BB0;">Self-funding loop that keeps improving</div></div>', unsafe_allow_html=True)

    avg_loss = df['loss_percentage'].mean() if df is not None and len(df) > 0 else 18.4
    susp_cnt = int(df['is_suspicious'].sum()) if df is not None and len(df) > 0 else 6
    rev_rec  = round(avg_loss * 47, 0)
    co2_save = round((avg_loss - 2) * 8.3, 1)

    st.markdown(f'<div class="policy-grid"><div class="policy-card" style="border-color:#F5A623"><div class="policy-val" style="color:#F5A623">Rs{rev_rec:.0f}Cr</div><div class="policy-label">Est. Annual Revenue Recovery</div><div class="policy-trend" style="color:#00C896">Reinvested into grid upgrades</div></div><div class="policy-card" style="border-color:#00C896"><div class="policy-val" style="color:#00C896">{co2_save:.0f} MT</div><div class="policy-label">CO2 Avoided / Year</div><div class="policy-trend" style="color:#F5A623">Converted to carbon credits</div></div><div class="policy-card" style="border-color:#7B5EA7"><div class="policy-val" style="color:#9B7EC8">{avg_loss:.1f}%</div><div class="policy-label">Current Loss Rate</div><div class="policy-trend" style="color:#F5A623">Target below 2% by 2030</div></div><div class="policy-card" style="border-color:#00BCD4"><div class="policy-val" style="color:#00BCD4">{total_readings:,}</div><div class="policy-label">Total Readings Processed</div><div class="policy-trend" style="color:#00C896">RDSS Compliance Active</div></div></div>', unsafe_allow_html=True)

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    base = avg_loss
    trend = [round(max(2.0, base - i*(base-2)/11 + random.uniform(-0.5,0.5)),1) for i in range(12)]
    trend_df = pd.DataFrame({"Month":months,"Loss %":trend})
    fig_sus = go.Figure()
    fig_sus.add_trace(go.Scatter(x=trend_df["Month"], y=trend_df["Loss %"], mode="lines+markers", line=dict(color="#F5A623",width=3), marker=dict(size=7,color="#F5A623"), fill="tozeroy", fillcolor="rgba(245,166,35,0.08)"))
    fig_sus.add_hline(y=2, line_dash="dash", line_color="#00C896", annotation_text="2030 Target: 2%", annotation_font_color="#00C896")
    fig_sus.update_layout(height=200, margin=dict(t=10,b=10,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#C8D4E0", showlegend=False)
    fig_sus.update_xaxes(gridcolor="#1E3A5F"); fig_sus.update_yaxes(gridcolor="#1E3A5F")
    st.plotly_chart(fig_sus, use_container_width=True)

    st.markdown('<div class="loop-bar"><div class="loop-text">← <span>Continuous improvement loop:</span> Every action feeds back into the Sense layer — the grid gets smarter every day</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("🤖 Ask Gemini AI about this flow"):
        q = st.text_input("e.g. Which layer needs the most attention right now?", key="giip_gemini_q")
        if st.button("Get Insight", key="giip_gemini_btn") and q:
            try:
                from gemini_engine import ask_gridsense
                state_avg = df.groupby('state')['loss_percentage'].mean() if df is not None and len(df) > 0 else {}
                ctx = {"avg_loss":avg_loss,"suspicious_count":susp_cnt,"high_risk_count":int((df['risk_label']=='HIGH').sum()) if df is not None and len(df)>0 else 0,"worst_state":state_avg.idxmax() if len(state_avg)>0 else "N/A","best_state":state_avg.idxmin() if len(state_avg)>0 else "N/A","revenue_loss":rev_rec,"total_readings":total_readings,"last_updated":datetime.now().strftime("%H:%M:%S")}
                with st.spinner("Gemini thinking..."):
                    answer = ask_gridsense(q, ctx)
                st.markdown(answer)
            except Exception as e:
                st.warning(f"Gemini not available: {e}")

if __name__ == "__main__":
    st.set_page_config(page_title="GIIP Flow", layout="wide", page_icon="⚡")
    show_giip_page()
