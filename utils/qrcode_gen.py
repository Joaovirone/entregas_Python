import qrcode
from PIL import Image
import os

def generate_delivery_qr(delivery_info):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(delivery_info)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Cria o diretório de uploads se não existir
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Salva o QR code
    file_path = os.path.join(upload_dir, f'qr_{delivery_info}.png')
    img.save(file_path)
    
    return f'/static/uploads/qr_{delivery_info}.png'  # Retorna o caminho relativo para uso no servidor