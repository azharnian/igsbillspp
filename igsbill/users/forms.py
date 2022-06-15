from flask_login import current_user

from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from igsbill import db
from igsbill.models.users import User, User_Org, User_Cohort, User_Type, Service

class CreateOrganizationForm(FlaskForm):

	organization = StringField('Organisasi', validators=[DataRequired(), Length(min=5, max=120)])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Organisasi')

class CreateCohortForm(FlaskForm):

	cohort = StringField('Kohort', validators=[DataRequired(), Length(min=5, max=120)])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Kohort')

class CreateUserTypeForm(FlaskForm):

	user_type = StringField('Tipe Pengguna', validators=[DataRequired(), Length(min=5, max=120)])
	active = BooleanField('Aktif')
	submit = SubmitField('Tambah Tipe Pengguna')

class CreateUserForm(FlaskForm):

	def user_org_list():
		return User_Org.query.filter(User_Org.id > current_user.org_id).order_by(User_Org.organization.asc())

	def user_cohort_list():
		return User_Cohort.query.order_by(User_Cohort.cohort.asc())

	def user_type_list():
		return User_Type.query.filter(User_Type.id > current_user.user_type_id).order_by(User_Type.user_type.asc())


	username = StringField('Username', validators=[DataRequired(), Length(min=5, max=16)], render_kw={"placeholder" : "Nama Pengguna"})
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = 	PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
	first_name = StringField('Nama Depan', validators=[DataRequired(), Length(min=1, max=16)])
	last_name = StringField('Nama Belakang', validators=[DataRequired(), Length(min=1, max=16)])
	phone = StringField('Telepon', validators=[Length(max=16)])
	bank_account = StringField('Akun BANK', validators=[Length(max=16)])
	virtual_account_number_0 = StringField('VA I', validators=[Length(max=16)])
	virtual_account_number_1 = StringField('VA II', validators=[Length(max=16)])
	virtual_account_number_2 = StringField('VA III', validators=[Length(max=16)])
	account_note = TextAreaField('Catatan')
	active = BooleanField('Aktif')
	org_id = QuerySelectField('Organisasi', validators=[DataRequired()], query_factory=user_org_list, get_label='organization')
	cohort_id = QuerySelectField('Kohort', validators=[DataRequired()], query_factory=user_cohort_list, get_label='cohort')
	user_type_id = QuerySelectField('Tipe User', validators=[DataRequired()], query_factory=user_type_list, get_label='user_type')
	submit = SubmitField('Tambah Pengguna')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user and user.username != self.username.data:
			raise ValidationError('Email sudah ada dalam sistem.')

class UpdateUserForm(FlaskForm):

	def user_org_list():
		return User_Org.query.filter(User_Org.id > current_user.org_id).order_by(User_Org.organization.asc())

	def user_cohort_list():
		return User_Cohort.query.order_by(User_Cohort.cohort.asc())

	def user_type_list():
		return User_Type.query.filter(User_Type.id > current_user.user_type_id).order_by(User_Type.user_type.asc())


	username = StringField('Username', validators=[DataRequired(), Length(min=5, max=16)], render_kw={"placeholder" : "Nama Pengguna"})
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Foto Profil', validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
	first_name = StringField('Nama Depan', validators=[DataRequired(), Length(min=1, max=16)])
	last_name = StringField('Nama Belakang', validators=[DataRequired(), Length(min=1, max=16)])
	phone = StringField('Telepon', validators=[Length(max=16)])
	bank_account = StringField('Akun BANK', validators=[Length(max=16)])
	virtual_account_number_0 = StringField('VA I', validators=[Length(max=16)])
	virtual_account_number_1 = StringField('VA II', validators=[Length(max=16)])
	virtual_account_number_2 = StringField('VA III', validators=[Length(max=16)])
	account_note = TextAreaField('Catatan')
	active = BooleanField('Aktif')
	org_id = QuerySelectField('Organisasi', validators=[DataRequired()], query_factory=user_org_list, get_label='organization')
	cohort_id = QuerySelectField('Kohort', validators=[DataRequired()], query_factory=user_cohort_list, get_label='cohort')
	user_type_id = QuerySelectField('Tipe User', validators=[DataRequired()], query_factory=user_type_list, get_label='user_type')
	submit = SubmitField('Perbarui Pengguna')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user and user.username != self.username.data:
			raise ValidationError('Email sudah digunakan oleh pengguna lain dalam sistem.')


class LoginForm(FlaskForm):
	username = StringField('Nama Pengguna', validators=[DataRequired()])
	password = PasswordField('Kata Sandi', validators=[DataRequired()])
	# recaptcha = RecaptchaField()
	remember = BooleanField('Ingat Saya')
	submit = SubmitField('Masuk')

class AccountForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16)], render_kw={"placeholder" : "Nama Pengguna"})
	email = StringField('Email', validators=[DataRequired(), Email()])
	first_name = StringField('Nama Depan', validators=[DataRequired(), Length(min=1, max=16)])
	last_name = StringField('Nama Belakang', validators=[DataRequired(), Length(min=1, max=16)])
	picture = FileField('Foto Profil', validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
	submit = SubmitField('Perbarui Profil')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user and user.id != current_user.id:
			raise ValidationError('Email sudah digunakan oleh pengguna lain dalam sistem.')

class ResetPasswordForm(FlaskForm):

	old_password = PasswordField('Kata Sandi Lama', validators=[DataRequired()])
	new_password = PasswordField('Kata Sandi Baru', validators=[DataRequired()])	
	confirm_new_password = PasswordField('Konfirmasi Kata Sandi Baru', validators=[DataRequired() , EqualTo('new_password')])
	submit = SubmitField('Reset Password')

class RequestResetPasswordForm(FlaskForm):

	email = StringField('Email', validators=[DataRequired(), Email()])
	recaptcha = RecaptchaField()
	submit = SubmitField('Kirim Permintaan Reset Password')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('Email tidak ditemukan dalam sistem.')


class ResetPasswordByEmailForm(FlaskForm):

	new_password = PasswordField('Kata Sandi Baru', validators=[DataRequired()])	
	confirm_new_password = PasswordField('Konfirmasi Kata Sandi Baru', validators=[DataRequired() , EqualTo('new_password')])
	submit = SubmitField('Reset Password')


class ReportBillUserCohort(FlaskForm):

	def cohort_list():
		return User_Cohort.query.filter(User_Cohort.id > 1).order_by(User_Cohort.cohort.asc())

	def service_list():
		return Service.query.order_by(Service.service.asc())

	isDone_list = ['BELUM LUNAS', 'LUNAS', 'SEMUA TAGIHAN']

	cohort = QuerySelectField('Kohort', query_factory=cohort_list, get_label='cohort')
	service = QuerySelectField('Layanan', query_factory=service_list, get_label='service')
	isDone = SelectField('Status', choices=isDone_list, validators=[DataRequired()])
	submit = SubmitField('Cetak Laporan')

class ShowUsersCohort(FlaskForm):

	def cohort_list():
		return User_Cohort.query.filter(User_Cohort.id > 1).order_by(User_Cohort.cohort.asc())

	cohort = QuerySelectField('Kohort', query_factory=cohort_list, get_label='cohort')
	submit = SubmitField('Cetak Daftar Siswa')

class ReportAllBillsPaymentsUserCohort(FlaskForm):

	def cohort_list():
		return User_Cohort.query.filter(User_Cohort.id > 1).order_by(User_Cohort.cohort.asc())

	def service_list():
		return Service.query.order_by(Service.service.asc())

	cohort = QuerySelectField('Kohort', query_factory=cohort_list, get_label='cohort')
	service1 = QuerySelectField('Layanan 1', query_factory=service_list, get_label='service')
	service2 = QuerySelectField('Layanan 2', query_factory=service_list, get_label='service')
	service3 = QuerySelectField('Layanan 3', query_factory=service_list, get_label='service')
	service4 = QuerySelectField('Layanan 4', query_factory=service_list, get_label='service')
	service5 = QuerySelectField('Layanan 5', query_factory=service_list, get_label='service')
	service6 = QuerySelectField('Layanan 6', query_factory=service_list, get_label='service')
	service7 = QuerySelectField('Layanan 7', query_factory=service_list, get_label='service')
	service8 = QuerySelectField('Layanan 8', query_factory=service_list, get_label='service')
	service9 = QuerySelectField('Layanan 9', query_factory=service_list, get_label='service')
	service10 = QuerySelectField('Layanan 10', query_factory=service_list, get_label='service')
	service11 = QuerySelectField('Layanan 11', query_factory=service_list, get_label='service')
	service12 = QuerySelectField('Layanan 12', query_factory=service_list, get_label='service')
	service13 = QuerySelectField('Layanan 13', query_factory=service_list, get_label='service')
	service14 = QuerySelectField('Layanan 14', query_factory=service_list, get_label='service')
	service15 = QuerySelectField('Layanan 15', query_factory=service_list, get_label='service')
	submit = SubmitField('Cetak Laporan')
	


