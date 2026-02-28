"""
theme.py — GridSense AI Design System (Streamlit-native approach)
No HTML div wrapping around st.plotly_chart — uses CSS to style
Streamlit's own containers instead.
"""
import streamlit as st

DARK_VARS = """
  --bg-base:       #070D16;
  --bg-surface:    #0D1825;
  --bg-card:       #111E2E;
  --bg-elevated:   #162436;
  --border-subtle: #1E3448;
  --border-mid:    #253D58;
  --border-strong: #2E5070;
  --text-primary:  #E8F0F8;
  --text-secondary:#8AA4BE;
  --text-muted:    #4A6580;
  --shadow:        rgba(0,0,0,0.45);
  --plot-bg:       rgba(13,24,37,0.95);
  --plot-grid:     #1E3448;
  --plot-text:     #8AA4BE;
"""

LIGHT_VARS = """
  --bg-base:       #F0F4F8;
  --bg-surface:    #FFFFFF;
  --bg-card:       #FFFFFF;
  --bg-elevated:   #EEF2F7;
  --border-subtle: #D0DCE8;
  --border-mid:    #B0C4D8;
  --border-strong: #8AAAC4;
  --text-primary:  #0D1B2A;
  --text-secondary:#3A5672;
  --text-muted:    #7A96B0;
  --shadow:        rgba(0,0,0,0.08);
  --plot-bg:       rgba(240,244,248,0.95);
  --plot-grid:     #D0DCE8;
  --plot-text:     #3A5672;
"""

def build_css(vars_block: str) -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap');

:root {{
{vars_block}
  --green:  #00C87A;
  --cyan:   #0099E6;
  --purple: #7B5EA7;
  --orange: #FF8C42;
  --red:    #E8304A;
  --yellow: #F0B429;
  --font-display: 'Syne', sans-serif;
  --font-body:    'Outfit', sans-serif;
  --font-mono:    'IBM Plex Mono', monospace;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
}}

/* ── Global base ───────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], section.main, .main {{
  background-color: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
}}
.block-container {{
  padding: 1.5rem 2rem 3rem !important;
  max-width: 1400px !important;
}}

/* ── Sidebar ───────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {{
  background-color: var(--bg-surface) !important;
  border-right: 1px solid var(--border-subtle) !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stRadio label {{
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
}}

/* ── Style Streamlit's native column/element containers as cards ── */
/* Every direct child block inside columns gets card treatment */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {{
  background: var(--bg-card) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-lg) !important;
  padding: 0 !important;
  box-shadow: 0 2px 12px var(--shadow) !important;
  overflow: hidden !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  margin-bottom: 4px !important;
}}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:hover {{
  border-color: var(--border-mid) !important;
  box-shadow: 0 4px 24px var(--shadow) !important;
}}

/* ── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: var(--bg-base); }}
::-webkit-scrollbar-thumb {{ background: var(--border-mid); border-radius: 10px; }}

/* ── Topbar ────────────────────────────────────────────────── */
.gs-topbar {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0 18px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 20px;
}}
.gs-page-title {{
  font-family: var(--font-display);
  font-size: 1.6rem; font-weight: 800;
  color: var(--text-primary); letter-spacing: -0.5px;
}}
.gs-breadcrumb {{
  font-size: 0.72rem; color: var(--text-muted);
  font-family: var(--font-mono); margin-top: 3px;
}}
.gs-time {{
  font-family: var(--font-mono); font-size: 0.75rem;
  color: var(--text-secondary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  padding: 5px 13px; border-radius: 20px;
}}

/* ── KPI cards ─────────────────────────────────────────────── */
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px; margin-bottom: 20px;
}}
.kpi-card {{
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px 18px;
  position: relative; overflow: hidden;
  box-shadow: 0 2px 10px var(--shadow);
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}}
.kpi-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 24px var(--shadow);
  border-color: var(--border-mid);
}}
.kpi-card::before {{
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
}}
.kpi-card.green::before  {{ background: var(--green);  }}
.kpi-card.cyan::before   {{ background: var(--cyan);   }}
.kpi-card.purple::before {{ background: var(--purple); }}
.kpi-card.orange::before {{ background: var(--orange); }}
.kpi-card.red::before    {{ background: var(--red);    }}
.kpi-icon {{
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--bg-elevated);
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; margin-bottom: 10px;
}}
.kpi-value {{
  font-family: var(--font-body);
  font-size: 1.75rem; font-weight: 700;
  line-height: 1.1; margin-bottom: 4px;
}}
.kpi-label {{
  font-size: 0.69rem; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 1px;
}}
.kpi-delta {{ font-size: 0.69rem; margin-top: 6px; font-family: var(--font-mono); }}

/* ── Chart title bar (rendered ABOVE the chart via st.markdown) ── */
.chart-header {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px 10px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-card);
}}
.chart-title {{
  font-family: var(--font-display);
  font-size: 0.92rem; font-weight: 700;
  color: var(--text-primary);
}}
.chart-badge {{
  font-family: var(--font-mono); font-size: 0.65rem;
  padding: 3px 9px; border-radius: 20px; font-weight: 600;
}}
.badge-live   {{ background:rgba(0,200,122,0.15); color:var(--green); border:1px solid rgba(0,200,122,0.3); }}
.badge-ml     {{ background:rgba(0,153,230,0.15); color:var(--cyan);  border:1px solid rgba(0,153,230,0.3); }}
.badge-ai     {{ background:rgba(123,94,167,0.15);color:var(--purple);border:1px solid rgba(123,94,167,0.3); }}

/* ── Section divider ───────────────────────────────────────── */
.section-divider {{
  display: flex; align-items: center; gap: 12px;
  margin: 20px 0 14px;
}}
.sd-line {{ flex: 1; height: 1px; background: var(--border-subtle); }}
.sd-label {{
  font-family: var(--font-mono); font-size: 0.66rem;
  color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px;
}}

/* ── Badges ────────────────────────────────────────────────── */
.badge {{
  display: inline-block; padding: 3px 9px; border-radius: 20px;
  font-size: 0.65rem; font-weight: 700;
  font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.5px;
}}
.badge-critical {{ background:rgba(232,48,74,0.13); color:var(--red);    border:1px solid rgba(232,48,74,0.3); }}
.badge-high     {{ background:rgba(255,140,66,0.13);color:var(--orange); border:1px solid rgba(255,140,66,0.3); }}
.badge-medium   {{ background:rgba(123,94,167,0.13);color:var(--purple); border:1px solid rgba(123,94,167,0.3); }}
.badge-low      {{ background:rgba(0,200,122,0.13); color:var(--green);  border:1px solid rgba(0,200,122,0.3); }}

/* ── Alert rows ────────────────────────────────────────────── */
.alert-row {{
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; border-radius: var(--radius-md);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle); border-left: 3px solid;
  margin-bottom: 7px; transition: background 0.15s;
}}
.alert-row:hover {{ background: var(--bg-card); }}
.alert-row.critical {{ border-left-color: var(--red);    }}
.alert-row.high     {{ border-left-color: var(--orange); }}
.alert-row.medium   {{ border-left-color: var(--purple); }}
.alert-icon  {{ font-size: 1rem; flex-shrink: 0; }}
.alert-body  {{ flex: 1; min-width: 0; }}
.alert-title {{ font-size: 0.82rem; font-weight: 600; color: var(--text-primary); }}
.alert-sub   {{ font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; font-family: var(--font-mono); }}
.alert-time  {{ font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-muted); }}

/* ── Sidebar brand ─────────────────────────────────────────── */
.sidebar-brand {{
  display: flex; align-items: center; gap: 11px;
  padding: 18px 12px 14px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 10px;
}}
.sidebar-logo {{
  width: 36px; height: 36px; border-radius: 8px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--green), var(--cyan));
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; font-weight: 800; color: #fff;
  font-family: var(--font-display);
}}
.sidebar-name {{ font-family:var(--font-display); font-size:1rem; font-weight:800; color:var(--text-primary); }}
.sidebar-tag  {{ font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; }}
.sidebar-live {{
  display:flex; align-items:center; gap:7px;
  padding:6px 12px 8px; font-size:0.72rem;
  color:var(--green); font-family:var(--font-mono);
}}
.live-dot {{
  width:7px; height:7px; border-radius:50%;
  background:var(--green); flex-shrink:0;
  animation: lp 1.8s infinite;
}}
@keyframes lp {{
  0%,100%{{ box-shadow:0 0 0 0 rgba(0,200,122,0.5); }}
  50%    {{ box-shadow:0 0 0 5px rgba(0,200,122,0);  }}
}}

/* ── Status ────────────────────────────────────────────────── */
.status-row {{ display:flex; align-items:center; gap:8px; font-family:var(--font-mono); font-size:0.72rem; color:var(--text-muted); }}
.status-dot  {{ width:6px; height:6px; border-radius:50%; flex-shrink:0; }}
.status-ok   .status-dot {{ background:var(--green); }}
.status-warn .status-dot {{ background:var(--orange); }}

/* ── Info banner ───────────────────────────────────────────── */
.info-banner {{
  border-radius: var(--radius-md); padding: 10px 15px;
  font-size: 0.81rem; color: var(--text-secondary);
  margin-bottom: 16px;
}}

/* ── Streamlit overrides ───────────────────────────────────── */
.stButton > button {{
  background: var(--bg-elevated) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-body) !important;
  font-size: 0.82rem !important;
  transition: all 0.15s !important;
}}
.stButton > button:hover {{
  background: var(--border-mid) !important;
  transform: translateY(-1px) !important;
}}
[data-testid="baseButton-primary"] {{
  background: linear-gradient(135deg, var(--green), var(--cyan)) !important;
  color: #fff !important; border: none !important; font-weight: 700 !important;
}}
.stSelectbox > div > div {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
}}
.stSelectbox label {{ color: var(--text-secondary) !important; font-size: 0.8rem !important; }}
.stTextInput > div > div > input {{
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
}}
.stTabs [data-baseweb="tab-list"] {{
  background: transparent !important;
  border-bottom: 1px solid var(--border-subtle) !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: var(--text-muted) !important;
  font-family: var(--font-body) !important;
  font-size: 0.83rem !important;
  border: none !important;
  padding: 8px 16px !important;
}}
.stTabs [aria-selected="true"] {{
  color: var(--text-primary) !important;
  border-bottom: 2px solid var(--green) !important;
}}
[data-testid="stMetric"] {{
  background: var(--bg-card) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-md) !important;
  padding: 14px 16px !important;
}}
[data-testid="stMetricValue"] {{ font-family:var(--font-display) !important; color:var(--text-primary) !important; }}
[data-testid="stMetricLabel"] {{ font-size:0.7rem !important; color:var(--text-muted) !important; text-transform:uppercase !important; letter-spacing:0.8px !important; }}
[data-testid="stDataFrame"] {{ border:1px solid var(--border-subtle) !important; border-radius:var(--radius-md) !important; overflow:hidden !important; }}
[data-testid="stAlert"] {{ border-radius:var(--radius-md) !important; background:var(--bg-elevated) !important; color:var(--text-secondary) !important; }}
[data-testid="stChatMessage"] {{ background:var(--bg-card) !important; border:1px solid var(--border-subtle) !important; border-radius:var(--radius-md) !important; }}
.streamlit-expanderHeader {{ background:var(--bg-elevated) !important; border:1px solid var(--border-subtle) !important; color:var(--text-secondary) !important; }}
.stDownloadButton > button {{ color:var(--green) !important; border:1px solid rgba(0,200,122,0.3) !important; }}
hr {{ border-color: var(--border-subtle) !important; margin: 14px 0 !important; }}
.stCaption {{ color:var(--text-muted) !important; font-size:0.72rem !important; font-family:var(--font-mono) !important; }}
#MainMenu, footer {{ visibility: hidden !important; }}
</style>
"""


def inject_theme():
    dark = st.session_state.get("dark_mode", True)
    st.markdown(build_css(DARK_VARS if dark else LIGHT_VARS), unsafe_allow_html=True)


def plotly_dark_layout(fig, height=300):
    dark = st.session_state.get("dark_mode", True)
    if dark:
        pb = "rgba(11,20,33,0.0)"
        pl = "rgba(13,24,37,0.0)"
        fc = "#8AA4BE"; gc = "#1E3448"; tc = "#4A6580"
    else:
        pb = "rgba(240,244,248,0.0)"
        pl = "rgba(240,244,248,0.0)"
        fc = "#3A5672"; gc = "#D0DCE8"; tc = "#7A96B0"
    fig.update_layout(
        height=height,
        paper_bgcolor=pb, plot_bgcolor=pl,
        font=dict(family="Outfit,sans-serif", color=fc, size=11),
        margin=dict(t=10, b=10, l=8, r=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=fc)),
        xaxis=dict(gridcolor=gc, linecolor=gc, tickcolor=tc),
        yaxis=dict(gridcolor=gc, linecolor=gc, tickcolor=tc),
    )
    return fig


def topbar(title: str, breadcrumb: str = ""):
    from datetime import datetime
    st.markdown(f"""
    <div class="gs-topbar">
      <div>
        <div class="gs-page-title">{title}</div>
        {f'<div class="gs-breadcrumb">{breadcrumb}</div>' if breadcrumb else ''}
      </div>
      <div class="gs-time">🕐 {datetime.now().strftime('%d %b %Y  %H:%M:%S')}</div>
    </div>""", unsafe_allow_html=True)


def kpi_row(cards: list):
    html = '<div class="kpi-grid">'
    for c in cards:
        col = c.get("color", "green")
        d = c.get("delta", "")
        dc = "var(--red)" if ("↑" in d or "worse" in d.lower()) else "var(--green)"
        html += f"""
        <div class="kpi-card {col}">
          <div class="kpi-icon">{c.get('icon','')}</div>
          <div class="kpi-value" style="color:var(--{col})">{c['value']}</div>
          <div class="kpi-label">{c['label']}</div>
          {f'<div class="kpi-delta" style="color:{dc}">{d}</div>' if d else ''}
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def section_divider(label: str):
    st.markdown(f"""
    <div class="section-divider">
      <div class="sd-line"></div>
      <div class="sd-label">{label}</div>
      <div class="sd-line"></div>
    </div>""", unsafe_allow_html=True)


def chart_title(title: str, badge: str = "", badge_cls: str = "badge-live"):
    """Render a title bar ABOVE a chart — must be called inside a with col: block."""
    badge_html = f'<span class="chart-badge {badge_cls}">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="chart-header">
      <div class="chart-title">{title}</div>
      {badge_html}
    </div>""", unsafe_allow_html=True)


def info_banner(text: str, color: str = "cyan"):
    colors = {
        "cyan":   ("rgba(0,153,230,0.08)",  "rgba(0,153,230,0.25)"),
        "purple": ("rgba(123,94,167,0.08)", "rgba(123,94,167,0.25)"),
        "green":  ("rgba(0,200,122,0.08)",  "rgba(0,200,122,0.25)"),
        "orange": ("rgba(255,140,66,0.08)", "rgba(255,140,66,0.25)"),
    }
    bg, border = colors.get(color, colors["cyan"])
    st.markdown(f"""
    <div class="info-banner" style="background:{bg};border:1px solid {border};">
      {text}
    </div>""", unsafe_allow_html=True)


def render_alert_row(icon, title, subtitle, severity, time_str=""):
    return f"""
    <div class="alert-row {severity.lower()}">
      <div class="alert-icon">{icon}</div>
      <div class="alert-body">
        <div class="alert-title">{title}</div>
        <div class="alert-sub">{subtitle}</div>
      </div>
      {f'<div class="alert-time">{time_str}</div>' if time_str else ''}
      <span class="badge badge-{severity.lower()}">{severity}</span>
    </div>"""


def sidebar_brand(total_readings: int = 0, data_source: str = "CSV"):
    st.sidebar.markdown(f"""
    <div class="sidebar-brand">
      <div class="sidebar-logo">G</div>
      <div>
        <div class="sidebar-name">GridSense AI</div>
        <div class="sidebar-tag">T&amp;D Loss Intelligence</div>
      </div>
    </div>
    <div class="sidebar-live">
      <div class="live-dot"></div>
      {data_source} &nbsp;·&nbsp; {total_readings:,} records
    </div>""", unsafe_allow_html=True)


def theme_toggle():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    dark = st.session_state.dark_mode
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='font-size:0.67rem;color:var(--text-muted);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Theme</div>", unsafe_allow_html=True)
    if st.sidebar.button("☀️ Light Mode" if dark else "🌙 Dark Mode", key="theme_btn", use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()
    st.sidebar.markdown(f"<div style='font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted);padding:2px 0 10px;text-align:center;'>{'🌙 Dark' if dark else '☀️ Light'} mode</div>", unsafe_allow_html=True)
    return dark