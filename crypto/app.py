
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management
socketio = SocketIO(app)

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
