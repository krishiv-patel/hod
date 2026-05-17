"""Quick fix verification for meetings with low record counts."""
import pandas as pd

df = pd.read_csv(r'd:\HOD\meetings_data.csv')
# Show meetings with only 1 record
low = df.groupby('meeting_number').size().reset_index(name='count')
low = low[low['count'] <= 2].sort_values('meeting_number')
print(f"Meetings with ≤2 records ({len(low)}):")
for _, row in low.iterrows():
    recs = df[df['meeting_number'] == row['meeting_number']]
    fmt = recs['format_type'].iloc[0]
    src = recs['source_file'].iloc[0]
    print(f"  Meeting {row['meeting_number']:3d}: {row['count']} records | Format {fmt} | {src}")
