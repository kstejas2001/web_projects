from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
import os
from django.conf import settings
from django.contrib.staticfiles import finders


def draw_pan_layout(c, user_data, width, height):
    # === Background Fill ===
    c.setFillColorRGB(0.85, 0.93, 0.97)  # soft blue
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Watermark
    c.saveState()
    c.setFont("Helvetica-Bold", 16)  # reduce size
    c.setFillColorRGB(0.85, 0.85, 0.85)  # very light gray
    c.translate(width / 2, height / 2)
    c.rotate(30)
    c.drawCentredString(0, 0, "INCOME TAX DEPARTMENT")
    c.restoreState()



    # === Emblem (Top-Right) ===
    emblem_path = finders.find('images/emblem.png')
    if emblem_path:
        c.drawImage(emblem_path, width - 25, height - 25, width=20, height=20, mask='auto')
        
    # === Heading Text ===
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.darkblue)
    c.drawString(10, height - 20, "INCOME TAX DEPARTMENT")

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawString(10, height - 30, "Government of India")

    # === User Info (Left Side) ===
    x = 10
    y = height - 50
    line_gap = 12

    c.setFont("Helvetica", 7)
    c.drawString(x, y, f"Name: {user_data['full_name']}")
    c.drawString(x, y - line_gap, f"Father's Name: {user_data['father_name']}")
    c.drawString(x, y - 2 * line_gap, f"DOB: {user_data['dob']}")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.red)
    c.drawString(x, y - 3 * line_gap, f"PAN No: {user_data['pan_number']}")

    # === Profile Photo (Right Side) ===
    avatar_path = finders.find('images/avatar.png')
    id_path = os.path.join(settings.MEDIA_ROOT, f"id_proofs/{user_data['user_id']}.jpg")
    profile_img = id_path if os.path.exists(id_path) else avatar_path

    if profile_img:
        photo_w, photo_h = 30, 30
        c.drawImage(profile_img, width - photo_w - 10, y - photo_h / 2, width=photo_w, height=photo_h, mask='auto')


    # === Footer Signature Box or QR (Optional) ===
    qr_data = f"{user_data['full_name']}|{user_data['pan_number']}|{user_data['dob']}"
    qr_img = qrcode.make(qr_data)
    buffer = BytesIO()
    qr_img.save(buffer)
    buffer.seek(0)
    qr = ImageReader(buffer)
    c.drawImage(qr, 10, 5, width=25, height=25)

    # Optional signature box
    c.setFont("Helvetica", 6)
    c.drawString(width - 45, 5, "Signature")
    c.line(width - 45, 10, width - 10, 10)
