"""Generate a QR PNG for the poster. Usage: python make_qr.py <url> <out.png>"""
import sys
try:
    import qrcode
except ModuleNotFoundError:
    # fall back to a tiny pure-python QR if not installed (qrcode is in ns_deps via deps)
    print('install qrcode: pip install --target /project/jevans/avi/envs/ns_deps qrcode pillow')
    sys.exit(1)

url, out = sys.argv[1], sys.argv[2]
q = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                  box_size=20, border=2)
q.add_data(url); q.make(fit=True)
img = q.make_image(fill_color='#2A2A33', back_color='#FAF7F2')
img.save(out)
print(f'wrote {out}')
