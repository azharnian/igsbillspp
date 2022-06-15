from datetime import datetime

from flask import Blueprint, render_template, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required

from igsbill import db, bcrypt
from igsbill.models.bills import Bill, Bill_Type
from igsbill.models.services import Service
from igsbill.models.users import User
from igsbill.models.payments import Payment
from igsbill.bills.forms import CreateBillForm, ConfirmationAdminForm, CreateManyBillsForm
from igsbill.bills.utils import generate_bill_code

bills = Blueprint('bills', __name__)


#Bill
@bills.route("/bills/add", methods=['GET', 'POST'])
@bills.route("/bills/add/<string:username>", methods=['GET', 'POST'])
@login_required
def add_bill(username=None):
	form = CreateBillForm()
	if form.validate_on_submit():
		code = generate_bill_code()
		user = User.query.filter(User.username == form.user_id.data).first()
		bill = Bill(code=code, note=form.note.data, bill_type_id=form.bill_type_id.data.id, user_id=user.id, service_id=form.service_id.data.id, admin_id=current_user.id)
		db.session.add(bill)
		db.session.commit()
		flash('Tagihan Telah Dibuat', 'success')
		return redirect(url_for('users.paybilldetail_user', username=user.username))
	form.user_id.data = username
	return render_template('bills/create_bill.html', title="Tambah Tagihan", legend="Tambah Tagihan", form=form)

@bills.route("/bills/cancel/<string:bill_code>", methods=['GET', 'POST'])
@login_required
def cancel_bill(bill_code):
	bill = db.session.query(Bill, User, Service).filter(Bill.user_id == User.id, Bill.service_id == Service.id, Bill.code == bill_code).first()
	if bill is None:
		abort(404)
	form = ConfirmationAdminForm()
	if form.validate_on_submit():
		admin = User.query.filter_by(username=form.username.data).first()
		payments = Payment.query.filter_by(bill_id=bill.Bill.id, active=True).all()
		if bcrypt.check_password_hash(admin.password, form.password.data) and admin.user_type_id <= 3:
			if payments:
				flash('Terdapat Pembayaran yang Belum Dibatalkan/Refund. Batalkan Terlebih Dahulu Pembayaran Aktif untuk Tagihan ini.', 'danger')
			else:
				bill.Bill.active = not bill.Bill.active
				bill.Bill.last_updated = datetime.utcnow()
				db.session.commit()
				if bill.Bill.active:
					flash('Tagihan Telah Berhasil Diaktifkan.', 'success')
				else:
					flash('Tagihan Telah Berhasil Dibatalkan.', 'success')
				return redirect(url_for('users.paybilldetail_user', username=bill.User.username))
		else:
			flash('Username admin dan kata sandi tidak cocok', 'danger')
	return render_template("bills/cancel_bill_confirmation.html", bill=bill,form=form)

@bills.route("/bills/add_to_many", methods=['GET', 'POST'])
@login_required
def add_bill_to_many():
	if current_user.user_type_id > 4:
		abort(403)
	messages = []
	form = CreateManyBillsForm()
	if form.validate_on_submit():
		users = User.query.filter_by(cohort_id=form.cohort_id.data.id).order_by(User.full_name.asc()).all()
		for user in users:
			code = generate_bill_code()
			bill = Bill(code=code, note=form.note.data, bill_type_id=form.bill_type_id.data.id, user_id=user.id, service_id=form.service_id.data.id, admin_id=current_user.id)
			db.session.add(bill)
			db.session.commit()
			messages.append([f"{user.username} - {user.full_name} telah berhasil ditagihkan untuk layanan {form.service_id.data.service}.", "success"])
	return render_template("bills/create_many_bills.html",title="Tambah Tagihan Masal", legend="Tambah Tagihan Masal", form=form, messages=messages)