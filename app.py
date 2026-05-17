"""
app.py — Interactive HOD Meeting Minutes Dashboard v2
Rashtriya Raksha University | Built with Streamlit + Plotly
Enhanced: Heatmap, Quarterly analysis, Scorecard, Meeting drill-down, Mini KPIs
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from analysis import (
    load_data, compute_macro_metrics, compute_department_analysis,
    compute_timeline_analysis, compute_quarterly_analysis,
    compute_heatmap_data, compute_department_scorecard,
    extract_top_keywords, generate_recommendations,
    compute_day_of_week_distribution, compute_meeting_productivity,
    compute_top_assignees,
)
from app_styles import CUSTOM_CSS

# ═══════════════════ Page Config ═══════════════════
st.set_page_config(
    page_title="RRU HOD Meeting Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ═══════════════════ Authentication ═══════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; margin-top: 100px; color: rgba(255,255,255,0.9);'>🔒 RRU HOD Dashboard Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Enter Password to Access Dashboard:", type="password")
        if st.button("Login", use_container_width=True):
            if pwd == "H0D@RRU##199":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Password. Please try again.")
    st.stop()

# ═══════════════════ Plotly Theme ═══════════════════
GC = 'rgba(255,255,255,0.05)'
COLORS = ['#c084fc', '#60a5fa', '#34d399', '#fbbf24', '#f472b6',
          '#a78bfa', '#818cf8', '#10b981', '#f59e0b', '#f87171',
          '#3b82f6', '#c084fc', '#e879f9', '#fb923c', '#9333ea']
PLT = dict(layout=dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='rgba(255,255,255,0.8)', size=12),
    margin=dict(l=40, r=20, t=40, b=40), colorway=COLORS,
))

STATUS_COLORS = {'Recorded':'#6366f1','Completed':'#10b981','In Progress':'#f59e0b','Pending':'#ef4444'}

# ═══════════════════ Data Loading ═══════════════════
@st.cache_data(ttl=3600)
def get_data():
    df = load_data()
    m = compute_macro_metrics(df)
    dept = compute_department_analysis(df)
    tl = compute_timeline_analysis(df)
    qt = compute_quarterly_analysis(df)
    hm = compute_heatmap_data(df)
    sc = compute_department_scorecard(dept)
    kw = extract_top_keywords(df)
    recs = generate_recommendations(df, dept, tl)
    dow = compute_day_of_week_distribution(df)
    prod = compute_meeting_productivity(df)
    top_a = compute_top_assignees(df)
    return df, m, dept, tl, qt, hm, sc, kw, recs, dow, prod, top_a

df, metrics, dept_stats, timeline, quarterly, heatmap, scorecard, keywords, recs, day_of_week, productivity, top_assignees = get_data()

# ═══════════════════ Sidebar ═══════════════════
with st.sidebar:
    st.markdown("### 📋 Pipeline Summary")
    st.markdown(f"""
    <div style="font-size:0.85rem;color:rgba(255,255,255,0.6);line-height:1.8;">
        <strong style="color:rgba(255,255,255,0.8);">Data Source</strong><br>
        {metrics['total_meetings']} meetings parsed<br>
        {metrics['total_tasks']:,} action items extracted<br><br>
        <strong style="color:rgba(255,255,255,0.8);">Date Range</strong><br>
        {metrics['date_range_start']} → {metrics['date_range_end']}<br><br>
        <strong style="color:rgba(255,255,255,0.8);">Avg. Meeting Gap</strong><br>
        {metrics['avg_meeting_gap_days']} days<br><br>
        <strong style="color:rgba(255,255,255,0.8);">Format Distribution</strong><br>
        {'<br>'.join(f"Format {k}: {v} items" for k, v in metrics['format_counts'].items())}<br><br>
        <strong style="color:rgba(255,255,255,0.8);">Departments Tracked</strong><br>
        {metrics['active_departments']} unique units/persons
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<p style='font-size:0.75rem;color:rgba(255,255,255,0.25);'>Last updated: {pd.Timestamp.now().strftime('%d %B %Y %H:%M')}</p>",
                unsafe_allow_html=True)

# ═══════════════════ Header ═══════════════════
st.markdown("""
<div class="dashboard-header">
    <h1>🏛️ RRU HOD Meeting Insights Dashboard</h1>
    <p>Rashtriya Raksha University — Heads of Department Meeting Analytics &bull; {s} to {e} &bull; {m} Meetings &bull; {t:,} Action Items</p>
</div>
""".format(s=metrics['date_range_start'], e=metrics['date_range_end'],
           m=metrics['total_meetings'], t=metrics['total_tasks']), unsafe_allow_html=True)

# ═══════════════════ Tabs ═══════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Macro Overview", "📈 Analytics & Trends",
    "🔍 Task Audit", "🧠 Strategy & Recommendations",
])

# ══════════════ TAB 1: Macro Overview ══════════════
with tab1:
    # KPI Row
    cols = st.columns(6)
    kpis = [
        (metrics['total_meetings'], 'Meetings', f"{metrics['date_range_start'][:4]}–{metrics['date_range_end'][:4]}", ''),
        (f"{metrics['total_tasks']:,}", 'Total Tasks', f"~{metrics['avg_tasks_per_meeting']} per meeting", ''),
        (metrics['completed'], 'Completed', 'Tasks with done status', 'kpi-green'),
        (metrics['in_progress'], 'In Progress', 'Currently active', 'kpi-amber'),
        (metrics['pending'], 'Pending', 'Needs follow-up', 'kpi-red'),
        (f"{metrics['completion_rate']}%", 'Completion Rate', 'Of actionable tasks', 'kpi-blue'),
    ]
    for col, (v, l, s, cls) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-value">{v}</div>'
                        f'<div class="kpi-label">{l}</div><div class="kpi-sub">{s}</div></div>',
                        unsafe_allow_html=True)
    st.markdown("")

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="section-header">📅 Meeting Activity Over Time</div>', unsafe_allow_html=True)
        tl = timeline[timeline['year_month'] != 'NaT'].copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=tl['year_month'], y=tl['total_tasks'], name='Total Tasks',
                             marker_color='rgba(139,92,246,0.5)', marker_line_color='rgba(167,139,250,0.8)', marker_line_width=1))
        fig.add_trace(go.Scatter(x=tl['year_month'], y=tl['meetings'], name='Meetings', yaxis='y2',
                                 mode='lines+markers', line=dict(color='#34d399', width=2), marker=dict(size=5)))
        fig.update_layout(**PLT['layout'], height=350,
                          yaxis=dict(title='Tasks', gridcolor=GC),
                          yaxis2=dict(title='Meetings', overlaying='y', side='right', gridcolor=GC),
                          legend=dict(orientation='h', y=1.1, x=0, font=dict(size=11)))
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown('<div class="section-header">📊 Task Status Distribution</div>', unsafe_allow_html=True)
        sdf = df['task_status'].value_counts().reset_index()
        sdf.columns = ['Status', 'Count']
        fig = go.Figure(go.Pie(
            labels=sdf['Status'], values=sdf['Count'], hole=0.55,
            marker=dict(colors=[STATUS_COLORS.get(s, '#a78bfa') for s in sdf['Status']]),
            textinfo='label+percent', textposition='outside', textfont=dict(size=12), pull=[0.03]*len(sdf)))
        fig.update_layout(**PLT['layout'], height=350, showlegend=False,
            annotations=[dict(text=f"<b>{metrics['total_tasks']:,}</b><br><span style='font-size:11px;color:rgba(255,255,255,0.4)'>Total</span>",
                              x=0.5, y=0.5, font_size=20, showarrow=False, font=dict(color='rgba(255,255,255,0.8)'))])
        st.plotly_chart(fig, width='stretch')

    # Heatmap — Year x Month activity
    st.markdown('<div class="section-header">🗓️ Activity Heatmap — Tasks by Year × Month</div>', unsafe_allow_html=True)
    hm = heatmap.copy()
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    # Ensure all 12 months exist
    for m in month_names:
        if m not in hm.columns:
            hm[m] = 0
    hm = hm[month_names]

    fig = go.Figure(go.Heatmap(
        z=hm.values, x=month_names, y=[str(y) for y in hm.index],
        colorscale=[[0, 'rgba(15,12,41,0.9)'], [0.25, '#312e81'], [0.5, '#6366f1'], [0.75, '#a78bfa'], [1, '#c4b5fd']],
        hovertemplate='%{y} %{x}: <b>%{z} tasks</b><extra></extra>',
        texttemplate='%{z}', textfont=dict(size=11, color='rgba(255,255,255,0.7)'),
    ))
    fig.update_layout(**PLT['layout'], height=280, yaxis=dict(autorange='reversed'),
                      xaxis=dict(side='top', gridcolor=GC))
    st.plotly_chart(fig, width='stretch')

    # Year-over-Year & Day-of-Week row
    yc1, yc2 = st.columns([3, 2])
    with yc1:
        st.markdown('<div class="section-header">📆 Year-over-Year Breakdown</div>', unsafe_allow_html=True)
        yr = df[df['year'] > 0].groupby('year').agg(
            meetings=('meeting_number','nunique'), tasks=('task_status','count'),
            completed=('task_status', lambda x: (x=='Completed').sum()),
            in_progress=('task_status', lambda x: (x=='In Progress').sum()),
            pending=('task_status', lambda x: (x=='Pending').sum()),
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=yr['year'], y=yr['completed'], name='Completed', marker_color='#10b981'))
        fig.add_trace(go.Bar(x=yr['year'], y=yr['in_progress'], name='In Progress', marker_color='#f59e0b'))
        fig.add_trace(go.Bar(x=yr['year'], y=yr['pending'], name='Pending', marker_color='#ef4444'))
        fig.add_trace(go.Bar(x=yr['year'], y=yr['tasks']-yr['completed']-yr['in_progress']-yr['pending'],
                             name='Recorded', marker_color='rgba(99,102,241,0.5)'))
        fig.update_layout(**PLT['layout'], barmode='stack', height=350,
                          xaxis=dict(title='Year', dtick=1, gridcolor=GC), yaxis=dict(title='Tasks', gridcolor=GC),
                          legend=dict(orientation='h', y=1.12, x=0, font=dict(size=11)))
        st.plotly_chart(fig, width='stretch')

    with yc2:
        st.markdown('<div class="section-header">📅 Day-of-Week Distribution</div>', unsafe_allow_html=True)
        dow = day_of_week.copy()
        # Radar / polar chart for day distribution
        r_vals = dow['meetings'].tolist() + [dow['meetings'].iloc[0]]  # close the polygon
        theta_vals = dow['day'].tolist() + [dow['day'].iloc[0]]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=r_vals, theta=theta_vals, fill='toself', name='Meetings',
            line=dict(color='#a78bfa', width=2), fillcolor='rgba(139,92,246,0.15)',
        ))
        fig.update_layout(**PLT['layout'], height=350,
                          polar=dict(
                              bgcolor='rgba(0,0,0,0)',
                              radialaxis=dict(visible=True, gridcolor='rgba(255,255,255,0.06)',
                                              tickfont=dict(size=10, color='rgba(255,255,255,0.4)')),
                              angularaxis=dict(gridcolor='rgba(255,255,255,0.06)',
                                               tickfont=dict(size=11, color='rgba(255,255,255,0.6)')),
                          ), showlegend=False)
        st.plotly_chart(fig, width='stretch')

# ══════════════ TAB 2: Analytics & Trends ══════════════
with tab2:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="section-header">🏢 Top 20 Departments by Task Volume</div>', unsafe_allow_html=True)
        td = dept_stats.head(20)
        fig = go.Figure()
        for name, col, clr in [('Completed','completed','#10b981'),('In Progress','in_progress','#f59e0b'),
                                ('Pending','pending','#ef4444'),('Recorded','recorded','rgba(99,102,241,0.4)')]:
            fig.add_trace(go.Bar(y=td['department_group'], x=td[col], name=name, orientation='h', marker_color=clr))
        fig.update_layout(**PLT['layout'], barmode='stack', height=600,
                          yaxis=dict(autorange='reversed', gridcolor=GC), xaxis=dict(title='Tasks', gridcolor=GC),
                          legend=dict(orientation='h', y=1.05, x=0, font=dict(size=11)))
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown('<div class="section-header">🎯 Completion Efficiency by Department</div>', unsafe_allow_html=True)
        ed = dept_stats[dept_stats['actionable'] >= 3].nlargest(15, 'actionable')
        fig = go.Figure(go.Bar(
            y=ed['department_group'], x=ed['completion_pct'], orientation='h',
            marker=dict(color=ed['completion_pct'], colorscale=[[0,'#ef4444'],[0.5,'#f59e0b'],[1,'#10b981']], cmin=0, cmax=100),
            text=ed['completion_pct'].apply(lambda x: f'{x:.0f}%'), textposition='auto', textfont=dict(size=11, color='white')))
        fig.update_layout(**PLT['layout'], height=500,
                          yaxis=dict(autorange='reversed', gridcolor=GC), xaxis=dict(title='Completion %', range=[0,110], gridcolor=GC))
        fig.add_vline(x=50, line_dash='dash', line_color='rgba(255,255,255,0.2)')
        st.plotly_chart(fig, width='stretch')

    # Quarter-over-Quarter comparison
    st.markdown('<div class="section-header">📊 Quarter-over-Quarter Comparison</div>', unsafe_allow_html=True)
    qt = quarterly.copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=qt['year_quarter'], y=qt['total_tasks'], name='Tasks', marker_color='rgba(139,92,246,0.5)',
                         marker_line_color='rgba(167,139,250,0.8)', marker_line_width=1))
    fig.add_trace(go.Scatter(x=qt['year_quarter'], y=qt['efficiency'], name='Efficiency %', yaxis='y2',
                             mode='lines+markers', line=dict(color='#34d399', width=2.5), marker=dict(size=6)))
    fig.update_layout(**PLT['layout'], height=340,
                      yaxis=dict(title='Total Tasks', gridcolor=GC),
                      yaxis2=dict(title='Efficiency %', overlaying='y', side='right', range=[0,110], gridcolor=GC),
                      legend=dict(orientation='h', y=1.1, x=0, font=dict(size=11)))
    st.plotly_chart(fig, width='stretch')

    # Trendline
    st.markdown('<div class="section-header">📈 Task Completion Efficiency Trendline</div>', unsafe_allow_html=True)
    tc = timeline[timeline['year_month'] != 'NaT'].copy()
    tc['eff_rolling'] = tc['efficiency'].rolling(3, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tc['year_month'], y=tc['efficiency'], mode='markers', name='Monthly',
                             marker=dict(color='rgba(167,139,250,0.5)', size=6)))
    fig.add_trace(go.Scatter(x=tc['year_month'], y=tc['eff_rolling'], mode='lines', name='3-Month Avg',
                             line=dict(color='#a78bfa', width=3)))
    fig.update_layout(**PLT['layout'], height=300,
                      yaxis=dict(title='Completion %', range=[0,110], gridcolor=GC),
                      xaxis=dict(title='Month', gridcolor=GC),
                      legend=dict(orientation='h', y=1.1, x=0, font=dict(size=11)))
    fig.add_hline(y=50, line_dash='dash', line_color='rgba(255,255,255,0.15)',
                  annotation_text='50% threshold', annotation_position='bottom right',
                  annotation_font=dict(color='rgba(255,255,255,0.3)', size=10))
    st.plotly_chart(fig, width='stretch')

    # Meeting Productivity & Top Assignees row
    pc1, pc2 = st.columns([1, 1])
    with pc1:
        st.markdown('<div class="section-header">📊 Meeting Productivity (Tasks per Meeting)</div>', unsafe_allow_html=True)
        prod = productivity.copy()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prod['meeting_date'], y=prod['tasks'], mode='markers',
            marker=dict(size=prod['departments'].clip(3, 20), color=prod['tasks'],
                        colorscale=[[0,'rgba(99,102,241,0.3)'],[1,'#a78bfa']],
                        line=dict(width=0.5, color='rgba(255,255,255,0.2)')),
            text=prod.apply(lambda r: f"Meeting #{r['meeting_number']}<br>{r['tasks']} tasks, {r['departments']} depts", axis=1),
            hoverinfo='text', name='Meetings',
        ))
        # Rolling average line
        prod['tasks_rolling'] = prod['tasks'].rolling(10, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=prod['meeting_date'], y=prod['tasks_rolling'], mode='lines', name='10-Meeting Avg',
            line=dict(color='#34d399', width=2, dash='dot'),
        ))
        fig.update_layout(**PLT['layout'], height=400,
                          xaxis=dict(title='Date', gridcolor=GC),
                          yaxis=dict(title='Tasks per Meeting', gridcolor=GC),
                          legend=dict(orientation='h', y=1.1, x=0, font=dict(size=11)))
        st.plotly_chart(fig, width='stretch')

    with pc2:
        st.markdown('<div class="section-header">👤 Top Assignees by Task Volume</div>', unsafe_allow_html=True)
        ta = top_assignees.copy().sort_values('tasks', ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=ta['department_group'], x=ta['completed'], name='Completed',
            orientation='h', marker_color='#10b981',
        ))
        fig.add_trace(go.Bar(
            y=ta['department_group'], x=ta['in_progress'], name='In Progress',
            orientation='h', marker_color='#f59e0b',
        ))
        fig.add_trace(go.Bar(
            y=ta['department_group'], x=ta['pending'], name='Pending',
            orientation='h', marker_color='#ef4444',
        ))
        fig.add_trace(go.Bar(
            y=ta['department_group'], x=ta['tasks'] - ta['completed'] - ta['in_progress'] - ta['pending'],
            name='Recorded', orientation='h', marker_color='rgba(99,102,241,0.4)',
        ))
        fig.update_layout(**PLT['layout'], barmode='stack', height=400,
                          xaxis=dict(title='Tasks Assigned', gridcolor=GC), yaxis=dict(gridcolor=GC),
                          legend=dict(orientation='h', y=1.08, x=0, font=dict(size=11)))
        st.plotly_chart(fig, width='stretch')

    # Keywords
    st.markdown('<div class="section-header">🔤 Most Discussed Topics (TF-IDF Analysis)</div>', unsafe_allow_html=True)
    if keywords:
        kdf = pd.DataFrame(keywords[:25], columns=['Topic','Score']).sort_values('Score', ascending=True)
        fig = go.Figure(go.Bar(y=kdf['Topic'], x=kdf['Score'], orientation='h',
                               marker=dict(color=kdf['Score'], colorscale=[[0,'rgba(99,102,241,0.3)'],[1,'#a78bfa']])))
        fig.update_layout(**PLT['layout'], height=550,
                          xaxis=dict(title='TF-IDF Relevance Score', gridcolor=GC), yaxis=dict(gridcolor=GC))
        st.plotly_chart(fig, width='stretch')

# ══════════════ TAB 3: Task Audit ══════════════
with tab3:
    st.markdown('<div class="section-header">🔍 Task Audit & Follow-Up Tracker</div>', unsafe_allow_html=True)

    # Filters
    cf1, cf2, cf3, cf4 = st.columns([1.5, 1.5, 1, 1])
    with cf1:
        status_f = st.multiselect("Filter by Status", ['Completed','In Progress','Pending','Recorded'],
                                  default=['Pending','In Progress'], key='as')
    with cf2:
        dept_f = st.multiselect("Filter by Department", dept_stats['department_group'].tolist(), default=[], key='ad')
    with cf3:
        year_f = st.multiselect("Filter by Year", sorted(df[df['year']>0]['year'].unique().tolist()), default=[], key='ay')
    with cf4:
        search = st.text_input("🔎 Search Tasks", "", key='ax')

    filt = df.copy()
    if status_f: filt = filt[filt['task_status'].isin(status_f)]
    if dept_f: filt = filt[filt['department_group'].isin(dept_f)]
    if year_f: filt = filt[filt['year'].isin(year_f)]
    if search: filt = filt[filt['task_description'].str.contains(search, case=False, na=False)]

    # Mini KPIs for filtered data
    fc = filt['task_status'].value_counts()
    mk = st.columns(5)
    mini_data = [
        (f"{len(filt):,}", 'Matching', ''),
        (str(fc.get('Completed',0)), 'Completed', 'mini-green'),
        (str(fc.get('In Progress',0)), 'In Progress', 'mini-amber'),
        (str(fc.get('Pending',0)), 'Pending', 'mini-red'),
        (str(filt['meeting_number'].nunique()), 'Meetings', 'mini-blue'),
    ]
    for col, (v, l, cls) in zip(mk, mini_data):
        with col:
            st.markdown(f'<div class="mini-kpi {cls}"><div class="mini-value">{v}</div>'
                        f'<div class="mini-label">{l}</div></div>', unsafe_allow_html=True)
    st.markdown("")

    # Table
    dcols = ['meeting_number','meeting_date','sr_no','task_description','concerned_unit','task_status','source_file']
    ddf = filt[dcols].copy()
    ddf['meeting_date'] = ddf['meeting_date'].dt.strftime('%Y-%m-%d').fillna('N/A')
    ddf.columns = ['Meeting #','Date','Sr. No.','Task Description','Responsible Unit/Person','Status','Source File']

    st.dataframe(ddf, use_container_width=True, height=500,
                 column_config={
                     'Meeting #': st.column_config.NumberColumn(width='small'),
                     'Date': st.column_config.TextColumn(width='small'),
                     'Sr. No.': st.column_config.TextColumn(width='small'),
                     'Task Description': st.column_config.TextColumn(width='large'),
                     'Responsible Unit/Person': st.column_config.TextColumn(width='medium'),
                     'Status': st.column_config.TextColumn(width='small'),
                     'Source File': st.column_config.TextColumn(width='medium'),
                 })

    st.download_button("📥 Download Filtered Data as CSV",
                       ddf.to_csv(index=False).encode('utf-8-sig'),
                       "hod_task_audit.csv", "text/csv")

    # Meeting Drill-Down
    st.markdown('<div class="section-header">📋 Meeting Drill-Down</div>', unsafe_allow_html=True)
    meeting_nums = sorted(df['meeting_number'].unique().tolist())
    selected_meeting = st.selectbox("Select Meeting Number", meeting_nums,
                                    index=len(meeting_nums)-1, key='meeting_dd')
    mdf = df[df['meeting_number'] == selected_meeting]
    if not mdf.empty:
        mdate = mdf['meeting_date'].iloc[0]
        mdate_str = mdate.strftime('%d %B %Y') if pd.notna(mdate) else 'N/A'
        mc = mdf['task_status'].value_counts()
        st.markdown(f"""
        <div class="meeting-detail-card">
            <h4 style="color:rgba(255,255,255,0.9);margin:0 0 0.5rem 0;">Meeting #{selected_meeting} — {mdate_str}</h4>
            <p style="color:rgba(255,255,255,0.5);margin:0;font-size:0.9rem;">
                <strong>{len(mdf)}</strong> tasks &bull;
                <span style="color:#10b981">{mc.get('Completed',0)} completed</span> &bull;
                <span style="color:#f59e0b">{mc.get('In Progress',0)} in progress</span> &bull;
                <span style="color:#ef4444">{mc.get('Pending',0)} pending</span> &bull;
                Source: {mdf['source_file'].iloc[0]}
            </p>
        </div>""", unsafe_allow_html=True)

        mdisp = mdf[['sr_no','task_description','concerned_unit','task_status']].copy()
        mdisp.columns = ['Sr. No.','Task Description','Responsible','Status']
        st.dataframe(mdisp, use_container_width=True, height=300)

# ══════════════ TAB 4: Strategy & Recommendations ══════════════
with tab4:
    st.markdown('<div class="section-header">🧠 Data-Driven Strategic Recommendations</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin-bottom: 1.5rem;">
        The following recommendations are generated automatically from statistical analysis of
        <strong>{:,}</strong> meeting records spanning <strong>{}</strong> to <strong>{}</strong>.
        They identify systemic bottlenecks, workload imbalances, and process improvements.
    </p>""".format(metrics['total_tasks'], metrics['date_range_start'], metrics['date_range_end']),
    unsafe_allow_html=True)

    for rec in recs:
        pc = f"priority-{rec['priority'].lower()}"
        st.markdown(f"""
        <div class="rec-card {pc}">
            <div class="priority-badge">{rec['priority']} Priority</div>
            <h4>{rec['title']}</h4>
            <p>{rec['description']}</p>
        </div>""", unsafe_allow_html=True)

    # Department Performance Scorecard
    st.markdown('<div class="section-header">🏆 Department Performance Scorecard</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin-bottom:1rem;">'
                'Composite score = 40% completion rate + 30% task volume + 30% meeting engagement</p>',
                unsafe_allow_html=True)

    # Build HTML table
    rows_html = ""
    for s in scorecard:
        # Color the score badge
        if s['composite_score'] >= 70: scls = 'score-high'
        elif s['composite_score'] >= 50: scls = 'score-mid'
        else: scls = 'score-low'

        # Completion bar
        bar_color = '#10b981' if s['completion_pct'] >= 70 else '#f59e0b' if s['completion_pct'] >= 50 else '#ef4444'
        bar_w = min(s['completion_pct'], 100)

        rows_html += f"""<tr>
            <td style="font-weight:600;color:rgba(255,255,255,0.85)">{s['department']}</td>
            <td>{s['total_tasks']}</td>
            <td style="color:#10b981">{s['completed']}</td>
            <td style="color:#f59e0b">{s['in_progress']}</td>
            <td style="color:#ef4444">{s['pending']}</td>
            <td class="bar-cell">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div class="bar-bg" style="width:80px;"><div class="bar-fill" style="width:{bar_w}%;background:{bar_color}"></div></div>
                    <span style="font-size:0.8rem">{s['completion_pct']}%</span>
                </div>
            </td>
            <td>{s['meetings_involved']}</td>
            <td><span class="score-badge {scls}">{s['composite_score']}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="scorecard-table">
        <thead><tr>
            <th>Department</th><th>Tasks</th><th>Done</th><th>Active</th><th>Pending</th>
            <th>Completion</th><th>Meetings</th><th>Score</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown("")

    # Supporting charts
    st.markdown('<div class="section-header">📊 Supporting Data</div>', unsafe_allow_html=True)
    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown("#### Meeting Frequency Distribution")
        vd = df[df['meeting_date'].notna()]
        if not vd.empty:
            md = vd.groupby('meeting_number')['meeting_date'].first().sort_values()
            gaps = md.diff().dt.days.dropna()
            fig = go.Figure(go.Histogram(x=gaps, nbinsx=30, marker_color='rgba(139,92,246,0.6)',
                                         marker_line_color='rgba(167,139,250,0.8)', marker_line_width=1))
            fig.update_layout(**PLT['layout'], height=300,
                              xaxis=dict(title='Days Between Meetings', gridcolor=GC),
                              yaxis=dict(title='Frequency', gridcolor=GC))
            fig.add_vline(x=gaps.mean(), line_dash='dash', line_color='#a78bfa',
                          annotation_text=f'Avg: {gaps.mean():.0f}d', annotation_position='top',
                          annotation_font=dict(color='#a78bfa', size=11))
            st.plotly_chart(fig, width='stretch')

    with cs2:
        st.markdown("#### Department Workload Concentration")
        t10 = dept_stats.head(10)
        other = dept_stats['total_tasks'].sum() - t10['total_tasks'].sum()
        fig = go.Figure(go.Pie(
            labels=t10['department_group'].tolist()+['Others'],
            values=t10['total_tasks'].tolist()+[other], hole=0.4,
            marker=dict(colors=COLORS[:10]+['#475569']),
            textinfo='label+percent', textposition='outside', textfont=dict(size=10)))
        fig.update_layout(**PLT['layout'], height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch')

# ═══════════════════ Footer ═══════════════════
st.markdown("---")
st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,0.25);font-size:0.8rem;'>"
            f"RRU HOD Meeting Dashboard v2 &bull; {metrics['total_tasks']:,} tasks from "
            f"{metrics['total_meetings']} meetings &bull; Last updated: {pd.Timestamp.now().strftime('%d %B %Y')}</p>",
            unsafe_allow_html=True)
