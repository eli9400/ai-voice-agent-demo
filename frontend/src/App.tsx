import { useState } from 'react'
import './App.css'

type HealthResponse = {
  status: string
  service: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)

  const handleCheckHealth = async () => {
    setLoading(true)
    setError('')
    setHealth(null)

    try {
      const response = await fetch('http://localhost:8000/health')

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = (await response.json()) as HealthResponse
      setHealth(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to fetch backend health: ${message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <h1>AI Voice Agent Demo</h1>
      <button type="button" onClick={handleCheckHealth} disabled={loading}>
        {loading ? 'Checking...' : 'Check Backend Health'}
      </button>

      {health ? (
        <pre>{JSON.stringify(health, null, 2)}</pre>
      ) : null}

      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
    </main>
  )
}

export default App
