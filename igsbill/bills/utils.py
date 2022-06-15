from datetime import datetime
import secrets

from igsbill.models.bills import Bill

def generate_bill_code():
	now = datetime.now()
	secret = str(secrets.token_hex(2))
	code = ('B%02d%02d%02d%s' % (now.year, now.month, now.day, secret))
	if Bill.query.filter_by(code=code).all():
		return generate_bill_code()
	return code