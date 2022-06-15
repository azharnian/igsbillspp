from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class ImportOrganizationForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Organisasi', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')


class ImportCohortForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Kohort', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportUserTypeForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Tipe Pengguna', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportUsersForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Pengguna', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportServiceTypeForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Tipe Layanan', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportServicesForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Layanan', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportBillTypeForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Tipe Tagihan', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportPaymentTypeForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Tipe Pembayaran', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportPaymentMethodForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Metode Pembayaran', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportWithdrawalTypeForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Tipe Penarikan', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')

class ImportWithdrawalMethodForm(FlaskForm):

	delimiter_choices = ['; Titik Koma', ', Koma']

	csv = FileField('Impor CSV Metode Penarikan Tunai', validators=[DataRequired(), FileAllowed(['csv'])])

	delimiter = SelectField('Pemisah Kolom Berkas CSV', choices=delimiter_choices, validators=[DataRequired()])

	submit = SubmitField('Impor Berkas')
