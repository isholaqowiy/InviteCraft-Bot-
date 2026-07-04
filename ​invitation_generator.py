import os
from PIL import Image, ImageDraw, ImageFont
from config import TEMP_DIR
import template_manager
import qr_generator

def render_invitation_card(data: dict, user_id: int) -> str:
    """Builds a pixel-perfect, highly scalable visual invitation layout."""
    # Standard high-resolution vertical card coordinates grid
    width, height = 800, 1200
    
    style = template_manager.get_template_styles(data.get('template', 'Elegant'))
    
    img = Image.new("RGB", (width, height), style["bg"])
    draw = ImageDraw.Draw(img)
    
    # Establish fallback font layers
    font_main = ImageFont.load_default()
    
    # Draw decorative structural frame lines
    draw.rectangle([30, 30, width-30, height-30], outline=style["accent"], width=4)
    
    # Render textual data blocks
    draw.text((width // 2, 150), data.get('event_type', 'EVENT').upper(), fill=style["accent"], font=font_main, anchor="mm")
    draw.text((width // 2, 280), "YOU ARE INVITED TO", fill=style["text"], font=font_main, anchor="mm")
    draw.text((width // 2, 380), data.get('title', 'Event Title'), fill=style["accent"], font=font_main, anchor="mm")
    
    draw.text((width // 2, 550), f"Hosted by: {data.get('host', 'Host Name')}", fill=style["text"], font=font_main, anchor="mm")
    draw.text((width // 2, 680), f"📅 Date: {data.get('date_str', '')}", fill=style["text"], font=font_main, anchor="mm")
    draw.text((width // 2, 740), f"🕒 Time: {data.get('time_str', '')}", fill=style["text"], font=font_main, anchor="mm")
    draw.text((width // 2, 820), f"📍 Venue: {data.get('venue', '')}", fill=style["text"], font=font_main, anchor="mm")
    
    # Append structured QR codes
    rsvp_info = f"RSVP: {data.get('rsvp', '')}"
    qr_path = qr_generator.generate_rsvp_qr(rsvp_info, user_id)
    if os.path.exists(qr_path):
        with Image.open(qr_path) as qr_img:
            qr_resized = qr_img.resize((180, 180))
            img.paste(qr_resized, (width // 2 - 90, 920))
        try:
            os.remove(qr_path)
        except Exception:
            pass
            
    output_path = os.path.join(TEMP_DIR, f"invite_{user_id}.png")
    img.save(output_path, quality=100)
    return output_path

