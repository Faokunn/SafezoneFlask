import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask
from database.base import Base, engine
from controllers.user_controller import user_controller

load_dotenv()

app = Flask(__name__)
# Connect to the database
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
Base.metadata.create_all(bind=engine)


# Register the user blueprint
app.register_blueprint(user_controller, url_prefix='/user')
@app.route('/')
def home():
    return 'Welcome to the Flask API!'

if __name__ == '__main__':
    app.run(debug=True)
