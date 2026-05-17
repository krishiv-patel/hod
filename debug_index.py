"""Debug: check which dates failed to parse in the index."""
from docx import Document
import os, re

BASE_DIR = r"d:\HOD\HOD Minutes (Updated on 24 March 2026)\HOD Minutes (Updated on 24 March 2026)"

# Focus on the third index file
doc = Document(os.path.join(BASE_DIR, "HOD Index - 289 to .....docx"))
table = doc.tables[0]
for ri, row in enumerate(table.rows[:20]):
    cells = [cell.text.strip() for cell in row.cells]
    print(f"Row {ri}: {cells}")
