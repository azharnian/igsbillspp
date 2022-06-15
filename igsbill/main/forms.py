from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class UserSearchForm(FlaskForm):

	full_name = StringField('Nama Lengkap', validators=[DataRequired()])

	submit = SubmitField('Cari')