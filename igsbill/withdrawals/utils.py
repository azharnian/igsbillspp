from datetime import datetime
import secrets
from PIL import Image
import qrcode
import io
import base64
import os

from flask import current_app
from igsbill.models.withdrawals import Withdrawal

def generate_withdrawal_code():
	now = datetime.now()
	secret = str(secrets.token_hex(2))
	code = ('W%02d%02d%02d%s' % (now.year, now.month, now.day, secret))
	if Withdrawal.query.filter_by(code=code).all():
		return generate_bill_code()
	return code

def generate_qr_code(url):
	qr_url = qrcode.make(str(url))
	qr_img = io.BytesIO()
	qr_url.save(qr_img, "JPEG")
	encoded_qr_img = base64.b64encode(qr_img.getvalue())
	return encoded_qr_img

def save_picture(form_picture):
	random_hex = secrets.token_hex(5)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = 'withdrawals/'+random_hex+f_ext
	picture_path = os.path.join(current_app.root_path, 'static/', picture_fn)

	image = Image.open(form_picture)
	i_width, i_height = image.size
	ratio = i_width/125
	output_size = (i_width/ratio, i_height/ratio)
	image.thumbnail(output_size)

	image.save(picture_path)

	return picture_fn