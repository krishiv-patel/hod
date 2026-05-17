"""
app_styles.py — Premium dark-mode custom CSS for the HOD Dashboard.
Enhanced v2 with animated elements, refined glassmorphism, and responsive polish.
"""

CUSTOM_CSS = """
<style>
    /* ===== Google Fonts ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== Global ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: radial-gradient(circle at 15% 50%, rgba(30, 27, 55, 1), rgba(15, 12, 41, 1) 100%) !important;
        background-attachment: fixed !important;
    }

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(15, 12, 41, 0.6); }
    ::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.7); }

    /* ===== Header ===== */
    .dashboard-header {
        background: linear-gradient(135deg, rgba(15, 12, 41, 0.6) 0%, rgba(48, 43, 99, 0.6) 50%, rgba(36, 36, 62, 0.6) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 20px rgba(139, 92, 246, 0.05);
        position: relative;
        overflow: hidden;
    }
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        animation: pulseGlow 8s infinite alternate;
    }
    @keyframes pulseGlow {
        0% { transform: scale(1); opacity: 0.8; }
        100% { transform: scale(1.1); opacity: 1; }
    }
    .dashboard-header h1 {
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.25rem 0;
        background: linear-gradient(90deg, #a78bfa, #818cf8, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .dashboard-header p {
        color: rgba(255, 255, 255, 0.55);
        font-size: 0.95rem;
        margin: 0;
        font-weight: 400;
    }

    /* ===== KPI Cards ===== */
    .kpi-card {
        background: rgba(20, 18, 40, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        padding: 1.25rem 0.75rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::after {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.03), transparent);
        transform: skewX(-20deg); transition: 0.5s;
    }
    .kpi-card:hover::after { left: 150%; }
    .kpi-card:hover {
        border-color: rgba(167, 139, 250, 0.7);
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(139, 92, 246, 0.3), 0 0 15px rgba(167, 139, 250, 0.3);
    }
    .kpi-card .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        margin-bottom: 0.25rem;
        white-space: nowrap;
    }
    .kpi-card .kpi-label {
        font-size: 0.72rem;
        color: rgba(255, 255, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        white-space: nowrap;
    }
    .kpi-card .kpi-sub {
        font-size: 0.75rem;
        color: rgba(167, 139, 250, 0.7);
        margin-top: 0.15rem;
        font-weight: 400;
    }

    /* ===== Variant KPI Colors ===== */
    .kpi-green .kpi-value {
        background: linear-gradient(135deg, #34d399, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-amber .kpi-value {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-red .kpi-value {
        background: linear-gradient(135deg, #f87171, #ef4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-blue .kpi-value {
        background: linear-gradient(135deg, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ===== Section Headers ===== */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.88);
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(139, 92, 246, 0.2);
        letter-spacing: -0.01em;
    }

    /* ===== Recommendation Cards ===== */
    .rec-card {
        background: linear-gradient(145deg, rgba(30, 27, 55, 0.85), rgba(20, 18, 40, 0.9));
        border: 1px solid rgba(139, 92, 246, 0.12);
        border-left: 4px solid;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .rec-card:hover {
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transform: translateX(4px);
    }
    .rec-card.priority-high {
        border-left-color: #ef4444;
    }
    .rec-card.priority-medium {
        border-left-color: #f59e0b;
    }
    .rec-card.priority-low {
        border-left-color: #10b981;
    }
    .rec-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.05rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.9);
    }
    .rec-card p {
        margin: 0;
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.65);
        line-height: 1.6;
    }
    .rec-card .priority-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 2px 8px;
        border-radius: 6px;
        margin-bottom: 0.5rem;
    }
    .rec-card.priority-high .priority-badge {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
    }
    .rec-card.priority-medium .priority-badge {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
    }

    /* ===== Mini KPI Row (for Task Audit tab) ===== */
    .mini-kpi {
        background: rgba(30, 27, 55, 0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(139, 92, 246, 0.15);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .mini-kpi:hover {
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
        transform: translateY(-2px);
    }
    .mini-kpi .mini-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #a78bfa;
        line-height: 1;
    }
    .mini-kpi .mini-label {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.2rem;
        font-weight: 600;
    }
    .mini-kpi.mini-green .mini-value { color: #34d399; }
    .mini-kpi.mini-amber .mini-value { color: #fbbf24; }
    .mini-kpi.mini-red .mini-value { color: #f87171; }
    .mini-kpi.mini-blue .mini-value { color: #60a5fa; }

    /* ===== Scorecard table ===== */
    .scorecard-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        font-size: 0.85rem;
    }
    .scorecard-table thead th {
        background: rgba(139, 92, 246, 0.12);
        color: rgba(255,255,255,0.7);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.72rem;
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 1px solid rgba(139, 92, 246, 0.15);
    }
    .scorecard-table tbody tr {
        transition: all 0.3s ease;
    }
    .scorecard-table tbody tr:hover {
        background: rgba(139, 92, 246, 0.15);
        transform: scale(1.01);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .scorecard-table tbody td {
        padding: 0.6rem 1rem;
        color: rgba(255,255,255,0.75);
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .scorecard-table .bar-cell {
        position: relative;
    }
    .scorecard-table .bar-bg {
        height: 6px;
        border-radius: 3px;
        background: rgba(255,255,255,0.06);
        position: relative;
    }
    .scorecard-table .bar-fill {
        height: 100%;
        border-radius: 3px;
        position: absolute;
        top: 0;
        left: 0;
    }
    .score-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
    }
    .score-high { background: rgba(16,185,129,0.15); color: #34d399; }
    .score-mid { background: rgba(245,158,11,0.15); color: #fbbf24; }
    .score-low { background: rgba(239,68,68,0.15); color: #f87171; }

    /* ===== Meeting drill-down ===== */
    .meeting-detail-card {
        background: linear-gradient(145deg, rgba(30, 27, 55, 0.9), rgba(20, 18, 40, 0.95));
        border: 1px solid rgba(139, 92, 246, 0.12);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* ===== Tab styling ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(20, 18, 40, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 6px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 16px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(139, 92, 246, 0.2) !important;
        box-shadow: inset 0 0 10px rgba(139, 92, 246, 0.1);
    }

    /* ===== Dataframe styling ===== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1e1b37 100%) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.1);
    }
    [data-testid="stSidebar"] h3 {
        background: linear-gradient(90deg, #a78bfa, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.1rem;
    }

    /* ===== KPI Fade-In Animation ===== */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .kpi-card {
        animation: fadeSlideUp 0.5s ease-out both;
    }
    .kpi-card:nth-child(1) { animation-delay: 0.05s; }
    .kpi-card:nth-child(2) { animation-delay: 0.1s; }
    .kpi-card:nth-child(3) { animation-delay: 0.15s; }
    .kpi-card:nth-child(4) { animation-delay: 0.2s; }
    .kpi-card:nth-child(5) { animation-delay: 0.25s; }
    .kpi-card:nth-child(6) { animation-delay: 0.3s; }

    .mini-kpi {
        animation: fadeSlideUp 0.4s ease-out both;
    }

    /* ===== Rec-card slide-in ===== */
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-16px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .rec-card {
        animation: slideInLeft 0.4s ease-out both;
    }
    .rec-card:nth-child(2) { animation-delay: 0.05s; }
    .rec-card:nth-child(3) { animation-delay: 0.1s; }
    .rec-card:nth-child(4) { animation-delay: 0.15s; }
    .rec-card:nth-child(5) { animation-delay: 0.2s; }

    /* ===== Plotly modebar refinement ===== */
    .modebar-btn {
        opacity: 0.3 !important;
    }
    .modebar-btn:hover {
        opacity: 0.8 !important;
    }

    /* ===== Hide Deploy button & Streamlit branding ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
</style>
"""
