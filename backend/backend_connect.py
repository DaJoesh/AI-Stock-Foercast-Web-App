from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta, timezone
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import MinMaxScaler
from keras.layers import LSTM, Dense
from keras.models import Sequential
import yfinance as yf
import os
from dotenv import load_dotenv
import jwt

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.debug = False
CORS(app)
db = SQLAlchemy(app)

# Define database models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_pass = db.Column(db.String(50), nullable=False)

class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    stock_ticker = db.Column(db.String(10), nullable=False)
    stock_startDate = db.Column(db.Date, nullable=False)
    stock_endDate = db.Column(db.Date, nullable=False)
    stock_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('stocks', lazy=True))

@app.route('/')
def index():
    return jsonify(message='Hello from Flask backend!')

# Signup route
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if username already exists
    if User.query.filter_by(user_name=username).first():
        return jsonify(message="Username already exists"), 400

    # Create a new user object
    new_user = User(user_name=username, user_pass=password)

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message="Signup successful"), 201

# Signin route
@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    utc_now = datetime.now(timezone.utc)
    utc_expiration = utc_now + timedelta(hours=1)

    # Query the database for the user
    user = User.query.filter_by(user_name=username).first()

    if user:
        # Check if password matches
        if user.user_pass == password:
            # Generate a token
            token = jwt.encode({'user_id': user.user_id, 'exp': utc_expiration}, app.config['SECRET_KEY'])
            return jsonify(token=token), 200
        else:
            return jsonify(message="Invalid password"), 401
    else:
        return jsonify(message="User not found"), 401
    
# function to perform stock forecast
def perform_forecast(ticker, start_date):
    # Get the Dataset
    end_date = date.today().strftime("%Y-%m-%d")
    data = yf.download(ticker, start=start_date, end=end_date)

    # Set target variable as the closing price
    output_var = pd.DataFrame(data['Adj Close'])
    # Selecting the features
    features = ['Open','High','Low','Volume']

    # Setting up scaler
    scaler = MinMaxScaler()
    feature_transform = scaler.fit_transform(data[features])
    feature_transform = pd.DataFrame(data=feature_transform, columns=features, index=data.index)

    # Data Proessing for LSTM
    X = feature_transform.values.reshape(-1, 1, len(features))

    # LSTM Model
    lstm = Sequential()
    lstm.add(LSTM(32, input_shape=(X.shape[1], X.shape[2]), activation='relu', return_sequences=False))
    lstm.add(Dense(1))
    lstm.compile(loss='mean_squared_error', optimizer='adam')

    # Training the Model
    lstm.fit(X, output_var, epochs=200, batch_size=8, verbose=0, shuffle=False)

    # Fetch the latest data and make a future prediction
    latest_data = data[features].iloc[-1].values.reshape(1, len(features))
    latest_data_scaled = scaler.transform(latest_data)
    next_day_prediction = lstm.predict(latest_data_scaled.reshape(1, 1, len(features)))
    return next_day_prediction[0, 0]

# route for performing forecast
@app.route('/api/forecast', methods=['POST'])
def forecast():
    data = request.json
    ticker = data.get('ticker')
    start_date = data.get('startDate')
    forecasted_value = perform_forecast(ticker, start_date)
    return jsonify(forecastValue=float(forecasted_value)), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')