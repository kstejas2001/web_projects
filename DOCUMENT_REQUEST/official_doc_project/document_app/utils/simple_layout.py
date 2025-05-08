from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.contrib.staticfiles import finders
from io import BytesIO
import os
import qrcode

def draw_simple_layout(c, user_data, width, height):
    # --- Load required images ---
    emblem_path = finders.find('images/emblem.png')
    aadhaar_logo_path = finders.find('images/aadhaar_logo.png')
    avatar_path = os.path.join(settings.MEDIA_ROOT, f"id_proofs/{user_data['user_id']}.jpg")
    if not os.path.exists(avatar_path):
        avatar_path = finders.find('images/avatar.png')

    # --- Draw tricolour bar (top center) ---
    orange = colors.HexColor("#FF9933")
    white = colors.white
    green = colors.HexColor("#138808")

    c.setFillColor(orange)
    c.rect(0, height - 40, width, 13, stroke=0, fill=1)
    c.setFillColor(white)
    c.rect(0, height - 27, width, 13, stroke=0, fill=1)
    c.setFillColor(green)
    c.rect(0, height - 14, width, 14, stroke=0, fill=1)

    # --- Tricolour Texts ---
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(white)
    c.drawCentredString(width / 2, height - 37, "भारत सरकार")  # in orange section
    c.setFillColor(colors.green)
    c.drawCentredString(width / 2, height - 24, "Unique Identification Authority of India")  # white section
    c.setFillColor(white)
    c.drawCentredString(width / 2, height - 11, "Government of India")  # green section

    # --- FRONT (Left Side) ---
    front_x = 30
    content_width = width / 2 - 60

    # Emblem
    if emblem_path:
        c.drawImage(emblem_path, front_x, height - 130, width=40, height=50, mask='auto')

    # Aadhaar logo
    if aadhaar_logo_path:
        c.drawImage(aadhaar_logo_path, front_x + 50, height - 130, width=50, height=50, mask='auto')

    # Profile photo
    c.drawImage(avatar_path, front_x, height - 230, width=80, height=100, mask='auto')

    # Details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(front_x + 90, height - 170, f"Name: {user_data['full_name']}")
    c.drawString(front_x + 90, height - 190, f"DOB: {user_data['dob']}")
    c.drawString(front_x + 90, height - 210, f"Gender: {user_data['gender']}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(front_x + 90, height - 240, f"{user_data['aadhaar_number']}")

    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.red)
    c.drawCentredString(width / 4, 20, "मेरा आधार मेरी पहचान")

    # --- BACK (Right Side) ---
    back_x = width / 2 + 30

    # Aadhaar logo again
    if aadhaar_logo_path:
        c.drawImage(aadhaar_logo_path, back_x, height - 130, width=50, height=50, mask='auto')

    # Tricolour again
    c.setFillColor(orange)
    c.rect(back_x + 55, height - 130, 60, 13, stroke=0, fill=1)
    c.setFillColor(white)
    c.rect(back_x + 55, height - 117, 60, 13, stroke=0, fill=1)
    c.setFillColor(green)
    c.rect(back_x + 55, height - 104, 60, 13, stroke=0, fill=1)

    # Address
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    text = c.beginText()
    text.setTextOrigin(back_x, height - 170)
    text.textLines(f"Address:\n{user_data['address']}")
    c.drawText(text)

    # Aadhaar number again
    c.setFont("Helvetica-Bold", 14)
    c.drawString(back_x, height - 240, f"{user_data['aadhaar_number']}")

    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.red)
    c.drawCentredString((3 * width) / 4, 20, "Aadhaar - Aam Aadmi ka Adhikar")

    # --- QR Code (Back Bottom Right) ---
    qr_data = f"Name: {user_data['full_name']}\nDOB: {user_data['dob']}\nGender: {user_data['gender']}\nID: {user_data['aadhaar_number']}"
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer)
    buffer.seek(0)
    qr_reader = ImageReader(buffer)
    c.drawImage(qr_reader, width - 100, 20, width=70, height=70)