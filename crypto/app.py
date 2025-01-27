from flask import Flask, render_template, session
from flask_socketio import SocketIO
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = "secrete123"
socketio = SocketIO(app)

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

@app.route("/market")
def market_cap():
    session["currency"] = session.get("currency", "usd")
    data = fetch_crypto_data()
    return render_template("market_cap.html", data={"crypto_data": data, "currency": session["currency"]})

@socketio.on("fetch_data")
def handle_realtime_data():
    # Send updated data to the client in real-time
    data = fetch_crypto_data()
    socketio.emit("update_data", {"crypto_data": data})

@app.route("/market-cap")
def market_cap():
    currency = session["currency"]
    # Replace these with actual API data
    market_cap_data = {
        "marketCap": {"BTC": 600000000, "ETH": 400000000, "Others": 200000000},
        "volume": {"BTC": 1500, "ETH": 900, "Others": 600},
        "trend": [1.2, 1.3, 1.5, 1.4, 1.6, 1.8, 2.0],
        "dates": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
    }
    return render_template(
        "market_cap.html", data={"marketData": market_cap_data, "currency": currency}
    )

# Define the custom filter for formatting currency
def format_currency(value, symbol="$"):
    """
    Format a number as currency.
    
    Args:
        value (float): The number to format.
        symbol (str): The currency symbol (default is "$").
    
    Returns:
        str: The formatted currency string.
    """
    try:
        return f"{symbol}{value:,.2f}"  # Format number with 2 decimal places and thousands separator
    except (ValueError, TypeError):
        return value  # Return the original value if formatting fails

# Register the filter with Jinja2
app.jinja_env.filters["currency"] = format_currency

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

# Background data fetch
market_data = {}
news_data = []

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


@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/favorites")
def favorites():
    return render_template("favorites.html")


if __name__ == "__main__":
    socketio.run(app, debug=True)
