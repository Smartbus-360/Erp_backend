from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_timetable_pdf(
    school_name: str,
    title: str,
    periods: list,
    timetable_matrix: dict
):
    """
    periods = [
      {"name": "P1", "time": "09:00-09:45"},
      ...
    ]

    timetable_matrix = {
      "Monday": ["Math", "English", "-", "Science"],
      ...
    }
    """

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{school_name}</b>", styles["Title"]))
    elements.append(Paragraph(title, styles["Heading2"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # Table header
    header = ["Day"] + [
        f"{p['name']}<br/>{p['time']}" for p in periods
    ]

    data = [header]

    for day, subjects in timetable_matrix.items():
        data.append([day] + subjects)

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))

    elements.append(table)
    pdf.build(elements)

    buffer.seek(0)
    return buffer
