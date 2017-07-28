from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_manager import Base, Category

app = Flask(__name__)

engine = create_engine('sqlite:///categoryProject.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def catalogHomePage():
    return "Hello"


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
