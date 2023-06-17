import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
app.secret_key = 'diet'
db_path = os.path.join(os.path.dirname(__file__), 'diet.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.now())


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    logged = session.get('user_id')
    if(not logged):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('რეგისტრაცია წარმატებით გაიარეთ.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    logged = session.get('user_id')
    if(not logged):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['username'] = username
                flash('წარმატებით შეხვედით!', 'success')
                return redirect(url_for('home'))
            else:
                flash('არასწორი მომხარებლის სახელი ან პაროლი.', 'error')
        return render_template('login.html')
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('თქვენ გამოხვედით.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

