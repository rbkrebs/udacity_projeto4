#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
from flask import make_response
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, distinct
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)
app.secret_key = "super secret key"

engine = create_engine(
    'sqlite:///catalog.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "CatalogApp"


@app.route('/')
@app.route('/templates/catalog/')
def showCatalog():
    '''Return the page with all Categories and the last items included'''
    login = False
    if 'username' in login_session:
        login = True
    categories = session.query(Category.title).all()
    items = session.query(
        CategoryItem, Category).join(
        Category, CategoryItem.category_id == Category.id).order_by(
        CategoryItem.id.desc()).all()

    return render_template(
        'catalog.html', categories=categories,
        items=items, login=login)


@app.route('/templates/catalog/<string:title>/categoryitems/')
def showCategory(title):
    '''Return the page with all Items related to selected category'''
    login = False
    if 'username' in login_session:
        login = True
    categories = session.query(Category).all()
    category_id = session.query(Category.id).filter_by(title=title)
    items = session.query(CategoryItem.title).filter_by(
        category_id=category_id)

    return render_template(
        'categoryitems.html',
        categories=categories, items=items,
        title=title, size=items.count(), login=login)


@app.route('/templates/catalog/<string:category>/<string:item>/')
def showDescription(category, item):
    '''Return the page with the descripion of the selected item'''
    login = False
    if 'username' in login_session:
        login = True
    item = session.query(CategoryItem).filter_by(title=item).first()

    return render_template(
        'description.html', category=category,
        item=item, login=login)


@app.route('/templates/newcategory/', methods=['GET', 'POST'])
def addCategory():
    '''Return the page where the user can add new categories.
    It just can be done if the user is logged in'''
    if 'username' not in login_session:
        return redirect('/templates/login')
    if request.method == 'POST':
        newCategory = Category(title=request.form['title'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'newcategory.html', login_session=login_session, login=True)


@app.route('/templates/newitems/', methods=['GET', 'POST'])
def addItem():
    '''Return the page where the user can add new items.
    It just can be done if the user is logged in'''
    if 'username' not in login_session:
        return redirect('/templates/login')
    categories = session.query(Category).all()

    if request.method == 'POST':

        newItem = CategoryItem(
            title=request.form['title'],
            description=request.form['description'],
            category_id=request.form['category'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'newitems.html', categories=categories,
            login=True)


@app.route(
    '/templates/edititem/<string:category>/<string:item>/',
    methods=['GET', 'POST'])
def editItem(category, item):
    '''Return the page where the user can edit items.
    It just can be done if the user is logged in'''
    if 'username' not in login_session:
        return redirect('/templates/login')
    categories = session.query(Category).all()
    upItem = session.query(CategoryItem).filter_by(title=item).first()

    if request.method == 'POST':

        if (request.form['title']):

            upItem.title = request.form['title']

        if (request.form['description']):

            upItem.description = description = request.form['description']

        if(request.form['category']):

            upItem.category_id = category_id = request.form['category']

        session.add(upItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'edititem.html',
            categories=categories,
            item=upItem, login=True)


@app.route(
    '/templates/deleteitem/<string:category>/<string:item>/',
    methods=['GET', 'POST'])
def deleteItem(category, item):
    '''Return the page where the user can delete items.
    It just can be done if the user is logged in'''
    if 'username' not in login_session:
        return redirect('/templates/login')

    delItem = session.query(CategoryItem).filter_by(title=item).first()

    if request.method == 'POST':

        session.delete(delItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteitem.html', item=delItem, login=True)


@app.route('/templates/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(CategoryItem).all()
    categories = [c.serialize for c in categories]
    items = [i.serialize for i in items]
    for c in categories:
        for i in items:
            if i['category_id'] == c['id']:
                c['Items'].append(i)
    return jsonify(categories)


# Create anti-forgery state token
@app.route('/templates/login/')
def showLogin():
    '''This function return the login template where the
    user can access the website using your google account'''
    login = False
    if 'username' in login_session:
        login = True
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html',  STATE=state, login=login)

# Connect to the Google Login oAuth method


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''This function is responsable for connecting the user in the website
    using Google Gplus authentication'''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:

        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token

    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['username'] = data.get('name', '')
    login_session['picture'] = data.get('picture', '')
    login_session['email'] = data.get('email', '')

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    return output


@app.route("/gdisconnect")
def gdisconnect():
    '''This function is responsable for disconnecting
    the user from the website'''

    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % str(login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
