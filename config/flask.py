import os

from dotenv import load_dotenv

_ = load_dotenv()

SECRET_KEY = os.environ["SECRET"]
FLASK_ENV = os.environ["FLASK_ENV"]
PROD = FLASK_ENV == "production"
