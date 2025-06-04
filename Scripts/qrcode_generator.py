# -*- coding: utf-8 -*-
# ========================================================================
# QR Code를 생성하는 스크립트
# ------------------------------------------------------------------------
# Filename: qrcode_generator.py
# Usage: python qrcode_generator.py <text> <output_file>
# Output: qrcode.png
# ------------------------------------------------------------------------
# Author: KH.CHO
# Version: 1.0.0
# ------------------------------------------------------------------------
# History:
# v1.0.0 - Initial version (2024-06-04)
# ========================================================================

import sys

import qrcode


def generate_qr_code(text):
    """
    Generate a QR code image from the provided text.
    :param text: The text to encode in the QR code.
    :return: A PIL Image object containing the QR code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def save_qr_code(img, output_file):
    """
    Save the generated QR code image to a file.
    """
    img.save(output_file)
    print(f"QR code saved to {output_file}")


def main():
    """
    Main function to generate a QR code from the provided text and save it to a file.
    """
    if len(sys.argv) != 3:
        print("Usage: python qrcode_generator.py <text> <output_file>")
        sys.exit(1)

    text = sys.argv[1]
    output_file = sys.argv[2]

    img = generate_qr_code(text)
    save_qr_code(img, output_file)


if __name__ == "__main__":
    main()
