"""
analysis.py — Data analysis and auditing module for HOD Meeting Minutes.
Processes the structured CSV and generates analysis results for the dashboard.
v2: Enhanced with heatmap data, quarterly comparisons, department scorecards,
    and richer recommendation engine.
"""
import pandas as pd
import numpy as np
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer


def load_data(csv_path: str = "meetings_data.csv") -> pd.DataFrame:
    """Load and preprocess the meetings data."""
    df = pd.read_csv(csv_path)
    
    # Clean and type-cast
    df['meeting_number'] = pd.to_numeric(df['meeting_number'], errors='coerce').fillna(0).astype(int)
    df['meeting_date'] = pd.to_datetime(df['meeting_date'], errors='coerce')
    df['year'] = df['meeting_date'].dt.year.fillna(0).astype(int)
    df['month'] = df['meeting_date'].dt.month.fillna(0).astype(int)
    df['quarter'] = df['meeting_date'].dt.quarter.fillna(0).astype(int)
    df['year_quarter'] = df.apply(
        lambda r: f"{r['year']}-Q{r['quarter']}" if r['year'] > 0 and r['quarter'] > 0 else 'Unknown',
        axis=1
    )
    df['year_month'] = df['meeting_date'].dt.to_period('M').astype(str)
    df['day_of_week'] = df['meeting_date'].dt.day_name().fillna('Unknown')
    df['week_of_year'] = df['meeting_date'].dt.isocalendar().week.fillna(0).astype(int)
    
    # Normalize concerned_unit
    df['concerned_unit'] = df['concerned_unit'].fillna('Not Specified').str.strip()
    df.loc[df['concerned_unit'] == '', 'concerned_unit'] = 'Not Specified'
    
    # Clean bullet/dot prefixes from concerned_unit
    df['concerned_unit'] = df['concerned_unit'].apply(
        lambda x: re.sub(r'^[·•\-–]\s*', '', x).strip() if isinstance(x, str) else x
    )
    
    # Standardize department names for grouping
    df['department_group'] = df['concerned_unit'].apply(normalize_department)
    
    # Task description length (proxy for detail/complexity)
    df['desc_length'] = df['task_description'].fillna('').str.len()
    
    return df


def normalize_department(name: str) -> str:
    """Normalize department/person names for consistent grouping."""
    if not isinstance(name, str) or name.strip() == '' or name == 'Not Specified':
        return 'Not Specified'
    
    name = name.strip()
    
    # Remove common academic/military titles to unify names
    name = re.sub(r'^(Dr|Prof|Mr|Ms|Mrs|Lt\sGen|Col|Brig|Shri)\.?\s+', '', name, flags=re.IGNORECASE)
    name = name.replace('.', ' ').replace('  ', ' ').strip()
    
    # Known department mappings
    mappings = {
        'Pro VC': ['pro vc', 'provc', 'pro-vc', 'pvc'],
        'University Dean': ['university dean', 'dean office', 'dean r&p', 'dean r&p'],
        'Registrar': ['registrar'],
        'All School Directors': ['all school director', 'all director', 'all school directors'],
        'Finance': ['director-finance', 'finance', 'director finance'],
        'HR Branch': ['ar-hr', 'hr branch', 'hr'],
        'ICTB/IT': ['head-ictb', 'ict', 'it branch', 'director-sitaics', 'sitaics'],
        'SPICSM': ['director-spicsm', 'spicsm'],
        'SISDSS': ['director sisdss', 'sisdss', 'director-sisdss'],
        'Campus Development': ['director- campus development', 'campus development', 'director-campus'],
        'Procurement': ['ar-procurement', 'procurement'],
        'RSS': ['rss principal', 'rss'],
        'Exam Branch': ['exam', 'controller of exam', 'coe'],
    }
    
    name_lower = name.lower()
    for group, keywords in mappings.items():
        for kw in keywords:
            if kw in name_lower:
                return group
    
    # Capitalize cleanly
    name = name.title()
    
    # If name is short enough, use as-is (likely a person name)
    if len(name) <= 40:
        return name
    
    # Truncate very long names
    return name[:40]


def compute_macro_metrics(df: pd.DataFrame) -> dict:
    """Compute high-level KPI metrics."""
    total_meetings = df['meeting_number'].nunique()
    total_tasks = len(df)
    
    # Status distribution
    status_counts = df['task_status'].value_counts().to_dict()
    completed = status_counts.get('Completed', 0)
    in_progress = status_counts.get('In Progress', 0)
    pending = status_counts.get('Pending', 0)
    recorded = status_counts.get('Recorded', 0)
    
    # Completion rate (completed / total non-Recorded)
    actionable = completed + in_progress + pending
    completion_rate = (completed / actionable * 100) if actionable > 0 else 0
    
    # Date range
    valid_dates = df[df['meeting_date'].notna()]
    date_min = valid_dates['meeting_date'].min()
    date_max = valid_dates['meeting_date'].max()
    
    # Active departments
    active_depts = df['department_group'].nunique()
    
    # Average tasks per meeting
    avg_tasks = total_tasks / total_meetings if total_meetings > 0 else 0
    
    # Meeting gaps
    meeting_dates = valid_dates.groupby('meeting_number')['meeting_date'].first().sort_values()
    gaps = meeting_dates.diff().dt.days.dropna()
    avg_gap = gaps.mean() if len(gaps) > 0 else 0
    
    # Format detection
    format_counts = df['format_type'].value_counts().to_dict()
    
    return {
        'total_meetings': total_meetings,
        'total_tasks': total_tasks,
        'completed': completed,
        'in_progress': in_progress,
        'pending': pending,
        'recorded': recorded,
        'actionable': actionable,
        'completion_rate': round(completion_rate, 1),
        'date_range_start': str(date_min.date()) if pd.notna(date_min) else 'N/A',
        'date_range_end': str(date_max.date()) if pd.notna(date_max) else 'N/A',
        'active_departments': active_depts,
        'avg_tasks_per_meeting': round(avg_tasks, 1),
        'avg_meeting_gap_days': round(avg_gap, 1),
        'format_counts': format_counts,
    }


def compute_department_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute task distribution and completion rates by department."""
    dept_stats = df.groupby('department_group').agg(
        total_tasks=('task_status', 'count'),
        completed=('task_status', lambda x: (x == 'Completed').sum()),
        in_progress=('task_status', lambda x: (x == 'In Progress').sum()),
        pending=('task_status', lambda x: (x == 'Pending').sum()),
        recorded=('task_status', lambda x: (x == 'Recorded').sum()),
        meetings_involved=('meeting_number', 'nunique'),
        avg_desc_length=('desc_length', 'mean'),
    ).reset_index()
    
    dept_stats['actionable'] = dept_stats['completed'] + dept_stats['in_progress'] + dept_stats['pending']
    dept_stats['completion_pct'] = np.where(
        dept_stats['actionable'] > 0,
        (dept_stats['completed'] / dept_stats['actionable'] * 100).round(1),
        0
    )
    dept_stats['avg_desc_length'] = dept_stats['avg_desc_length'].round(0).astype(int)
    
    return dept_stats.sort_values('total_tasks', ascending=False)


def compute_timeline_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute task trends over time."""
    valid = df[df['meeting_date'].notna()].copy()
    
    timeline = valid.groupby('year_month').agg(
        meetings=('meeting_number', 'nunique'),
        total_tasks=('task_status', 'count'),
        completed=('task_status', lambda x: (x == 'Completed').sum()),
        in_progress=('task_status', lambda x: (x == 'In Progress').sum()),
        pending=('task_status', lambda x: (x == 'Pending').sum()),
    ).reset_index()
    
    timeline['actionable'] = timeline['completed'] + timeline['in_progress'] + timeline['pending']
    timeline['efficiency'] = np.where(
        timeline['actionable'] > 0,
        (timeline['completed'] / timeline['actionable'] * 100).round(1),
        0
    )
    
    return timeline


def compute_quarterly_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute quarter-over-quarter comparison."""
    valid = df[(df['meeting_date'].notna()) & (df['year'] > 0)].copy()
    
    quarterly = valid.groupby('year_quarter').agg(
        meetings=('meeting_number', 'nunique'),
        total_tasks=('task_status', 'count'),
        completed=('task_status', lambda x: (x == 'Completed').sum()),
        in_progress=('task_status', lambda x: (x == 'In Progress').sum()),
        pending=('task_status', lambda x: (x == 'Pending').sum()),
        depts_active=('department_group', 'nunique'),
    ).reset_index()
    
    quarterly['actionable'] = quarterly['completed'] + quarterly['in_progress'] + quarterly['pending']
    quarterly['efficiency'] = np.where(
        quarterly['actionable'] > 0,
        (quarterly['completed'] / quarterly['actionable'] * 100).round(1),
        0
    )
    quarterly['avg_tasks_per_meeting'] = (quarterly['total_tasks'] / quarterly['meetings'].clip(lower=1)).round(1)
    
    return quarterly


def compute_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Generate a year x month heatmap of meeting activity."""
    valid = df[(df['meeting_date'].notna()) & (df['year'] > 0)].copy()
    
    heatmap = valid.groupby(['year', 'month']).agg(
        task_count=('task_status', 'count'),
    ).reset_index()
    
    # Pivot to year x month matrix
    pivot = heatmap.pivot_table(index='year', columns='month', values='task_count', fill_value=0)
    pivot.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:len(pivot.columns)]
    
    return pivot


def compute_department_scorecard(dept_stats: pd.DataFrame, top_n: int = 15) -> list[dict]:
    """Build a department performance scorecard with composite scores."""
    top_depts = dept_stats[dept_stats['total_tasks'] >= 5].head(top_n).copy()
    scorecard = []
    
    for _, row in top_depts.iterrows():
        # Composite score: weighted (completion rate 40%, volume breadth 30%, engagement 30%)
        comp_score = row['completion_pct'] * 0.4
        # Volume relative to max
        vol_ratio = min(row['total_tasks'] / max(top_depts['total_tasks'].max(), 1) * 100, 100)
        comp_score += vol_ratio * 0.3
        # Meetings involved relative to max
        meeting_ratio = min(row['meetings_involved'] / max(top_depts['meetings_involved'].max(), 1) * 100, 100)
        comp_score += meeting_ratio * 0.3
        
        scorecard.append({
            'department': row['department_group'],
            'total_tasks': int(row['total_tasks']),
            'completed': int(row['completed']),
            'pending': int(row['pending']),
            'in_progress': int(row['in_progress']),
            'completion_pct': row['completion_pct'],
            'meetings_involved': int(row['meetings_involved']),
            'composite_score': round(comp_score, 1),
        })
    
    scorecard.sort(key=lambda x: x['composite_score'], reverse=True)
    return scorecard


def extract_top_keywords(df: pd.DataFrame, n_keywords: int = 30) -> list[tuple]:
    """Extract most important keywords/topics using TF-IDF."""
    texts = df['task_description'].dropna().tolist()
    
    stop_words = [
        'the', 'and', 'for', 'that', 'with', 'will', 'are', 'was', 'has',
        'have', 'been', 'all', 'from', 'this', 'their', 'should', 'shall',
        'would', 'which', 'who', 'also', 'not', 'regarding', 'about',
        'sir', 'suggested', 'resolved', 'hod', 'meeting', 'discussed',
        'university', 'rru', 'campus', 'informed', 'said', 'asked',
        'regarding', 'office', 'per', 'can', 'may', 'one', 'new',
    ]
    
    tfidf = TfidfVectorizer(
        max_features=200,
        stop_words=stop_words + list(TfidfVectorizer(stop_words='english').get_stop_words()),
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.7,
    )
    
    try:
        tfidf_matrix = tfidf.fit_transform(texts)
        feature_names = tfidf.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        word_scores = list(zip(feature_names, scores))
        word_scores.sort(key=lambda x: x[1], reverse=True)
        return word_scores[:n_keywords]
    except Exception:
        return []


def generate_recommendations(df: pd.DataFrame, dept_stats: pd.DataFrame, timeline: pd.DataFrame) -> list[dict]:
    """Generate strategic recommendations based on data analysis."""
    recommendations = []
    
    # 1. Top departments with pending tasks
    high_pending = dept_stats[dept_stats['pending'] > 2].nlargest(5, 'pending')
    if not high_pending.empty:
        top_pending_depts = ', '.join(high_pending['department_group'].tolist()[:3])
        recommendations.append({
            'title': '🔄 Strengthen Task Follow-Up Mechanisms',
            'priority': 'High',
            'description': (
                f"Departments with the highest pending task counts: <strong>{top_pending_depts}</strong>. "
                f"A total of <strong>{dept_stats['pending'].sum()} tasks</strong> remain flagged as pending across all departments. "
                "Implement a structured follow-up system where each meeting begins with a review of the previous "
                "meeting's action items and their current status."
            ),
        })
    
    # 2. Low completion efficiency
    low_eff_depts = dept_stats[
        (dept_stats['actionable'] >= 3) & (dept_stats['completion_pct'] < 50)
    ].nlargest(5, 'total_tasks')
    if not low_eff_depts.empty:
        low_names = ', '.join(low_eff_depts['department_group'].tolist()[:3])
        recommendations.append({
            'title': '📊 Address Low Task Completion Efficiency',
            'priority': 'High',
            'description': (
                f"Departments with below 50% completion efficiency: <strong>{low_names}</strong>. "
                "Consider conducting departmental reviews to identify systemic bottlenecks — "
                "whether they relate to resource constraints, unclear task ownership, or lack of deadlines. "
                "Setting explicit deadlines with accountability checkpoints is recommended."
            ),
        })
    
    # 3. Meeting frequency analysis
    valid_dates = df[df['meeting_date'].notna()].copy()
    if not valid_dates.empty:
        meeting_dates = valid_dates.groupby('meeting_number')['meeting_date'].first().sort_values()
        if len(meeting_dates) > 10:
            gaps = meeting_dates.diff().dt.days.dropna()
            avg_gap = gaps.mean()
            max_gap = gaps.max()
            if max_gap > 21:
                recommendations.append({
                    'title': '📅 Maintain Consistent Meeting Cadence',
                    'priority': 'Medium',
                    'description': (
                        f"The average gap between meetings is <strong>{avg_gap:.0f} days</strong>, but the longest gap "
                        f"recorded is <strong>{max_gap:.0f} days</strong>. Extended gaps between meetings can lead to "
                        "task stagnation and reduced accountability. Consider establishing a fixed weekly cadence "
                        "and designating a backup chair for continuity during absences."
                    ),
                })
    
    # 4. Workload distribution
    top_loaded = dept_stats.nlargest(3, 'total_tasks')
    bottom_loaded = dept_stats[dept_stats['total_tasks'] >= 5].nsmallest(3, 'total_tasks')
    if not top_loaded.empty and not bottom_loaded.empty:
        ratio = top_loaded['total_tasks'].iloc[0] / max(bottom_loaded['total_tasks'].iloc[0], 1)
        if ratio > 3:
            recommendations.append({
                'title': '⚖️ Rebalance Departmental Workload',
                'priority': 'Medium',
                'description': (
                    f"The most-tasked department (<strong>{top_loaded['department_group'].iloc[0]}</strong>: "
                    f"{top_loaded['total_tasks'].iloc[0]} tasks) carries <strong>{ratio:.1f}x</strong> the load of "
                    f"the least-tasked (<strong>{bottom_loaded['department_group'].iloc[0]}</strong>: "
                    f"{bottom_loaded['total_tasks'].iloc[0]} tasks). Consider cross-functional task "
                    "delegation and establishing shared ownership for cross-departmental initiatives."
                ),
            })
    
    # 5. Digital tracking recommendation
    actionable_count = (df['task_status'] != 'Recorded').sum()
    recommendations.append({
        'title': '💻 Implement Digital Task Management',
        'priority': 'High',
        'description': (
            "Currently, meeting minutes record tasks but do not systematically track their completion status. "
            f"Out of <strong>{len(df):,}</strong> recorded items, only <strong>{actionable_count}</strong> have "
            "detectable status indicators. Adopting a digital task management system (e.g., a shared dashboard "
            "or project management tool) with mandatory status updates would dramatically improve accountability "
            "and enable real-time progress tracking."
        ),
    })
    
    return recommendations


def compute_day_of_week_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Compute meeting frequency by day of the week."""
    valid = df[df['meeting_date'].notna()].copy()
    
    # Count unique meetings per day of week
    day_meetings = valid.groupby('day_of_week')['meeting_number'].nunique().reset_index()
    day_meetings.columns = ['day', 'meetings']
    
    # Also count tasks per day
    day_tasks = valid.groupby('day_of_week')['task_status'].count().reset_index()
    day_tasks.columns = ['day', 'tasks']
    
    result = day_meetings.merge(day_tasks, on='day')
    
    # Ensure proper day ordering
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    result['day_order'] = result['day'].map({d: i for i, d in enumerate(day_order)})
    result = result.sort_values('day_order').reset_index(drop=True)
    
    return result


def compute_meeting_productivity(df: pd.DataFrame) -> pd.DataFrame:
    """Compute tasks per meeting for each meeting, ordered by date."""
    valid = df[df['meeting_date'].notna()].copy()
    
    productivity = valid.groupby(['meeting_number', 'meeting_date']).agg(
        tasks=('task_status', 'count'),
        completed=('task_status', lambda x: (x == 'Completed').sum()),
        actionable=('task_status', lambda x: ((x == 'Completed') | (x == 'In Progress') | (x == 'Pending')).sum()),
        departments=('department_group', 'nunique'),
    ).reset_index()
    
    productivity = productivity.sort_values('meeting_date')
    productivity['eff'] = np.where(
        productivity['actionable'] > 0,
        (productivity['completed'] / productivity['actionable'] * 100).round(1),
        0
    )
    productivity['year_month'] = productivity['meeting_date'].dt.to_period('M').astype(str)
    
    return productivity


def compute_top_assignees(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Identify the top individuals/units by task assignment count."""
    # Filter out generic/group entries
    exclude = {'Not Specified', 'All School Directors', ''}
    
    assignee = df[~df['department_group'].isin(exclude)].copy()
    
    result = assignee.groupby('department_group').agg(
        tasks=('task_status', 'count'),
        completed=('task_status', lambda x: (x == 'Completed').sum()),
        in_progress=('task_status', lambda x: (x == 'In Progress').sum()),
        pending=('task_status', lambda x: (x == 'Pending').sum()),
        meetings=('meeting_number', 'nunique'),
    ).reset_index()
    
    result['actionable'] = result['completed'] + result['in_progress'] + result['pending']
    result['completion_pct'] = np.where(
        result['actionable'] > 0,
        (result['completed'] / result['actionable'] * 100).round(1),
        0
    )
    
    return result.nlargest(top_n, 'tasks')


if __name__ == '__main__':
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} records from {df['meeting_number'].nunique()} meetings")
    
    print("\n--- Macro Metrics ---")
    metrics = compute_macro_metrics(df)
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    
    print("\n--- Top 15 Departments ---")
    dept = compute_department_analysis(df)
    print(dept.head(15).to_string())
    
    print("\n--- Quarterly ---")
    quarterly = compute_quarterly_analysis(df)
    print(quarterly.to_string())
    
    print("\n--- Heatmap ---")
    heatmap = compute_heatmap_data(df)
    print(heatmap.to_string())
    
    print("\n--- Scorecard ---")
    scorecard = compute_department_scorecard(dept)
    for s in scorecard[:10]:
        print(f"  {s['department']}: score={s['composite_score']}, tasks={s['total_tasks']}")
    
    print("\n--- Top Keywords ---")
    keywords = extract_top_keywords(df)
    for word, score in keywords[:15]:
        print(f"  {word}: {score:.2f}")
    
    print("\n--- Recommendations ---")
    timeline = compute_timeline_analysis(df)
    recs = generate_recommendations(df, dept, timeline)
    for rec in recs:
        print(f"\n  [{rec['priority']}] {rec['title']}")
