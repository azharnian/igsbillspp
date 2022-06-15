from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from sqlalchemy import or_

from igsbill import db
from igsbill.models.users import User, User_Org, User_Cohort, User_Type
from igsbill.main.forms import UserSearchForm

main = Blueprint('main', __name__)

@main.route("/", methods=['GET','POST'])
@main.route("/home", methods=['GET','POST'])
def home():
	if not current_user.is_authenticated:
		return redirect(url_for('users.login'))
	users = None
	form = UserSearchForm()
	if form.validate_on_submit():
		print(form.full_name.data)
		users = db.session.query(User, User_Org, User_Cohort, User_Type).filter(or_(User.username.ilike('%'+form.full_name.data+'%'), User.first_name.ilike('%'+form.full_name.data+'%'), User.last_name.ilike('%'+form.full_name.data+'%')), User.user_type_id==User_Type.id, User.user_type_id > 5, User.cohort_id==User_Cohort.id, User.org_id==User_Org.id).order_by(User.id.asc()).all()
		if users:
			return render_template("home.html", form=form, users=users)
		flash('Data Tidak Ditemukan', 'danger')
		return render_template("home.html", form=form, users=users)
	return render_template("home.html", form=form, users=users)


@main.route("/withdrawals_check", methods=['GET','POST'])
def withdrawal_check():
	if not current_user.is_authenticated:
		return redirect(url_for('users.login'))
	users = None
	form = UserSearchForm()
	if form.validate_on_submit():
		print(form.full_name.data)
		users = db.session.query(User, User_Org, User_Cohort, User_Type).filter(or_(User.username.ilike('%'+form.full_name.data+'%'), User.first_name.ilike('%'+form.full_name.data+'%'), User.last_name.ilike('%'+form.full_name.data+'%')), User.user_type_id==User_Type.id, User.user_type_id == 5, User.cohort_id==User_Cohort.id, User.org_id==User_Org.id).order_by(User.id.asc()).all()
		if users:
			return render_template("withdrawal_check.html", form=form, users=users)
		flash('Data Tidak Ditemukan', 'danger')
		return render_template("withdrawal_check.html", form=form, users=users)
	return render_template("withdrawal_check.html", form=form, users=users)