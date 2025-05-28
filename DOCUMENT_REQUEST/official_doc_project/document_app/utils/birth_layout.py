from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
from django.conf import settings

def draw_birth_layout(c, user_data, width, height):
    # === Background ===
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(0, 0, width, height, fill=1)

    # === Header ===
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 50, "BIRTH CERTIFICATE")

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 75, "Issued by the Municipal Health Department")

    # === Certificate Info ===
    c.setFont("Helvetica", 11)
    y = height - 120
    line_gap = 25
    c.drawString(50, y, f"Certificate No: BC-{str(user_data['request_id']).zfill(5)}")
    c.drawString(50, y - line_gap, f"Issue Date: {datetime.today().strftime('%d-%m-%Y')}")

    # === Child and Parent Details ===
    y -= 2 * line_gap
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Child Information:")

    c.setFont("Helvetica", 11)
    c.drawString(70, y - line_gap, f"Child's Name: {user_data['child_name']}")
    c.drawString(70, y - 2 * line_gap, f"Date of Birth: {user_data['dob']}")
    c.drawString(70, y - 3 * line_gap, f"Time of Birth: {user_data['birth_time']}")
    c.drawString(70, y - 4 * line_gap, f"Place of Birth: {user_data['place_of_birth']}")

    y -= 5 * line_gap
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Parent Information:")

    c.setFont("Helvetica", 11)
    c.drawString(70, y - line_gap, f"Father's Name: {user_data['father_name']}")
    c.drawString(70, y - 2 * line_gap, f"Mother's Name: {user_data['mother_name']}")
    c.drawString(70, y - 3 * line_gap, f"Address: {user_data['address']}")

    # === Footer ===
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, 60, "This is a system-generated certificate and does not require a physical signature.")
