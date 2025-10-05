import pytest
import json
import os
import tempfile
from app import app, init_db, DATABASE

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Use a temporary database for testing
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'Stock Prediction API' in data['service']

def test_predict_valid_ticker(client):
    """Test prediction with valid ticker"""
    response = client.post('/predict', 
                          data=json.dumps({'ticker': 'AAPL'}),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['ticker'] == 'AAPL'
    assert 'prediction' in data
    assert 'historical_prices' in data
    assert 'moving_average' in data
    assert data['prediction'] is not None

def test_predict_invalid_ticker(client):
    """Test prediction with invalid/unknown ticker"""
    response = client.post('/predict', 
                          data=json.dumps({'ticker': 'INVALID'}),
                          content_type='application/json')
    
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data
    assert data['ticker'] == 'INVALID'

def test_predict_missing_ticker(client):
    """Test prediction without ticker"""
    response = client.post('/predict', 
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing ticker symbol' in data['error']

def test_predict_empty_ticker(client):
    """Test prediction with empty ticker"""
    response = client.post('/predict', 
                          data=json.dumps({'ticker': ''}),
                          content_type='application/json')
    
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Invalid ticker symbol' in data['error']

def test_get_historical_data(client):
    """Test getting historical data"""
    response = client.get('/historical/AAPL')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['ticker'] == 'AAPL'
    assert 'historical_data' in data
    assert 'count' in data
    assert isinstance(data['historical_data'], list)

def test_get_historical_data_with_limit(client):
    """Test getting historical data with limit"""
    response = client.get('/historical/AAPL?days=2')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['ticker'] == 'AAPL'
    assert len(data['historical_data']) <= 2

def test_add_stock_price(client):
    """Test adding new stock price"""
    new_price_data = {
        'ticker': 'TEST',
        'date': '2024-10-05',
        'price': 100.50
    }
    
    response = client.post('/add_price',
                          data=json.dumps(new_price_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'successfully' in data['message']

def test_add_stock_price_missing_fields(client):
    """Test adding stock price with missing fields"""
    incomplete_data = {
        'ticker': 'TEST'
        # Missing date and price
    }
    
    response = client.post('/add_price',
                          data=json.dumps(incomplete_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing required fields' in data['error']

def test_get_available_tickers(client):
    """Test getting available tickers"""
    response = client.get('/tickers')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'tickers' in data
    assert 'count' in data
    assert isinstance(data['tickers'], list)
    assert len(data['tickers']) > 0

def test_case_insensitive_ticker(client):
    """Test that ticker symbols are case insensitive"""
    # Test lowercase
    response1 = client.post('/predict', 
                           data=json.dumps({'ticker': 'aapl'}),
                           content_type='application/json')
    
    # Test uppercase
    response2 = client.post('/predict', 
                           data=json.dumps({'ticker': 'AAPL'}),
                           content_type='application/json')
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)
    
    assert data1['ticker'] == data2['ticker'] == 'AAPL'

if __name__ == '__main__':
    pytest.main(['-v', __file__])
