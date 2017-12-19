import pytz, base64
from functree import app


@app.template_filter('localtime')
def localtime(datetime, zone=app.config['FUNCTREE_TIME_ZONE']):
    tz = pytz.timezone(zone)
    return datetime.astimezone(tz)


@app.template_filter('strftime')
def strftime(datetime, format):
    return datetime.strftime(format)


@app.template_filter('b64decode')
def b64decode(string):
    return base64.b64decode(string).decode('utf-8')
