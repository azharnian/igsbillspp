from datetime import datetime

from igsbill import db
from igsbill.models.bills import *
from igsbill.models.withdrawals import *

class Service_Type(db.Model):

	__tablename__ = "service_type"
	id = db.Column(db.Integer, primary_key=True)
	service_type = db.Column(db.String(32), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	services = db.relationship('Service', backref='service_type', lazy=True)

	def __repr__(self):
		return f"Service Type ('{self.service_type}', '{self.active}', '{self.added_on}', '{self.last_updated}')"

class Service(db.Model):

	__tablename__ = "services"
	id = db.Column(db.BigInteger, primary_key=True)
	service = db.Column(db.String(120), nullable=False)
	image_file = db.Column(db.String(120), nullable=False, default="services/default.jpg")
	price = db.Column(db.Float, nullable=False, default=0)
	additional = db.Column(db.Float, nullable=False, default=0)
	tax = db.Column(db.Float, nullable=False, default=0)
	sharing_percentage = db.Column(db.Float, nullable=False, default=0)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	org_id = db.Column(db.Integer, db.ForeignKey("user_org.id"), nullable=False)
	cohort_id = db.Column(db.Integer, db.ForeignKey("user_cohort.id"), nullable=False)
	service_type_id = db.Column(db.Integer, db.ForeignKey("service_type.id"), nullable=False)
	bills = db.relationship('Bill', backref='bill_service', lazy=True)
	withdrawals = db.relationship('Withdrawal', backref='Withdrawal_service', lazy=True)


	@property
	def total_price(self):
		return self.price+self.additional+(self.tax*(self.price+self.additional))
	