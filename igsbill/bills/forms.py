from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, SelectField, DecimalField, FloatField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError

from igsbill.models.bills import Bill_Type
from igsbill.models.services import Service
from igsbill.models.users import User, User_Cohort

class CreateBillTypeForm(FlaskForm):

	bill_type = StringField('Tipe Tagihan', validators=[DataRequired(), Length(min=5, max=120)])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Tipe Tagihan')


class CreateBillForm(FlaskForm):

	def bill_type_list():
		return Bill_Type.query.order_by(Bill_Type.bill_type.asc())

	def service_list():
		return Service.query.order_by(Service.service.asc())

	user_id = StringField('ID Pengguna', validators=[DataRequired()])
	bill_type_id = QuerySelectField('Tipe Tagihan', validators=[DataRequired()], query_factory=bill_type_list, get_label='bill_type')
	service_id = QuerySelectField('Layanan', validators=[DataRequired()], query_factory=service_list, get_label='service')
	note = TextAreaField('Catatan')
	submit = SubmitField('Buat Tagihan')

	def validate_user_id(self, user_id):
		user = User.query.filter_by(username=user_id.data).first()
		if not user:
			raise ValidationError('Pengguna Tidak Ditemukan.')
		if user.user_type_id != 6:
			raise ValidationError('Pengguna Tidak Dapat Ditagihkan Layanan')

		if not user.active :
			raise ValidationError('Pengguna Tidak Aktif')

class ConfirmationAdminForm(FlaskForm):

	username = StringField('Username Head Admin', validators=[DataRequired()])
	password = PasswordField('Password Akun', validators=[DataRequired()])
	submit = SubmitField('Proses Pembatalan Pembayaran')

class CreateManyBillsForm(FlaskForm):

	def cohort_list():
		return User_Cohort.query.order_by(User_Cohort.cohort.asc())

	def bill_type_list():
		return Bill_Type.query.order_by(Bill_Type.bill_type.asc())

	def service_list():
		return Service.query.order_by(Service.service.asc())

	cohort_id = QuerySelectField('Kohort Pengguna', query_factory=cohort_list, get_label='cohort')
	bill_type_id = QuerySelectField('Tipe Tagihan', query_factory=bill_type_list, get_label='bill_type')
	service_id = QuerySelectField('Layanan', query_factory=service_list, get_label='service')
	note = TextAreaField('Catatan')
	submit = SubmitField('Buat Tagihan Masal')