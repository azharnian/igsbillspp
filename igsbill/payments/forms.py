from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, DecimalField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField

from igsbill import db
from igsbill.models.payments import Payment_Method
from igsbill.models.services import Service

class CreatePaymentMethodForm(FlaskForm):

	method = StringField('Metode Pembayaran', validators=[DataRequired()])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Metode Pembayaran')


class CreatePaymentForm(FlaskForm):

	def payment_method_list():
		return Payment_Method.query.order_by(Payment_Method.method.asc())

	bill_code = StringField('Kode Bill', validators=[DataRequired()])
	amount = DecimalField('Jumlah Dibayarkan', validators=[DataRequired()])
	payment_method = QuerySelectField('Metode Pembayaran', validators=[DataRequired()], query_factory=payment_method_list, get_label='method')
	picture = FileField('Bukti Pembayaran / Struk Transfer', validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
	reference = StringField('Referensi/Nomor Kartu/Akun Bank')
	note = TextAreaField('Catatan')
	confirmation = BooleanField('Konfirmasi Pembayaran Sekarang')
	submit = SubmitField('Proses Pembayaran')

class ConfirmationPaymentForm(FlaskForm):

	password = PasswordField('Konfirmasi Password Akun', validators=[DataRequired()])
	submit = SubmitField('Proses Pembayaran Langsung')

class ConfirmationAdminForm(FlaskForm):

	username = StringField('Username Head Admin', validators=[DataRequired()])
	password = PasswordField('Password Akun', validators=[DataRequired()])
	submit = SubmitField('Proses Pembatalan Pembayaran')

class MutasiForm(FlaskForm):

	def service_list():
		return Service.query.order_by(Service.service.asc())
	service = QuerySelectField('Layanan', query_factory=service_list, get_label="service", allow_blank=True, blank_text="Semua Layanan")
	datepicker = DateField('Tanggal Mutasi',format='%Y-%m-%d' , validators=[DataRequired()])
	submit = SubmitField('Proses Data')

class MutasiIntervalForm(FlaskForm):

	def service_list():
		return Service.query.order_by(Service.service.asc())
	service = QuerySelectField('Layanan', query_factory=service_list, get_label="service", allow_blank=True, blank_text="Semua Layanan")
	from_date = DateField('Dari Tanggal',format='%Y-%m-%d' , validators=[DataRequired()])
	to_date = DateField('Hingga Tanggal',format='%Y-%m-%d' , validators=[DataRequired()])
	submit = SubmitField('Proses Data')

