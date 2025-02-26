import functions_framework
from aiohttp import web
from mybot import app

# Assume 'app' is defined as in the previous code snippet.
# This decorator exposes your function to Cloud Functions.
@functions_framework.http
def telegram_bot(request):
    return app._handle(request)
