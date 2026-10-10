/**
 * ResultCard component
 *
 * Displays the prediction result returned by POST /api/predict.
 * Shows the potable/not-potable label, probability scores, and
 * the mandatory screening disclaimer.
 *
 * Props
 * -----
 * result   — PredictionResponse object from the API
 * onReset  — called when the user clicks "Try another sample"
 * error    — string error message (shown instead of result when set)
 */

export function ResultCard({ result, error, onReset }) {
  // ── Error state ────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        className="rounded-xl border border-red-200 bg-red-50 p-6"
      >
        <div className="flex items-start gap-3">
          <ErrorIcon />
          <div className="flex-1">
            <h3 className="font-semibold text-red-800 text-base">
              Prediction failed
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
        <button
          onClick={onReset}
          className="mt-4 px-5 py-2 rounded-lg text-sm font-semibold
            border border-red-300 text-red-700 bg-white
            hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-400
            focus:ring-offset-2 transition-colors"
        >
          Try again
        </button>
      </div>
    )
  }

  if (!result) return null

  const { potable, probability_potable, probability_not_potable, disclaimer } = result

  // Percentage strings for display
  const pctPotable    = probability_potable    != null ? Math.round(probability_potable    * 100) : null
  const pctNotPotable = probability_not_potable != null ? Math.round(probability_not_potable * 100) : null

  return (
    <div
      role="region"
      aria-label="Prediction result"
      className={[
        'rounded-xl border-2 p-6',
        potable
          ? 'border-emerald-300 bg-emerald-50'
          : 'border-amber-300 bg-amber-50',
      ].join(' ')}
    >
      {/* ── Verdict ─────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 mb-4">
        {potable ? <DropIcon potable /> : <DropIcon potable={false} />}
        <div>
          <p className="text-xs uppercase tracking-wider font-semibold text-gray-500 mb-0.5">
            Screening result
          </p>
          <h3
            className={[
              'text-2xl font-bold',
              potable ? 'text-emerald-700' : 'text-amber-700',
            ].join(' ')}
          >
            {potable ? 'Potable label' : 'Not-potable label'}
          </h3>
          <p className={[
            'text-sm mt-0.5',
            potable ? 'text-emerald-600' : 'text-amber-600',
          ].join(' ')}>
            {potable
              ? 'The model assigned the dataset\'s "potable" class to this sample.'
              : 'The model assigned the dataset\'s "not potable" class to this sample.'}
          </p>
        </div>
      </div>

      {/* ── Probability bars ─────────────────────────────────────────────── */}
      {(pctPotable !== null || pctNotPotable !== null) && (
        <div className="space-y-3 mb-5">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Model confidence
          </p>
          {pctPotable !== null && (
            <ProbBar
              label="Potable label"
              percent={pctPotable}
              colorClass="bg-emerald-400"
              textClass="text-emerald-800"
            />
          )}
          {pctNotPotable !== null && (
            <ProbBar
              label="Not-potable label"
              percent={pctNotPotable}
              colorClass="bg-amber-400"
              textClass="text-amber-800"
            />
          )}
        </div>
      )}

      {/* ── Disclaimer ───────────────────────────────────────────────────── */}
      <div className="rounded-lg bg-white/70 border border-gray-200 p-3">
        <p className="text-xs text-gray-500 leading-relaxed">
          <span className="font-semibold text-gray-600">⚠ Screening only — </span>
          {disclaimer}
        </p>
      </div>

      {/* ── Reset ────────────────────────────────────────────────────────── */}
      <button
        onClick={onReset}
        className="mt-5 px-5 py-2 rounded-lg text-sm font-semibold
          border border-gray-300 text-gray-700 bg-white
          hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-aqua-400
          focus:ring-offset-2 transition-colors"
      >
        Try another sample
      </button>
    </div>
  )
}

// ── Sub-components ───────────────────────────────────────────────────────────

function ProbBar({ label, percent, colorClass, textClass }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className={`font-medium ${textClass}`}>{label}</span>
        <span className={`font-bold ${textClass}`}>{percent}%</span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-gray-200 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${colorClass}`}
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${label}: ${percent}%`}
        />
      </div>
    </div>
  )
}

function DropIcon({ potable }) {
  return potable ? (
    <span className="text-4xl" aria-hidden="true">💧</span>
  ) : (
    <span className="text-4xl" aria-hidden="true">⚠️</span>
  )
}

function ErrorIcon() {
  return (
    <svg
      className="w-5 h-5 text-red-500 mt-0.5 shrink-0"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 9v3m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
      />
    </svg>
  )
}
