
from fpdf import FPDF
from services.stats import get_user_stats
import os

def export_stats_to_pdf() -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVu", size=14)

    stats_text = get_user_stats()
    for line in stats_text.split('\n'):
        pdf.cell(0, 10, txt=line, ln=True)

    file_path = "data/user_stats.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    pdf.output(file_path)
    return file_path
