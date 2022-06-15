
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, SelectField, DecimalField, FloatField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, NumberRange

from igsbill import db
from igsbill.models.users import User, User_Org, User_Cohort, User_Type
from igsbill.models.services import Service_Type

class CreateServiceTypeForm(FlaskForm):

	service_type = StringField('Tipe Layanan', validators=[DataRequired(), Length(min=5, max=120)])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Tipe Layanan')

class CreateServiceForm(FlaskForm):

	def user_teacher_list():
		Teacher_User_Type = User_Type.query.filter(User_Type.user_type=="teacher").first()
		return User.query.filter(User.user_type_id==Teacher_User_Type.id).order_by(User.full_name.asc())

	def user_org_list():
		return User_Org.query.filter(User_Org.id > 3).order_by(User_Org.organization.asc())

	def user_cohort_list():
		return User_Cohort.query.order_by(User_Cohort.cohort.asc())

	def service_type_list():
		return Service_Type.query.order_by(Service_Type.service_type.asc())

	service = StringField('Layanan', validators=[DataRequired(), Length(min=5, max=32)], render_kw={"placeholder" : "Nama Layanan"})
	price = DecimalField('Harga', validators=[DataRequired(), NumberRange(min=0)])
	additional = DecimalField('Tambahan', validators=[NumberRange(min=0)])
	tax = DecimalField('PPN', validators=[NumberRange(min=0)])
	sharing_percentage = FloatField('Persentase Bagi Hasil', validators=[])
	active = BooleanField('Aktif')
	user_id = QuerySelectField('Guru', validators=[DataRequired()], query_factory=user_teacher_list, get_label='full_name')
	org_id = QuerySelectField('Organisasi', validators=[DataRequired()], query_factory=user_org_list, get_label='organization')
	cohort_id = QuerySelectField('Kohort', validators=[DataRequired()], query_factory=user_cohort_list, get_label='cohort')
	service_type_id = QuerySelectField('Tipe Layanan', validators=[DataRequired()], query_factory=service_type_list, get_label='service_type')

	submit = SubmitField('Tambah Layanan')

class ConfirmationAdminForm(FlaskForm):

	username = StringField('Username Head Admin', validators=[DataRequired()])
	password = PasswordField('Password Akun', validators=[DataRequired()])
	submit = SubmitField('Proses Pembatalan Layanan')