from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import os
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Database configuration
DATABASE = 'stock_data.db'

def init_db():
    """Initialize the database with sample stock data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create table for historical stock prices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            price REAL NOT NULL,
            UNIQUE(ticker, date)
        )
    ''')
    
    # Insert sample data for testing
    sample_data = [
        ('AAPL', '2024-10-01', 150.25),
        ('AAPL', '2024-10-02', 152.30),
        ('AAPL', '2024-10-03', 148.75),
        ('AAPL', '2024-10-04', 151.20),
        ('GOOGL', '2024-10-01', 2750.50),
        ('GOOGL', '2024-10-02', 2780.25),
        ('GOOGL', '2024-10-03', 2765.75),
        ('GOOGL', '2024-10-04', 2790.30),
        ('TSLA', '2024-10-01', 245.80),
        ('TSLA', '2024-10-02', 248.90),
        ('TSLA', '2024-10-03', 242.15),
        ('TSLA', '2024-10-04', 250.45),
    ]
    
    for ticker, date, price in sample_data:
        cursor.execute('''
            INSERT OR IGNORE INTO stock_prices (ticker, date, price)
            VALUES (?, ?, ?)
        ''', (ticker, date, price))
    
    conn.commit()
    conn.close()

def get_historical_prices(ticker: str, days: int = 3) -> List[float]:
    """Get the last N days of stock prices for a ticker"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT price FROM stock_prices 
        WHERE ticker = ? 
        ORDER BY date DESC 
        LIMIT ?
    ''', (ticker.upper(), days))
    
    prices = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return prices

def calculate_moving_average(prices: List[float]) -> float:
    """Calculate simple moving average of prices"""
    if not prices:
        return 0.0
    return sum(prices) / len(prices)

def predict_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Rule-based stock prediction using moving average of last 3 days
    This is a simple rule-based approach, not ML
    """
    try:
        # Get last 3 days of prices
        historical_prices = get_historical_prices(ticker, 3)
        
        if len(historical_prices) < 3:
            return {
                'error': f'Insufficient data for {ticker}. Need at least 3 days of historical data.',
                'ticker': ticker,
                'prediction': None
            }
        
        # Calculate moving average (our prediction rule)
        moving_avg = calculate_moving_average(historical_prices)
        
        # Add some simple trend analysis
        if len(historical_prices) >= 2:
            recent_trend = historical_prices[0] - historical_prices[1]
            # Adjust prediction based on trend (simple rule)
            trend_factor = 0.1  # 10% weight to recent trend
            predicted_price = moving_avg + (recent_trend * trend_factor)
        else:
            predicted_price = moving_avg
        
        return {
            'ticker': ticker.upper(),
            'prediction': round(predicted_price, 2),
            'historical_prices': historical_prices,
            'moving_average': round(moving_avg, 2),
            'method': 'Moving Average (3-day) with Trend Adjustment',
            'confidence': 'Medium (Rule-based prediction)'
        }
        
    except Exception as e:
        return {
            'error': f'Error predicting price for {ticker}: {str(e)}',
            'ticker': ticker,
            'prediction': None
        }

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Stock Prediction API',
        'version': '1.0.0'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict stock price for given ticker"""
    try:
        data = request.get_json()
        
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Missing ticker symbol'}), 400
        
        ticker = data['ticker'].strip().upper()
        
        if not ticker:
            return jsonify({'error': 'Invalid ticker symbol'}), 400
        
        prediction_result = predict_stock_price(ticker)
        
        if 'error' in prediction_result:
            return jsonify(prediction_result), 404
        
        return jsonify(prediction_result)
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/historical/<ticker>', methods=['GET'])
def get_historical_data(ticker):
    """Get historical data for a ticker"""
    try:
        days = request.args.get('days', 10, type=int)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, price FROM stock_prices 
            WHERE ticker = ? 
            ORDER BY date DESC 
            LIMIT ?
        ''', (ticker.upper(), days))
        
        data = [{'date': row[0], 'price': row[1]} for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'ticker': ticker.upper(),
            'historical_data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching historical data: {str(e)}'}), 500

@app.route('/add_price', methods=['POST'])
def add_stock_price():
    """Add new stock price data (for testing purposes)"""
    try:
        data = request.get_json()
        
        required_fields = ['ticker', 'date', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: ticker, date, price'}), 400
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO stock_prices (ticker, date, price)
            VALUES (?, ?, ?)
        ''', (data['ticker'].upper(), data['date'], float(data['price'])))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Stock price added successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Error adding stock price: {str(e)}'}), 500

@app.route('/tickers', methods=['GET'])
def get_available_tickers():
    """Get list of available tickers"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT ticker FROM stock_prices ORDER BY ticker')
        tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'tickers': tickers,
            'count': len(tickers)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching tickers: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
