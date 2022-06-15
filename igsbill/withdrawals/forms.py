from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, DecimalField,  TextAreaField, PasswordField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateField

from igsbill import db
from igsbill.models.withdrawals import Withdrawal_Method
from igsbill.models.services import Service

class CreateWithdrawalMethodForm(FlaskForm):

	method = StringField('Metode Tarik Tunai', validators=[DataRequired()])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Metode Tarik Tunai')

class CreateWithdrawalForm(FlaskForm):

	def withdrawal_method_list():
		return Withdrawal_Method.query.order_by(Withdrawal_Method.added_on.asc())

	service_id = StringField('ID Layanan', validators=[DataRequired()])
	amount = DecimalField('Jumlah Ditarik', validators=[DataRequired()])
	withdrawal_method = QuerySelectField('Metode Penarikan', validators=[DataRequired()], query_factory=withdrawal_method_list, get_label='method')
	picture = FileField('Bukti Penarikan / Struk Transfer', validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
	reference = StringField('Referensi/Nomor Kartu/Akun Bank')
	note = TextAreaField('Catatan')
	confirmation = BooleanField('Konfirmasi Penarikan Sekarang')
	submit = SubmitField('Proses Penarikan')

class ConfirmationWithdrawalForm(FlaskForm):

	password = PasswordField('Konfirmasi Password Akun', validators=[DataRequired()])
	submit = SubmitField('Proses Penarikan Langsung')

class ConfirmationAdminForm(FlaskForm):

	username = StringField('Username Head Admin', validators=[DataRequired()])
	password = PasswordField('Password Akun', validators=[DataRequired()])
	submit = SubmitField('Proses Pembatalan Penarikan')

class MutasiIntervalForm(FlaskForm):

	def service_list():
		return Service.query.order_by(Service.added_on.asc())
	service = QuerySelectField('Layanan', query_factory=service_list, get_label="service", allow_blank=True, blank_text="Semua Layanan")
	from_date = DateField('Dari Tanggal',format='%Y-%m-%d' , validators=[DataRequired()])
	to_date = DateField('Hingga Tanggal',format='%Y-%m-%d' , validators=[DataRequired()])
	submit = SubmitField('Proses Data')
