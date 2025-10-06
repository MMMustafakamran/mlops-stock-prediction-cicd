import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import axios from 'axios'

vi.mock('axios')

document.body.innerHTML = `
  <select id="ticker"></select>
  <select id="history-range"></select>
  <form id="prediction-form"></form>
  <button id="predict-button"></button>
  <div id="status-message"></div>
  <section id="result-section"></section>
  <section id="chart-section"></section>
  <span id="result-ticker"></span>
  <span id="result-price"></span>
  <span id="result-moving-average"></span>
  <span id="result-confidence"></span>
  <canvas id="history-chart"></canvas>
`

describe('Frontend Prediction Flow', () => {
  beforeEach(() => {
    vi.resetAllMocks()

    axios.get.mockResolvedValueOnce({
      data: {
        tickers: ['AAPL', 'GOOGL', 'TSLA'],
        count: 3
      }
    })

    axios.post.mockImplementation((url, data) => {
      if (url.includes('/predict')) {
        return Promise.resolve({
          data: {
            ticker: data.ticker,
            prediction: 151.24,
            moving_average: 150.67,
            confidence: 'Medium'
          }
        })
      }
      return Promise.resolve({ data: {} })
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches tickers and populates dropdown', async () => {
    await import('../src/scripts/main.js')

    const tickerSelect = document.getElementById('ticker')
    expect(tickerSelect.children.length).toBeGreaterThan(0)
  })

  it('handles prediction request successfully', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        historical_data: [
          { date: '2024-10-04', price: 151.2 },
          { date: '2024-10-03', price: 148.75 },
          { date: '2024-10-02', price: 152.3 }
        ]
      }
    })

    const tickerSelect = document.getElementById('ticker')
    tickerSelect.innerHTML = '<option value="AAPL">AAPL</option>'
    tickerSelect.value = 'AAPL'

    const predictionForm = document.getElementById('prediction-form')
    const submitEvent = new Event('submit')

    await import('../src/scripts/main.js')

    predictionForm.dispatchEvent(submitEvent)

    await Promise.resolve()
    await Promise.resolve()
    await Promise.resolve()

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/predict'),
      { ticker: 'AAPL' }
    )
  })

  it('handles prediction errors gracefully', async () => {
    axios.post.mockRejectedValueOnce({
      response: { data: { error: 'Invalid ticker' } }
    })

    axios.get.mockResolvedValue({
      data: {
        tickers: ['AAPL', 'GOOGL'],
        historical_data: []
      }
    })

    const tickerSelect = document.getElementById('ticker')
    tickerSelect.innerHTML = '<option value="AAPL">AAPL</option>'
    tickerSelect.value = 'AAPL'

    const predictionForm = document.getElementById('prediction-form')
    const submitEvent = new Event('submit')

    await import('../src/scripts/main.js')

    predictionForm.dispatchEvent(submitEvent)

    await Promise.resolve()
    await Promise.resolve()

    expect(axios.post).toHaveBeenCalled()
  })
})

