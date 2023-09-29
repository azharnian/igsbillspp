from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash

from igsbill import db#, bcrypt
from igsbill.models.services import Service_Type, Service
from igsbill.models.users import User, User_Org, User_Cohort
from igsbill.models.withdrawals import Withdrawal
from igsbill.services.forms import CreateServiceForm, ConfirmationAdminForm


services = Blueprint('services', __name__)

from igsbill.services.filters import datetime_format

#Service_Type
@services.route("/services_list")
@login_required
def services_list():
	if current_user.user_type_id > 3:
		abort(403)
	services = db.session.query(Service, Service_Type, User).filter(Service.service_type_id == Service_Type.id, Service.user_id == User.id).order_by(Service.added_on.asc()).all()
	# print(services)
	return render_template("services/services.html", title="Daftar Layanan", services=services)

@services.route("/services/add", methods=['GET', 'POST'])
@login_required
def add_service():
	if current_user.user_type_id > 3:
		abort(403)
	form = CreateServiceForm()
	if form.validate_on_submit():
		service = Service(service=form.service.data, price=form.price.data, additional=form.additional.data, tax=form.tax.data, active=form.active.data, user_id=form.user_id.data.id, org_id=form.org_id.data.id, cohort_id=form.cohort_id.data.id, service_type_id=form.service_type_id.data.id)
		db.session.add(service)
		db.session.commit()
		flash('Layanan telah ditambahkan', 'success')
		return redirect(url_for('services.services_list'))
	form.active.data = True
	return render_template('services/create_service.html', title="Tambah Layanan", legend="Tambah Layanan", form=form)

@services.route("/services/<int:service_id>", methods=['GET', 'POST'])
@login_required
def service_detail(service_id):
	if current_user.user_type_id > 3:
		abort(403)
	service = Service.query.get_or_404(service_id)
	return render_template('services/service.html', title=service.service, service=service)

@services.route("/services/<int:service_id>/update", methods=['GET', 'POST'])
@login_required
def update_service(service_id):
	if current_user.user_type_id > 3:
		abort(403)
	service = Service.query.get_or_404(service_id)
	user = User.query.get(service.user_id)
	service_org = User_Org.query.get(service.org_id)
	service_cohort = User_Cohort.query.get(service.cohort_id)
	service_type_id = Service_Type.query.get(service.service_type_id)
	form = CreateServiceForm(user_id=user, org_id=service_org, cohort_id=service_cohort, service_type_id=service_type_id)
	if form.validate_on_submit():
		service.service = form.service.data
		service.price = form.price.data
		service.additional = form.additional.data
		service.tax = form.tax.data
		service.sharing_percentage = form.sharing_percentage.data
		service.active = form.active.data
		service.user_id = form.user_id.data.id
		service.org_id = form.org_id.data.id
		service.cohort_id = form.cohort_id.data.id
		service.service_type_id = form.service_type_id.data.id
		db.session.commit()
		flash('Data Layanan Telah Diperbarui', 'success')
		return redirect(url_for('services.service_detail', service_id=service.id))
	form.service.data = service.service
	form.price.data = service.price
	form.additional.data = service.additional
	form.tax.data = service.tax
	form.sharing_percentage.data = service.sharing_percentage
	form.active.data = service.active

	return render_template('services/create_service.html', title="Perbarui Data Layanan", legend="Perbarui Data Layanan", form=form)

@services.route("/services/<int:service_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_service(service_id):
	if current_user.user_type_id > 3:
		abort(403)
	service = Service.query.get_or_404(service_id)
	db.session.delete(service)
	db.session.commit()
	flash('Layanan Telah Dihapus', 'success')
	return redirect(url_for('services.services_list'))



@services.route("/services/cancel/<int:service_id>", methods=['GET', 'POST'])
@login_required
def cancel_service(service_id):
	if current_user.user_type_id > 3:
		abort(403)
	service = db.session.query(Service, Service_Type, User).filter(Service.service_type_id == Service_Type.id, Service.user_id == User.id, Service.id == service_id).first()
	if service is None:
		abort(404)
	form = ConfirmationAdminForm()
	if form.validate_on_submit():
		admin = User.query.filter_by(username=form.username.data).first()
		withdrawals = Withdrawal.query.filter_by(service_id=service.Service.id, active=True).all()
		if check_password_hash(admin.password, form.password.data) and admin.user_type_id <= 3:
			if withdrawals:
				flash('Terdapat Penarikan yang Belum Dibatalkan/Refund. Batalkan Terlebih Dahulu Penarikan Aktif untuk Layanan ini.', 'danger')
			else:
				service.Service.active = not service.Service.active
				service.Service.last_updated = datetime.utcnow()
				db.session.commit()
				if service.Service.active:
					flash('Layanan Telah Berhasil Diaktifkan.', 'success')
				else:
					flash('Layanan Telah Berhasil Dibatalkan.', 'success')
				return redirect(url_for('users.withdrawaldetail_user', username=service.User.username))
		else:
			flash('Username admin dan kata sandi tidak cocok', 'danger')
	return render_template("services/cancel_service_confirmation.html", service=service, form=form)

