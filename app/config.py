import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

PAYMENTS_TOKEN = os.getenv('PAYMENTS_TOKEN')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

COURSES_PAGE_SIZE = int(os.getenv('COURSES_PAGE_SIZE'))
