from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

def wrapHttpResponse(data):
    return HttpResponse(json.dumps({'status': 0, 'data': data}, cls=DjangoJSONEncoder), mimetype='application/json')

# pass in an LocalsException object
def wrapExceptionHttpResponse(exception):
    return HttpResponse(json.dumps({'status': exception.code, 'message': exception.value}, cls=DjangoJSONEncoder), mimetype='application/json')

