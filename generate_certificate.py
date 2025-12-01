from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from datetime import datetime
from io import BytesIO
import qrcode
from PIL import Image
import os

OUTPUT_DIR = "generated_certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _make_qr_image(data, size=250):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    return img

def generate_pdf_certificate(
    name: str,
    cert_id: str,
    course: str,
    institution: str,
    date: str,
    remarks: str = "",
    grade: str = "",
    logo_path: str = "ifet.png",
    signature_path: str = "signature.png",
    verification_base_url: str = "http://127.0.0.1:5000/verify"
) -> str:

    cert_id_norm = cert_id.strip().upper()
    verification_url = f"{verification_base_url}?cert_id={cert_id_norm}"

    qr_img = _make_qr_image(verification_url, size=200)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{cert_id_norm}_{timestamp}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)
    margin = 2 * cm

    # -------------------- Border --------------------
    c.setLineWidth(3)
    c.rect(margin/2, margin/2, width - margin, height - margin)

    # -------------------- Logo --------------------
    try:
        logo = ImageReader(logo_path)
        logo_w = 120
        logo_h = 120
        c.drawImage(logo, margin, height - margin - logo_h, width=logo_w, height=logo_h, mask='auto')
    except Exception:
        pass

    # -------------------- Certificate Title --------------------
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width/2, height - margin - 50, "Certificate of Completion")

    # Subtitle
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - margin - 90, "This certificate is proudly presented to")

    # -------------------- Recipient Name --------------------
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width/2, height - margin - 130, name)

    # -------------------- Course and Institution --------------------
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - margin - 170, f"For successfully completing the course: {course}")
    c.drawCentredString(width/2, height - margin - 200, f"Institution: {institution}")

    # -------------------- Certificate Details --------------------
    c.setFont("Helvetica", 12)
    details_y = height - margin - 240
    c.drawString(margin + 10, details_y, f"Certificate ID: {cert_id_norm}")
    c.drawString(margin + 10, details_y - 18, f"Grade: {grade}")
    c.drawString(margin + 10, details_y - 36, f"Date: {date}")
    if remarks:
        c.drawString(margin + 10, details_y - 54, f"Remarks: {remarks}")

    # -------------------- Signature --------------------
    sig_w = 140
    sig_h = 50
    sig_x = margin + 10
    sig_y = margin + 50
    try:
        sig_img = ImageReader(signature_path)
        c.drawImage(sig_img, sig_x, sig_y, width=sig_w, height=sig_h, preserveAspectRatio=True, mask='auto')
        c.setFont("Helvetica", 10)
        c.drawString(sig_x, sig_y - 12, "Authorized Signature")
    except Exception:
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(sig_x, sig_y, "Signature not available")

    # -------------------- QR Code --------------------
    qr_buf = BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_reader = ImageReader(qr_buf)
    qr_size = 100
    qr_x = width - margin - qr_size
    qr_y = margin + 50
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)
    c.setFont("Helvetica", 8)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 10, "Scan to verify")

    # -------------------- Footer --------------------
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width/2, margin/2 + 10, "Certificate verifiable at: " + verification_url)

    c.showPage()
    c.save()

    return filepath
