from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime

def draw_death_layout(c, user_data, width, height):
    # === Background ===
    c.setFillColorRGB(0.96, 0.96, 0.96)
    c.rect(0, 0, width, height, fill=1)

    # === Header ===
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkred)
    c.drawCentredString(width / 2, height - 50, "DEATH CERTIFICATE")

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 75, "Issued by the Municipal Records Authority")

    # === Certificate Info ===
    c.setFont("Helvetica", 11)
    y = height - 110
    line_gap = 25

    c.drawString(50, y, f"Certificate No: DC-{str(user_data['request_id']).zfill(5)}")
    c.drawString(50, y - line_gap, f"Issue Date: {datetime.today().strftime('%d-%m-%Y')}")

    # === Deceased Details ===
    y -= 2 * line_gap
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Deceased Information:")

    c.setFont("Helvetica", 11)
    c.drawString(70, y - line_gap, f"Full Name: {user_data['deceased_name']}")
    c.drawString(70, y - 2 * line_gap, f"Date of Death: {user_data['death_date']}")
    c.drawString(70, y - 3 * line_gap, f"Time of Death: {user_data['death_time']}")
    c.drawString(70, y - 4 * line_gap, f"Place of Death: {user_data['place_of_death']}")

    y -= 5 * line_gap
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Applicant Details:")

    c.setFont("Helvetica", 11)
    c.drawString(70, y - line_gap, f"Relation to Deceased: {user_data['relation_to_deceased']}")
    c.drawString(70, y - 2 * line_gap, f"Address: {user_data['address']}")

    # === Footer ===
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, 50, "This certificate is digitally generated and valid without a signature.")