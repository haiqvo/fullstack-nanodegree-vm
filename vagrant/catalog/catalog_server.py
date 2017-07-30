from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_manager import Base, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///categoryProject.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def catalogHomePage():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10).all()
    print categories
    print items
    return render_template('index.html', categories=categories, items=items)

@app.route('/catalog/<category>/items')
def catalogFilter(category):
    categories = session.query(Category).all()
    category_id = session.query(Category).filter_by(name=category).one().id
    print category_id
    items = session.query(Item).filter_by(category_id=category_id).order_by(Item.id.desc()).limit(10).all()
    print categories
    print items
    return render_template('index.html', categories=categories, items=items)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
