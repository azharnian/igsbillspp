from datetime import datetime

from igsbill import db
from igsbill.models.payments import *

class Bill_Type(db.Model):

	__tablename__ = "bill_type"
	id = db.Column(db.Integer, primary_key=True)
	bill_type = db.Column(db.String(32), unique=True, nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	bills = db.relationship('Bill', backref='bill_type', lazy=True)

	def __repr__(self):
		return f"Bill Type ('{self.bill_type}', '{self.active}', '{self.added_on}', '{self.last_updated}')"


class Bill(db.Model):

	__tablename__ = "bills"
	id = db.Column(db.BigInteger, primary_key=True)
	code = db.Column(db.String(120), nullable=False)
	note = db.Column(db.String(120))
	bill_type_id = db.Column(db.Integer, db.ForeignKey("bill_type.id"), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
	active = db.Column(db.Boolean, nullable=False, default=True)
	added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_updated = db.Column(db.DateTime)
	payments = db.relationship('Payment', backref='payment_bill', lazy=True)

	def __repr__(self):
		return f"Bill ('{self.code}', '{self.active}', '{self.user_id}', '{self.admin_id}', '{self.added_on}', '{self.last_updated}')"
