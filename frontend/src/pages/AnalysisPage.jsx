/**
 * AnalysisPage
 *
 * Hosts the water-quality form, result card, and the model info note.
 * Content migrated from the original App.jsx single-page layout.
 *
 * Phase F: when a user is logged-in and a prediction succeeds,
 * the analysis is automatically saved to the backend history.
 */

import { useState, useEffect } from 'react'

import { WaterForm }    from '../components/WaterForm'
import { ResultCard }   from '../components/ResultCard'
import { usePrediction } from '../hooks/usePrediction'
import { useAuth }      from '../hooks/useAuth'
import { saveAnalysis } from '../services/api'

export default function AnalysisPage() {
  const { status, result, error, predict, reset } = usePrediction()
  const { user, token } = useAuth()

  const isLoading = status === 'loading'
  const hasResult = status === 'success' || status === 'error'

  const [lastSample, setLastSample] = useState(null)
  const [savedId,    setSavedId]    = useState(null)

  const handleSubmit = async (sample) => {
    setLastSample(sample)
    setSavedId(null)
    await predict(sample)
  }

  const handleReset = () => {
    reset()
    setLastSample(null)
    setSavedId(null)
  }

  // Phase F: auto-save when authenticated user gets a successful prediction.
  useEffect(() => {
    if (result && lastSample && user && token && savedId === null) {
      setSavedId('saving')
      saveAnalysis(token, {
        ...lastSample,
        potable_label:       result.potable_label,
        probability_potable: result.probability_potable ?? null,
      })
        .then((saved) => setSavedId(saved?.id ?? 'saved'))
        .catch(() => setSavedId('error'))
    }
  }, [result, lastSample, user, token, savedId])

  return (
    <>
      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <div className="bg-gradient-to-b from-aqua-600 to-aqua-700 text-white">
        <div className="max-w-5xl mx-auto px-4 py-10">
          <h2 className="text-3xl font-bold mb-2">
            Water Potability Screening
          </h2>
          <p className="text-aqua-100 text-base max-w-2xl leading-relaxed">
            Enter nine water-quality measurements to receive a preliminary
            potability prediction from our trained machine-learning model.
            This tool is for screening and educational purposes only — it does
            not replace certified laboratory water-quality testing.
          </p>
        </div>
      </div>

      {/* ── Main content ────────────────────────────────────────────────── */}
      <main className="max-w-5xl mx-auto px-4 py-8">

        {hasResult && (
          <div className="mb-8" aria-live="polite">
            <ResultCard result={result} error={error} onReset={handleReset} />
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-sm border border-aqua-100 p-6 md:p-8">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-aqua-800">
              Water Sample Measurements
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              All nine fields are required. Enter the values from your water
              analysis report or sensor readings.
            </p>
          </div>

          <WaterForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            onReset={handleReset}
          />
        </div>

        {/* Model info note */}
        <div className="mt-6 rounded-xl bg-white border border-aqua-100 p-4
          flex gap-3 items-start">
          <InfoIcon />
          <div className="text-xs text-gray-500 leading-relaxed">
            <span className="font-semibold text-gray-600">About this model — </span>
            Predictions are made by a Random Forest classifier trained on the
            Kaggle Water Potability dataset (3,276 samples).
            Training-set cross-validation ROC-AUC: 0.70.
            Test-set accuracy: 65%. The dataset labels are not certified by any
            water authority. AquaPura is a student AI/ML project demonstrating
            SDG 6 alignment.
          </div>
        </div>
      </main>
    </>
  )
}

function InfoIcon() {
  return (
    <svg
      className="w-4 h-4 text-aqua-400 mt-0.5 shrink-0"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 110 20A10 10 0 0112 2z"
      />
    </svg>
  )
}
