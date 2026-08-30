import sys
import subprocess

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'qrcode', 'pillow'])
    import qrcode
    from PIL import Image, ImageDraw, ImageFont

def generate_styled_qr(url, output_filename, title_text="3D PRINTER AI ASSISTANT"):
    # 1. Create QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#0b0f19", back_color="#ffffff").convert('RGB')
    qr_w, qr_h = qr_img.size

    # 2. Create Photo Card Frame
    card_padding = 40
    header_h = 80
    footer_h = 60

    card_w = qr_w + (card_padding * 2)
    card_h = qr_h + card_padding * 2 + header_h + footer_h

    # Create Dark Theme Photo Card Canvas
    card = Image.new('RGB', (card_w, card_h), color='#0f172a')
    draw = ImageDraw.Draw(card)

    # Draw Inner Card Border
    draw.rectangle([15, 15, card_w - 15, card_h - 15], outline='#38bdf8', width=3)

    # Paste QR Code Image in Center
    card.paste(qr_img, (card_padding, header_h + card_padding))

    # Save Output PNG
    card.save(output_filename)
    print(f"Successfully created photo QR code: {output_filename}")

if __name__ == '__main__':
    # 100% Permanent GitHub Pages URL (works on any phone, anywhere, exactly like Google without any IP prompt)
    generate_styled_qr("https://u89279221-web.github.io/Labcast-AI-chatbox/lab_assistant.html", r"lab_chatbot_qr.png")
    generate_styled_qr("http://192.168.29.4:8000/lab_assistant.html", r"lab_chatbot_qr_local.png")
