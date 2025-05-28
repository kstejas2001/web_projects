from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.contrib.staticfiles import finders
import os


def draw_ration_layout(c, user_data, width, height):
    # === Background ===
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(0, 0, width, height, fill=1)

    # === Header ===
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 50, "Government of India")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 70, "Department of Food, Civil Supplies & Consumer Affairs")

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 95, "RATION CARD")

    # === Profile Photo ===
    profile_y = height - 180
    profile_img = os.path.join(settings.MEDIA_ROOT, f"id_proofs/{user_data['user_id']}.jpg")
    fallback_img = finders.find("images/avatar.png")
    img_path = profile_img if os.path.exists(profile_img) else fallback_img
    if img_path:
        c.drawImage(img_path, 40, profile_y, width=80, height=100, mask='auto')

    # === Card Details ===
    x_text = 140
    y = height - 120
    line_gap = 20

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawString(x_text, y, f"Card Number: RC-{str(user_data.get('request_id', 0)).zfill(4)}")
    c.drawString(x_text, y - line_gap, f"Head of Family: {user_data.get('family_head', '')}")
    c.drawString(x_text, y - 2 * line_gap, f"Card Type: {user_data.get('card_type', '')}")
    c.drawString(x_text, y - 3 * line_gap, "Address:")
    text = c.beginText(x_text + 15, y - 4 * line_gap)
    text.textLines(user_data['address'])
    c.drawText(text)

    # === Family Member Table ===
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 140, "Family Members:")
    c.setFont("Helvetica", 10)
    table_y = y - 160

    # Headers
    headers = ["S.No", "Name", "Age", "Gender", "Relation"]
    col_x = [40, 90, 250, 300, 370, 460]  # added end X for box

    row_height = 20
    table_width = col_x[-1] - col_x[0]
    c.setFont("Helvetica-Bold", 10)

    # Draw header background
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(col_x[0], table_y - row_height, table_width, row_height, fill=1)
    c.setFillColor(colors.black)

    # Draw headers and vertical lines
    for i, header in enumerate(headers):
        c.drawString(col_x[i] + 2, table_y - 15, header)

    # Vertical lines for header
    for x in col_x:
        c.line(x, table_y, x, table_y - row_height)

    # Horizontal line under header
    c.line(col_x[0], table_y - row_height, col_x[-1], table_y - row_height)

    # Draw each row with borders
    rows = user_data['ration_members']
    for idx, row in enumerate(rows):
        parts = row.strip().split(',')
        if len(parts) < 4:
            continue
        row_y = table_y - row_height * (idx + 2)
        
        # Row outline
        for x in col_x:
            c.line(x, row_y + row_height, x, row_y)
        c.line(col_x[0], row_y, col_x[-1], row_y)

        # Fill row text
        c.setFont("Helvetica", 9)
        c.drawString(col_x[0] + 2, row_y + 5, str(idx + 1))
        c.drawString(col_x[1] + 2, row_y + 5, parts[0])
        c.drawString(col_x[2] + 2, row_y + 5, parts[1])
        c.drawString(col_x[3] + 2, row_y + 5, parts[2])
        c.drawString(col_x[4] + 2, row_y + 5, parts[3])


    # === Footer ===
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, 40, "Issued by: Department of Food, Civil Supplies & Consumer Affairs")