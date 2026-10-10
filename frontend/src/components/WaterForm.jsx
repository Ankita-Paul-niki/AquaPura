/**
 * WaterForm component
 *
 * Renders the nine water-quality measurement fields, performs client-side
 * validation, and calls onSubmit with the validated numeric sample object.
 *
 * Props
 * -----
 * onSubmit(sample)  — called with a plain object of 9 numeric values
 * isLoading         — disables the submit button while a request is in flight
 * onReset           — called when the user clicks "Reset form"
 */

import { useState } from 'react'

// ── Field metadata ──────────────────────────────────────────────────────────
// Each entry drives the label, unit, description, and validation for one field.
// The `key` must match the exact JSON field name accepted by the API.
const FIELDS = [
  {
    key: 'ph',
    label: 'pH',
    unit: '(0 – 14)',
    description: 'Acidity / alkalinity of the water. WHO safe range: 6.5 – 8.5.',
    min: 0,
    max: 14,
    placeholder: 'e.g. 7.0',
    step: '0.01',
  },
  {
    key: 'hardness',
    label: 'Hardness',
    unit: 'mg/L',
    description: 'Dissolved calcium and magnesium salts.',
    min: 0.001,
    placeholder: 'e.g. 150',
    step: '0.1',
  },
  {
    key: 'solids',
    label: 'Total Dissolved Solids',
    unit: 'ppm',
    description: 'Total dissolved solids (TDS). Typical drinking-water limit: < 500 ppm (EPA).',
    min: 0.001,
    placeholder: 'e.g. 20000',
    step: '1',
  },
  {
    key: 'chloramines',
    label: 'Chloramines',
    unit: 'ppm',
    description: 'Disinfectant added during water treatment. EPA limit: ≤ 4 ppm.',
    min: 0,
    placeholder: 'e.g. 7.0',
    step: '0.01',
  },
  {
    key: 'sulfate',
    label: 'Sulfate',
    unit: 'mg/L',
    description: 'Naturally occurring dissolved mineral.',
    min: 0,
    placeholder: 'e.g. 250',
    step: '0.1',
  },
  {
    key: 'conductivity',
    label: 'Conductivity',
    unit: 'µS/cm',
    description: 'Electrical conductivity — a proxy for total dissolved ions.',
    min: 0.001,
    placeholder: 'e.g. 400',
    step: '0.1',
  },
  {
    key: 'organic_carbon',
    label: 'Organic Carbon',
    unit: 'ppm',
    description: 'Total organic carbon from decayed natural matter.',
    min: 0,
    placeholder: 'e.g. 14',
    step: '0.01',
  },
  {
    key: 'trihalomethanes',
    label: 'Trihalomethanes',
    unit: 'µg/L',
    description: 'By-products of chlorination. EPA limit: ≤ 80 µg/L.',
    min: 0,
    placeholder: 'e.g. 66',
    step: '0.1',
  },
  {
    key: 'turbidity',
    label: 'Turbidity',
    unit: 'NTU',
    description: 'Cloudiness of the water. WHO guideline: < 1 NTU for drinking water.',
    min: 0,
    placeholder: 'e.g. 4.0',
    step: '0.01',
  },
]

const EMPTY_VALUES = Object.fromEntries(FIELDS.map((f) => [f.key, '']))
const EMPTY_ERRORS = Object.fromEntries(FIELDS.map((f) => [f.key, '']))

// ── Validation ──────────────────────────────────────────────────────────────
function validateField(field, rawValue) {
  if (rawValue === '' || rawValue === null || rawValue === undefined) {
    return 'This field is required.'
  }
  const num = Number(rawValue)
  if (!Number.isFinite(num)) {
    return 'Enter a valid number.'
  }
  if (field.min !== undefined && num < field.min) {
    return field.min === 0
      ? 'Value must be 0 or greater.'
      : `Value must be greater than 0.`
  }
  if (field.max !== undefined && num > field.max) {
    return `Value must be ${field.max} or less.`
  }
  return ''   // no error
}

function validateAll(values) {
  const errors = {}
  let hasError = false
  for (const field of FIELDS) {
    const msg = validateField(field, values[field.key])
    errors[field.key] = msg
    if (msg) hasError = true
  }
  return { errors, hasError }
}

// ── Component ───────────────────────────────────────────────────────────────
export function WaterForm({ onSubmit, isLoading, onReset }) {
  const [values, setValues] = useState(EMPTY_VALUES)
  const [errors, setErrors] = useState(EMPTY_ERRORS)
  const [touched, setTouched] = useState({})

  function handleChange(key, raw) {
    setValues((prev) => ({ ...prev, [key]: raw }))
    // Clear error for this field as soon as the user types
    if (touched[key]) {
      const field = FIELDS.find((f) => f.key === key)
      setErrors((prev) => ({ ...prev, [key]: validateField(field, raw) }))
    }
  }

  function handleBlur(key) {
    setTouched((prev) => ({ ...prev, [key]: true }))
    const field = FIELDS.find((f) => f.key === key)
    setErrors((prev) => ({ ...prev, [key]: validateField(field, values[key]) }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    // Mark all as touched to show every error
    const allTouched = Object.fromEntries(FIELDS.map((f) => [f.key, true]))
    setTouched(allTouched)

    const { errors: newErrors, hasError } = validateAll(values)
    setErrors(newErrors)
    if (hasError) return

    // Convert strings to numbers and submit
    const sample = Object.fromEntries(
      FIELDS.map((f) => [f.key, Number(values[f.key])])
    )
    onSubmit(sample)
  }

  function handleReset() {
    setValues(EMPTY_VALUES)
    setErrors(EMPTY_ERRORS)
    setTouched({})
    onReset()
  }

  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Water quality measurement form">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {FIELDS.map((field) => {
          const hasErr = touched[field.key] && errors[field.key]
          return (
            <div key={field.key}>
              <label
                htmlFor={field.key}
                className="block text-sm font-semibold text-aqua-800 mb-1"
              >
                {field.label}{' '}
                <span className="font-normal text-aqua-500 text-xs">{field.unit}</span>
              </label>
              <input
                id={field.key}
                name={field.key}
                type="number"
                inputMode="decimal"
                step={field.step}
                min={field.min}
                max={field.max}
                placeholder={field.placeholder}
                value={values[field.key]}
                onChange={(e) => handleChange(field.key, e.target.value)}
                onBlur={() => handleBlur(field.key)}
                disabled={isLoading}
                aria-describedby={`${field.key}-desc ${hasErr ? `${field.key}-err` : ''}`}
                aria-invalid={hasErr ? 'true' : 'false'}
                className={[
                  'w-full rounded-lg border px-3 py-2 text-sm bg-white',
                  'focus:outline-none focus:ring-2 focus:ring-aqua-400 focus:border-aqua-400',
                  'disabled:bg-gray-50 disabled:cursor-not-allowed',
                  hasErr
                    ? 'border-red-400 text-red-800'
                    : 'border-aqua-200 text-gray-800',
                ].join(' ')}
              />
              <p
                id={`${field.key}-desc`}
                className="mt-1 text-xs text-gray-400 leading-snug"
              >
                {field.description}
              </p>
              {hasErr && (
                <p
                  id={`${field.key}-err`}
                  role="alert"
                  className="mt-1 text-xs text-red-600 font-medium"
                >
                  {errors[field.key]}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Actions */}
      <div className="mt-8 flex flex-col sm:flex-row gap-3">
        <button
          type="submit"
          disabled={isLoading}
          className={[
            'flex-1 sm:flex-none px-8 py-3 rounded-lg font-semibold text-sm',
            'bg-aqua-600 text-white',
            'hover:bg-aqua-700 active:bg-aqua-800',
            'focus:outline-none focus:ring-2 focus:ring-aqua-400 focus:ring-offset-2',
            'disabled:opacity-60 disabled:cursor-not-allowed',
            'transition-colors duration-150',
          ].join(' ')}
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <SpinnerIcon />
              Analysing…
            </span>
          ) : (
            'Analyse Water Sample'
          )}
        </button>

        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className={[
            'flex-1 sm:flex-none px-6 py-3 rounded-lg font-semibold text-sm',
            'border border-aqua-300 text-aqua-700 bg-white',
            'hover:bg-aqua-50 active:bg-aqua-100',
            'focus:outline-none focus:ring-2 focus:ring-aqua-400 focus:ring-offset-2',
            'disabled:opacity-60 disabled:cursor-not-allowed',
            'transition-colors duration-150',
          ].join(' ')}
        >
          Reset Form
        </button>
      </div>
    </form>
  )
}

function SpinnerIcon() {
  return (
    <svg
      className="animate-spin h-4 w-4 text-white"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  )
}
