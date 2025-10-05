# Stock Prediction Backend API

A Flask-based REST API that provides rule-based stock price predictions using moving averages.

## Features

- **Rule-based prediction**: Uses 3-day moving average with trend adjustment
- **Historical data storage**: SQLite database for stock price history
- **RESTful API**: Clean endpoints for predictions and data management
- **Comprehensive testing**: Full test suite with pytest
- **Docker support**: Containerized for easy deployment

## API Endpoints

### Health Check
- `GET /` - Check API health status

### Stock Prediction
- `POST /predict` - Get stock price prediction
  ```json
  {
    "ticker": "AAPL"
  }
  ```

### Historical Data
- `GET /historical/<ticker>` - Get historical prices
- `GET /historical/<ticker>?days=N` - Limit to N days

### Data Management
- `POST /add_price` - Add new stock price data
- `GET /tickers` - Get available ticker symbols

## Prediction Algorithm

The API uses a simple rule-based approach:
1. Fetch last 3 days of historical prices
2. Calculate moving average
3. Apply trend adjustment (10% weight to recent trend)
4. Return prediction with confidence metrics

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Run tests
pytest test_app.py -v
```

## Docker Usage

```bash
# Build image
docker build -t stock-prediction-backend .

# Run container
docker run -p 5000:5000 stock-prediction-backend
```

## Sample Data

The API comes pre-loaded with sample data for:
- AAPL (Apple Inc.)
- GOOGL (Alphabet Inc.)
- TSLA (Tesla Inc.)

## Testing

Run the test suite:
```bash
pytest test_app.py -v
```

Tests cover:
- API endpoint functionality
- Error handling
- Data validation
- Edge cases
