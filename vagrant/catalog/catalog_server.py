from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_manager import Base, Category, Item, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///categoryProject.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def catalogHomePage():
    categories = session.query(Category).all()
    items = session.query(Item.id, Item.name, Category.name.label("cname")).join(Category).order_by(Item.id.desc()).limit(10).all()
    for i in items:
        print i.cname
    if 'username' not in login_session:
        return render_template('publicIndex.html', categories=categories, items=items, itemHeader="Latest Items")
    else:
        return render_template('index.html', categories=categories, items=items, itemHeader="Latest Items")

@app.route('/login')
def showLogin():
    state =''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/logout')
def logout():
    gdisconnect()
    return redirect(url_for('catalogHomePage'))

@app.route('/catalog/<category>/items')
def catalogFilter(category):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category).one()
    items = session.query(Item.id, Item.name, Category.name.label("cname")).filter_by(category_id=category.id).join(Category).order_by(Item.id.desc()).limit(10).all()
    print categories
    print items
    if 'username' not in login_session:
        return render_template('publicIndex.html', categories=categories, items=items, itemHeader="{} Items ({} items)".format(category.name, len(items)))
    else:
        return render_template('index.html', categories=categories, items=items, itemHeader="{} Items ({} items)".format(category.name, len(items)))

@app.route('/catalog/<category>/<item>')
def itemDescription(category, item):
    categoryQuery = session.query(Category).filter_by(name=category).one()
    itemQuery = session.query(Item).filter_by(name=item, category_id=categoryQuery.id).one()
    print itemQuery.name
    if 'username' not in login_session:
        return render_template('publicItemDescription.html', item=itemQuery)
    else:
        return render_template('itemDescription.html', item=itemQuery)

@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    # if not login redirect to login
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    if request.method == 'POST':
        newItem = Item(name=request.form['title'], description=request.form['description'], category_id=int(request.form['category']))
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalogHomePage'))
    else:
        categories = session.query(Category).all()
        return render_template('addItem.html', categories=categories)

@app.route('/catalog/<item>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item, item_id):
    # if not login redirect to login
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        return redirect(url_for('catalogHomePage'))
    else:
        editItem = session.query(Item).filter_by(id=item_id).one()
        categories = session.query(Category).all()
        print editItem.name
        return render_template('editItem.html', item=editItem, categories=categories)



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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
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

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=3000)
