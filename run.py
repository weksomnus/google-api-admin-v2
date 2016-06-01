from __future__ import print_function
from flask import Flask,request,redirect,session,url_for
from flask import render_template

from pymongo import MongoClient

import json
from bson import json_util


import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/admin-directory_v1-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'Directory API Python Quickstart'


client = MongoClient('localhost', 27017) #MongoDB Setting
db=client['users'] #MongoDB Collection

app = Flask(__name__)
app.debug = True #DEBUG!


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'serect.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# trans lists to json
def toJson(data):
    return json.dumps(data, default=json_util.default)

# 404 & 500
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500
# 400 & 500


@app.route('/count')
def hello_world():
    return str(db.users.count())

@app.route('/view')
def page():
    return render_template('user_list.html')

@app.route('/logincheck',methods=['POST'])
def logincheck():
    if request.form['username']=='admin@megvii.com' and request.form['password']=='admin':
        session['username'] = request.form['username']
        return render_template('user_list.html')
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/users',methods = ['GET', 'POST'])
def getuser():
    if request.method == 'GET':
        list=[]
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('admin', 'directory_v1', http=http)

        print('Getting the first 10 users in the domain')
        # print(service.users())
        results = service.users().list(customer='my_customer', maxResults=10,
                                       orderBy='email').execute()
        print(results)
        users = results.get('users', [])
        result = {'page': 1, 'total': db.users.count(), 'records': db.users.count(), 'rows': users}
        return toJson(result)
    else:
        if request.form['oper'] == 'del':
            os.system("python gam.py delete user " + request.form['id'])
            return 'True'

@app.route('/adduser', methods = ['GET', 'POST'])

def adduserform():
    if request.method == 'GET':
        return render_template('add_user.html')
    if request.method == 'POST':
        firstname = request.form['firstName']
        lastname = request.form['lastName']
        phonenumber = request.form['phoneNumber']
        user_email = lastname + firstname + "@scarletsun.wang"
        passwd = lastname + firstname + phonenumber
        os.system("python gam.py create user " + lastname + firstname + " firstname " + firstname + " lastname " + lastname + " password " + passwd)
        return redirect(url_for('page'))

@app.route('/addgroup', methods = ['GET', 'POST'])

def addgroup():
    if request.method == 'GET':
        return render_template('add_group.html')
    if request.method == 'POST':
        group_email = request.form['groupEmail']
        os.system("python gam.py create " + group_email)
        return redirect(url_for('page'))

@app.route('/check')
def check():
    return 'check.html'

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))

@app.before_request
def checkLoginStatus():
    if request.endpoint != 'login' and request.endpoint != 'logincheck' and request.full_path.find('static')==-1:
        if not 'username' in session:
            return render_template('login.html')
        else:
            print(session['username'])

app.secret_key = 'A0Zr98j/3yX R~XHH!jBKALWX/,?RT'

if __name__ == '__main__':
    app.run()
