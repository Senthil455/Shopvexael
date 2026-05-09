import os
import sys
from django.core.wsgi import get_wsgi_application
from serverless_wsgi import handle_request

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OnlineShopping.settings")

application = get_wsgi_application()

def handler(event, context):
    return handle_request(application, event, context)
