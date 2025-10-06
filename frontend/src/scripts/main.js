import axios from 'axios'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

const elements = {
  tickerSelect: document.getElementById('ticker'),
  historyRange: document.getElementById('history-range'),
  predictionForm: document.getElementById('prediction-form'),
  predictButton: document.getElementById('predict-button'),
  statusMessage: document.getElementById('status-message'),
  resultSection: document.getElementById('result-section'),
  chartSection: document.getElementById('chart-section'),
  resultTicker: document.getElementById('result-ticker'),
  resultPrice: document.getElementById('result-price'),
  resultMovingAverage: document.getElementById('result-moving-average'),
  resultConfidence: document.getElementById('result-confidence')
}

let historyChart = null

const setStatus = (message, type = 'info') => {
  elements.statusMessage.textContent = message
  elements.statusMessage.className = `status-message ${type}`
  elements.statusMessage.hidden = false
}

const clearStatus = () => {
  elements.statusMessage.hidden = true
  elements.statusMessage.textContent = ''
  elements.statusMessage.className = 'status-message'
}

const setLoading = (isLoading) => {
  elements.predictButton.disabled = isLoading
  elements.predictButton.textContent = isLoading ? 'Predicting...' : 'Predict Price'
}

const formatCurrency = (value) => `$${Number(value).toFixed(2)}`

const fetchTickers = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/tickers`)
    const { tickers } = response.data

    if (!tickers || tickers.length === 0) {
      setStatus('No tickers available. Please add stock data in backend.', 'warning')
      return
    }

    elements.tickerSelect.innerHTML = '<option value="">Select ticker...</option>'

    tickers.forEach((ticker) => {
      const option = document.createElement('option')
      option.value = ticker
      option.textContent = ticker
      elements.tickerSelect.appendChild(option)
    })

    clearStatus()
  } catch (error) {
    setStatus(`Failed to load tickers: ${error.response?.data?.error || error.message}`, 'error')
  }
}

const fetchHistoricalData = async (ticker, days = 5) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/historical/${ticker}?days=${days}`)
    return response.data.historical_data || []
  } catch (error) {
    setStatus(`Failed to load historical data: ${error.response?.data?.error || error.message}`, 'error')
    return []
  }
}

const renderHistoryChart = (historicalData, ticker) => {
  if (!elements.chartSection) return

  if (historyChart) {
    historyChart.destroy()
  }

  const labels = historicalData.map((item) => item.date).reverse()
  const prices = historicalData.map((item) => item.price).reverse()

  const ctx = document.getElementById('history-chart')
  if (!ctx) return

  historyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: `${ticker} Price`,
          data: prices,
          borderColor: '#2563eb',
          tension: 0.3,
          fill: false,
          pointBackgroundColor: '#2563eb'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: (value) => formatCurrency(value)
          }
        }
      }
    }
  })

  elements.chartSection.hidden = historicalData.length === 0
}

const updatePredictionResult = (data) => {
  elements.resultTicker.textContent = data.ticker
  elements.resultPrice.textContent = formatCurrency(data.prediction)
  elements.resultMovingAverage.textContent = formatCurrency(data.moving_average)
  elements.resultConfidence.textContent = data.confidence
  elements.resultSection.hidden = false
}

const handlePredict = async (event) => {
  event.preventDefault()

  const ticker = elements.tickerSelect.value
  if (!ticker) {
    setStatus('Please select a ticker symbol', 'warning')
    return
  }

  const days = Number(elements.historyRange.value) || 5

  setLoading(true)
  setStatus('Calculating prediction...', 'info')

  try {
    const predictionResponse = await axios.post(`${API_BASE_URL}/predict`, { ticker })
    updatePredictionResult(predictionResponse.data)

    const historicalData = await fetchHistoricalData(ticker, days)
    if (historicalData.length > 0) {
      renderHistoryChart(historicalData, ticker)
    }

    clearStatus()
  } catch (error) {
    const errorMessage = error.response?.data?.error || 'Failed to get prediction'
    setStatus(errorMessage, 'error')
  } finally {
    setLoading(false)
  }
}

const initApp = () => {
  fetchTickers()
  elements.predictionForm.addEventListener('submit', handlePredict)

  elements.historyRange.addEventListener('change', async () => {
    const ticker = elements.resultTicker?.textContent

    if (!ticker || ticker === '-') return

    const days = Number(elements.historyRange.value) || 5
    const historicalData = await fetchHistoricalData(ticker, days)
    renderHistoryChart(historicalData, ticker)
  })
}

const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    try {
      await navigator.serviceWorker.register('/service-worker.js')
    } catch (error) {
      // Silent fail for service worker registration
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initApp()
  registerServiceWorker()
})

