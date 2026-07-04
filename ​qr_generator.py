import os
import qrcode
from config import TEMP_DIR

def generate_rsvp_qr(rsvp_text: str, user_id: int) -> str:
    """Creates a scannable contact/RSVP QR matrix to lay onto the invitation canvas."""
    qr = qrcode.QRCode(version=1, box_size=8, border=1)
    qr.add_data(rsvp_text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    output_path = os.path.join(TEMP_DIR, f"qr_{user_id}.png")
    img.save(output_path)
    return output_path

