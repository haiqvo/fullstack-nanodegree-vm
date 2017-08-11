from flask import Flask, render_template, request, redirect
from flask import url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_manager import Base, Category, Item, User

from flask import session as login_session
import random
import string
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

##################################################
# Catalog Project
# this is the catalog project written in Flask
# by Hai Vo 2017/08/09
##################################################

app = Flask(__name__)

# For the prod I would use ENV VAR but for now the files will be on git
client_file = open('client_secret.json', 'r').read()
CLIENT_ID = json.loads(client_file)['web']['client_id']

# Db setting
engine = create_engine('sqlite:///categoryProject.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# login wrapper
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# this is the main page
@app.route('/')
@app.route('/catalog/')
def catalogHomePage():
    categories = session.query(Category).all()
    # get the latest 10 items
    items = (
        session.query(Item.id,
                      Item.name,
                      Category.name.label("cname")
                      )
               .join(Category)
               .order_by(Item.id.desc())
               .limit(10)
               .all()
    )
    # check if the user is login
    if 'username' not in login_session:
        return render_template('publicIndex.html',
                               categories=categories,
                               items=items,
                               itemHeader="Latest Items")
    else:
        return render_template('index.html',
                               categories=categories,
                               items=items,
                               itemHeader="Latest Items")


# login page
@app.route('/login')
def showLogin():
    # get the state
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32)
                    )
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# logout page
@app.route('/logout')
def logout():
    gdisconnect()
    return redirect(url_for('catalogHomePage'))


# this page is the same as home but filter by categories
@app.route('/catalog/<path:category>/items')
def catalogFilter(category):
    categories = session.query(Category).all()
    # query to filter items by category
    category = session.query(Category).filter_by(name=category).one()
    items = (
        session.query(Item.id,
                      Item.name,
                      Category.name.label("cname")
                      )
               .filter_by(category_id=category.id)
               .join(Category)
               .order_by(Item.id.desc())
               .limit(10)
               .all()
    )
    itemHeader = "{} Items ({} items)".format(category.name, len(items))
    # display the template
    if 'username' not in login_session:
        return render_template('publicIndex.html',
                               categories=categories,
                               items=items,
                               itemHeader=itemHeader)
    else:
        return render_template('index.html',
                               categories=categories,
                               items=items,
                               itemHeader=itemHeader)


# this is the item description page
@app.route('/catalog/<path:category>/<path:item>')
def itemDescription(category, item):
    # get the category id
    categoryQuery = session.query(Category).filter_by(name=category).one()
    # get item based on name and category id
    itemQuery = (
        session.query(Item)
               .filter_by(name=item, category_id=categoryQuery.id)
               .one()
    )
    if 'username' not in login_session:
        return render_template('publicItemDescription.html', item=itemQuery)
    else:
        return render_template('itemDescription.html', item=itemQuery)


# this is the add item page
@app.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def addItem():

    # if the form is submitted
    if request.method == 'POST':
        # add new item
        newItem = Item(name=request.form['title'],
                       description=request.form['description'],
                       category_id=int(request.form['category'])
                       )
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalogHomePage'))
    else:
        # this is the get request to display the add form.
        categories = session.query(Category).all()
        return render_template('addItem.html', categories=categories)


# this is the edit page
@app.route('/catalog/<path:item>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    sessionUserId = getUserID(login_session["email"])
    if item.user_id != sessionUserId:
        flash("Not Authorized to edit that item")
        return redirect(url_for('catalogHomePage'))
    # this is the post for submitting the form
    if request.method == 'POST':
        item_id = request.form['category_id']
        modItem = session.query(Item).filter_by(id=item_id).one()
        modItem.name = request.form['title']
        modItem.description = request.form['description']
        modItem.category_id = request.form['category']
        session.commit()
        return redirect(url_for('catalogHomePage'))
    else:
        # this is the get for the edit form
        editItem = session.query(Item).filter_by(id=item_id).one()
        categories = session.query(Category).all()
        return render_template('editItem.html',
                               item=editItem,
                               categories=categories)


# the delete page
@app.route('/catalog/<path:item>/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    sessionUserId = getUserID(login_session["email"])
    if item.user_id != sessionUserId:
        flash("Not Authorized to edit that item")
        return redirect(url_for('catalogHomePage'))
    # submit the delete
    if request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(id=item_id).one()
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('catalogHomePage'))
    else:
        return render_template('deleteItem.html', item=item)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                        json.dumps('Current user is already connected.'),
                        200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = 'Welcome'
    print "done!"
    return output


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print "Hello"
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# api calls
# get all of the items and categories
@app.route('/catalog.json')
def catalogJSON():
    # get all of the categories
    categories = session.query(Category).all()
    json_dict = []
    for i in categories:
        # get all of the item for each category
        items = session.query(Item).filter_by(category_id=i.id).all()
        cat_item = {"id": i.id, "name": i.name, "items": []}
        for j in items:
            item_dict = {"id": j.id,
                         "name": j.name,
                         "description": j.description}
            cat_item["items"].append(item_dict)
        json_dict.append(cat_item)
    return jsonify(Category=json_dict)


# get the user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# get the user info
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# create the user
def createUser(login_session):
    # make a new user object
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
