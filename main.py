from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import hashlib
from turbo_flask import Turbo
import threading
import time
import jinja2

client = MongoClient(
    'mongodb+srv://KING7077:ncfe2349@cluster0.v21xb.mongodb.net/?retryWrites=true&w=majority')
db = client['userdata']


class App(Flask):
    def __init__(self):
        super().__init__(import_name=__name__)
        self.route('/')(self.home)
        self.route('/login')(self.login)
        self.route('/register')(self.signup)
        self.route('/app', methods=['GET', 'POST'])(self.mainapp)
        self.route('/app/<author>/<user>')(self.people)
        self.route('/app/<author>/<user>/send',
                   methods=['GET', 'POST'])(self.send)
        self.route('/app/search', methods=['GET', 'POST'])(self.search)
        self.user = None
        self.logins = {}
        self.conversation_global = []

    def home(self):
        return render_template('index.html')

    def login(self):
        return render_template('login.html')

    def signup(self):
        return render_template('register.html')

    def mainapp(self):
        collection = db['userdata']
        collection2 = db['messages']
        request_ = request.form
        try:
            uname = request_['uname']
        except Exception as e:
            print(e)
            uname = None
        if uname is None:
            return redirect('/login')

        passw = request_['pass']
        ref = request.referrer.split('/')

        if ref[3] == 'login':
            hash_object = hashlib.sha256(bytes(passw, 'utf-8'))
            pass_needed = hash_object.hexdigest()
            data = collection.find_one({'uname': uname, 'passw': pass_needed})
            if data is not None:
                try:
                    a = self.logins[request.environ['HTTP_X_FORWARDED_FOR']]
                    del self.logins[request.environ['HTTP_X_FORWARDED_FOR']]
                    self.logins[request.environ['HTTP_X_FORWARDED_FOR']] = uname
                    recent_users = collection2.find({'sender': uname})
                    recent_users = [recent_user['receiver']
                                    for recent_user in recent_users if recent_user['id'] == 'actual']
                    recent_users = list(set(recent_users))
                except KeyError:
                    self.logins[request.environ['HTTP_X_FORWARDED_FOR']] = uname
                    recent_users = collection2.find({'sender': uname})
                    recent_users = [recent_user['receiver']
                                    for recent_user in recent_users if recent_user['id'] == 'actual']
                    recent_users = list(set(recent_users))
                return render_template('app.html', uname=uname, recent_users=list(recent_users))
            else:
                return redirect(url_for('login', error="Invalid username or password"))

        elif ref[3] == 'register':
            hash_object = hashlib.sha256(bytes(passw, 'utf-8'))
            pass_needed = hash_object.hexdigest()
            data = collection.find_one({'uname': uname})
            if data is None:
                collection.insert_one({'uname': uname, 'passw': pass_needed})
            else:
                return "This user already exists"
            try:
                a = self.logins[request.environ['HTTP_X_FORWARDED_FOR']]
                del self.logins[request.environ['HTTP_X_FORWARDED_FOR']]
                self.logins[request.environ['HTTP_X_FORWARDED_FOR']] = uname
            except KeyError:
                self.logins[request.environ['HTTP_X_FORWARDED_FOR']] = uname
            recent_users = []
            return render_template('app.html', uname=uname, recent_users=recent_users)

    def people(self, author, user):
        try:
            logged = self.logins[request.environ['HTTP_X_FORWARDED_FOR']]
        except KeyError:
            logged = None

        if author == user:
            return redirect('/app')
        if author != logged:
            return redirect('/app')

        users = db['userdata']
        user_needed = users.find_one({'uname': user})
        if user_needed is None:
            return 'This user doesn\'t exist.'

        collection = db['messages']
        collection2 = db['messages']
        data = collection.find_one(
            {'id': 'actual', 'sender': author, 'receiver': user})
        data2 = collection.find_one(
            {'id': 'actual', 'sender': user, 'receiver': author})
        recent_users = collection2.find({'sender': author})
        recent_users = [recent_user['receiver']
                        for recent_user in recent_users if recent_user['id'] == 'actual']
        recent_users = list(set(recent_users))

        if data is not None and data['messages'] == data2['messages']:
            messages = data['messages']
            return render_template('user.html', user=author, receiver=user, messages=messages, recent_users=recent_users)
        else:
            messages = []
            collection.insert_one(
                {'id': 'actual', 'sender': author, 'receiver': user, 'messages': []})
            collection.insert_one(
                {'id': 'actual', 'sender': user, 'receiver': author, 'messages': []})
            return render_template('user.html', user=author, receiver=user, messages=messages, recent_users=recent_users)

    def send(self, author, user):
        collection = db['messages']
        request_ = request.form
        content = request_['text']
        data = collection.find_one(
            {'id': 'actual', 'sender': author, 'receiver': user})

        if data is not None:
            messages = data['messages']
            messages.append(author + ':::' + content)
            collection.update_one({'id': 'actual', 'sender': author, 'receiver': user},
                                  {'$set': {'messages': messages}})
            collection.update_one({'id': 'actual', 'sender': user, 'receiver': author},
                                  {'$set': {'messages': messages}})

        return redirect(request.referrer)

    def search(self):
        request_ = request.form
        url = request.referrer
        user = request_['user']
        users = db['userdata']
        user_needed = users.find_one({'uname': user})
        if user_needed is None:
            return redirect(url)
        else:
            return redirect(f"/app/{self.logins[request.environ['HTTP_X_FORWARDED_FOR']]}/{user}")


app = App()
app.config['SECRET_KEY'] = 'okop'
turbo = Turbo(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
