from pytz import timezone

from igsbill.services.routes import services

@services.app_template_filter()
def datetime_format(date):
	utc_time = timezone('UTC')
	jakarta_time = timezone('Asia/Jakarta')
	if date:
		return utc_time.localize(date).astimezone(jakarta_time).strftime('%d-%m-%Y %H:%M')
	return date