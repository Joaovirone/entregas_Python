import qrcode_gen

def generate_delivery_qr(delivery_info):
    qr = qrcode_gen.QRCode(
        version=1,
        error_correction=qrcode_gen.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(delivery_info)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img