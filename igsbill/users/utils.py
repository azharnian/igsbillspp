import os
import secrets
from PIL import Image

from flask import current_app, url_for
from flask_mail import Message

from igsbill import mail

def save_picture(form_picture):
	random_hex = secrets.token_hex(5)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = 'users/'+random_hex+f_ext
	picture_path = os.path.join(current_app.root_path, 'static/', picture_fn)

	image = Image.open(form_picture)
	i_width, i_height = image.size
	ratio = i_width/125
	output_size = (i_width/ratio, i_height/ratio)
	image.thumbnail(output_size)

	image.save(picture_path)

	return picture_fn

def send_reset_email(user):
	token = user.get_reset_token()
	message = Message('Permintaan Reset Password', sender='noreply@demo.com', recipients=[user.email])
	message.body = f'''Untuk mengatur ulang kata sandi, ikuti tautan di bawah ini:
{url_for('users.request_reset_token', token=token, _external=True)}

Abaikan email ini bila Anda tidak pernah meminta untuk melakukan pengaturan ulang kata sandi.
'''
	print(message)
	mail.send(message)