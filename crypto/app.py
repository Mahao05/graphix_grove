from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, sesssion, jsonify
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_socketio import SocketIO
import requests
import threading
import time
import os

app = Flask (__name__)
app.secret_key='key1105'
socketio = SocketIO(app)


# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MySQL_USER'] = 'root'
app.config['MySQL_PASSWORD'] = 'Dont firget to add password'
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

Articles = Articles()

# Index
@app.route('/')
def home():
    return render_template('home.html')

# Articles    
@app.route('/articles')
def articles():
    return render_templates('articles.html', articles = Articles)

# Single Article
@app.route('/article/<string:id>/')
def article(id):
    return render_templates('article.html', id=id)

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Name', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password= PasswordField('Password', [
        validators.DataRequired(),
        validatirs.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route("/register,", nethod=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password =  sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSEET INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close

        flah('You are now registered and can log in', 'success')
        
        return redirect(url_for('login'))  
    return render_template('register.html', form=form)

#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        results = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Password
            if sha256_crypt.verify(password_candidate, password):
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap    

# Logout
@app_route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
    
        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO articles(titles, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))
    
        # Commit to DB
        mysql.connection.commit()

        # Close connection
        curl.close()

        flash('Article Created', 'success')
        
        return redirect(url_for('dashboard'))
   
    return render_template('add_article.html', form=form)

# Background data fetch
market_data = {}
news_data = []

#Add data
def fetch_data():
    global market_data, news_data
    while True:
        try:
            # Fetch market cap data
            market_data_response = requests.get("https://api.coingecko.com/api/v3/global").json()
            market_data = market_data_response['data']['total_market_cap']

            # Fetch crypto news
            news_response = requests.get("https://cryptopanic.com/api/v1/posts/?auth_token=YOUR_API_KEY").json()
            news_data = news_response['results']

            # Send data to the frontend via SocketIO
            socketio.emit("updateData", {"marketCap": market_data, "news": news_data})

            time.sleep(10)
        except Exception as e:
            print("Error fetching data:", e)

# Start background thread
threading.Thread(target=fetch_data, daemon=True).start()

# Routes
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/market")
def market_cap():
    return render_template(".html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/favorites")
def favorites():
    return render_template("favorites.html")

@app.route("/price")
def price():
    return render_template("price.html")

# Default currency
@app.before_request
def set_default_currency():
    if "currency" not in session:
        session["currency"] = "USD"

# Route to set currency
@app.route("/set-currency")
def set_currency():
    currency = request.args.get("currency", "USD")
    session["currency"] = currency
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/")
def dashboard():
    currency = session["currency"]
    # Example data to pass to the template
    data = {"marketCap": {"BTC": 500000000, "ETH": 300000000}, "currency": currency}
    return render_template("dashboard.html", data=data)

@app.template_filter("format_currency")
def format_currency(value, currency):
    if currency == "USD":
        return f"${value:,}"
    elif currency == "EUR":
        return f"€{value:,}"
    elif currency == "GBP":
        return f"£{value:,}"
    elif currency == "JPY":
        return f"¥{value:,}"
    return f"{value:,} {currency}"

# Helper function to fetch live data
def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": session.get("currency", "usd"),
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false",
    }
    response = requests.get(url, params=params)
    return response.json()

@app.route("/dashboard")
def dashboard():
    session["currency"] = session.get("currency", "usd")
    data = fetch_crypto_data()
    return render_template("dashboard.html", data={"crypto_data": data, "currency": session["currency"]})


@socketio.on("fetch_data")
def handle_realtime_data():
    # Send updated data to the client in real-time
    data = fetch_crypto_data()
    socketio.emit("update_data", {"crypto_data"}



if __name__ == '__main__':
    socketio.run(app, debug=True) 
    port = int(os.environ.get("PORT", 4000)) 
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
     
