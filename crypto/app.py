from flask import Flask, render_template, session
from flask_socketio import SocketIO
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"
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


if __name__ == "__main__":
    socketio.run(app, debug=True)
