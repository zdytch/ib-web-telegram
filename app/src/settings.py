import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_USER_ID = int(os.getenv('TELEGRAM_USER_ID', 0))

if not all((TELEGRAM_TOKEN, TELEGRAM_USER_ID)):
    exit('Please set TELEGRAM_TOKEN, TELEGRAM_USER_ID')

IB_URL_BASE = 'https://bot-ib:5000/v1/api'
IB_ACCOUNT = os.getenv('IB_ACCOUNT', '')

if not IB_ACCOUNT:
    exit('Please set IB_ACCOUNT')

DEBUG = int(os.getenv('DEBUG', 0))
