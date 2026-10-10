/**
 * usePrediction hook
 *
 * Manages the lifecycle of a single prediction request:
 *   idle → loading → result | error
 *
 * Usage:
 *   const { status, result, error, predict, reset } = usePrediction()
 *
 *   status: 'idle' | 'loading' | 'success' | 'error'
 *   result: PredictionResponse object (when status === 'success')
 *   error:  string message (when status === 'error')
 *   predict(sampleObject): triggers the API call
 *   reset(): returns to idle, clears result and error
 */

import { useState, useCallback } from 'react'
import { predictPotability } from '../services/api'

export function usePrediction() {
  const [status, setStatus] = useState('idle')   // 'idle' | 'loading' | 'success' | 'error'
  const [result, setResult] = useState(null)
  const [error,  setError]  = useState(null)

  const predict = useCallback(async (sample) => {
    // Prevent double-submission
    if (status === 'loading') return

    setStatus('loading')
    setResult(null)
    setError(null)

    try {
      const data = await predictPotability(sample)
      setResult(data)
      setStatus('success')
    } catch (err) {
      setError(err.message ?? 'An unexpected error occurred.')
      setStatus('error')
    }
  }, [status])

  const reset = useCallback(() => {
    setStatus('idle')
    setResult(null)
    setError(null)
  }, [])

  return { status, result, error, predict, reset }
}
