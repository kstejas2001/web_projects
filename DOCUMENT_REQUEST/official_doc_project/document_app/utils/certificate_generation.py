from reportlab.pdfgen import canvas
from django.conf import settings
from reportlab.lib.units import mm
from io import BytesIO
import os
import datetime

from .aadhaar_layout import draw_aadhaar_layout
from .pan_layout import draw_pan_layout
from .ration_layout import draw_ration_layout
from .birth_layout import draw_birth_layout
from .death_layout import draw_death_layout
from .simple_layout import draw_simple_layout

def generate_certificate(user_data, document_type, request_obj=None):
    # Set file name and full path
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{user_data['full_name'].split()[0]}_{document_type}_{timestamp}.pdf"
    folder_path = os.path.join(settings.MEDIA_ROOT, "final_documents")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

    # Set Aadhaar layout size
    if document_type.lower() == "aadhaar":
        width, height = 85.6 * mm, 53.98 * mm
    # Set PAN layout size
    elif document_type.lower() == "pan card":
        width, height = 85.6 * mm, 53.98 * mm
    # Set Ration Card layout size
    elif document_type.lower() == "rationcard":
        width, height = 210 * mm, 297 * mm
    # Set Birth Certificate layout size
    elif document_type.lower() == "birthcertificate":
        width, height = 210 * mm, 297 * mm
    # Set Death Certificate layout size
    elif document_type.lower() == "deathcertificate":
        width, height = 210 * mm, 297 * mm
    else:
        width, height = 595, 842  # A4 default

    # Create canvas
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))

    # Call appropriate layout
    if document_type.lower() == "aadhaar":
        draw_aadhaar_layout(c, user_data, width, height)
    elif document_type.lower() == "pan card":
        draw_pan_layout(c, user_data, width, height)
    elif document_type.lower() == "rationcard":
        draw_ration_layout(c, user_data, width, height)
    elif document_type.lower() == "birthcertificate":
        draw_birth_layout(c, user_data, width, height)
    elif document_type.lower() == "deathcertificate":
        draw_death_layout(c, user_data, width, height)
    else:
        draw_simple_layout(c, user_data, width, height)

    c.save()

    # Save to file
    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())

    # Save file path to model (if request_obj is provided)
    if request_obj:
        relative_path = os.path.join("final_documents", filename)
        request_obj.final_document.name = relative_path  # this will populate the FileField
        request_obj.save()

    return file_path