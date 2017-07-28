from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    categories = session.query(Category).all()
    print categories
    return render_template('index.html', categories=categories)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
