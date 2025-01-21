from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask (__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/articles')
def articles():
    return render_templates('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_templates('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Name', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password= PasswordField('Password', [
        validators.DataRequired(),
        validatirs.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route("/register,", nethod=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
    