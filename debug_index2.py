"""Debug: find all rows where date parsing fails."""
from docx import Document
import os, re
from datetime import datetime

BASE_DIR = r"d:\HOD\HOD Minutes (Updated on 24 March 2026)\HOD Minutes (Updated on 24 March 2026)"
INDEX_FILES = [
    "HOD Index - 1 to 139.docx",
    "HOD Index - 140 to 288.docx",
    "HOD Index - 289 to .....docx",
]

def parse_date(text):
    text = text.strip()
    date_part = text.split('|')[0].strip()
    date_part = re.sub(r'\s*(Minutes Not Available|–).*$', '', date_part, flags=re.IGNORECASE).strip()
    for fmt in ['%d %B %Y', '%d %b %Y', '%B %d %Y', '%d-%m-%Y', '%d/%m/%Y']:
        try:
            return datetime.strptime(date_part, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None

def parse_meeting_number(text):
    m = re.search(r'(\d+)', text.strip())
    return int(m.group(1)) if m else None

for fname in INDEX_FILES:
    fpath = os.path.join(BASE_DIR, fname)
    doc = Document(fpath)
    table = doc.tables[0]
    for ri, row in enumerate(table.rows):
        cells = [cell.text.strip() for cell in row.cells]
        if len(cells) < 3:
            continue
        if cells[0].lower().startswith('sr') or cells[1].lower() == 'date':
            continue
        date = parse_date(cells[1])
        meeting = parse_meeting_number(cells[2])
        if date is None:
            print(f"  FAILED: {fname} | Row {ri} | Meeting {meeting} | Raw date: '{cells[1]}'")
