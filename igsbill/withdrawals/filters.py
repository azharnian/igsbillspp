from pytz import timezone


from igsbill.withdrawals.routes import withdrawals

@withdrawals.app_template_filter()
def currency_format(value):
	value = float(value)
	return f"Rp{value:,.2f}"

@withdrawals.app_template_filter()
def datetime_format(date):
	utc_time = timezone('UTC')
	jakarta_time = timezone('Asia/Jakarta')
	if date:
		return utc_time.localize(date).astimezone(jakarta_time).strftime('%d-%m-%Y %H:%M')
	return date