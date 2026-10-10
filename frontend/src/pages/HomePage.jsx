/**
 * HomePage
 *
 * Full home page with:
 *  - Hero section with dual CTAs
 *  - Water awareness section
 *  - Parameter info cards
 *  - How it works (3-step)
 *  - Awareness tips
 *  - Final CTA
 */

import { Link } from 'react-router-dom'

// ── Parameter cards data ────────────────────────────────────────────────────
const PARAMETERS = [
  {
    name: 'pH',
    range: '6.5 – 8.5',
    description:
      'Measures acidity/alkalinity. Values outside the WHO range can indicate chemical contamination or corrosive water.',
  },
  {
    name: 'Hardness',
    range: '< 300 mg/L',
    description:
      'Calcium and magnesium concentration. Very hard water can cause scale buildup; very soft water may be corrosive.',
  },
  {
    name: 'Total Dissolved Solids',
    range: '< 500 mg/L',
    description:
      'Sum of all dissolved minerals and salts. High TDS may indicate industrial or agricultural contamination.',
  },
  {
    name: 'Chloramines',
    range: '< 4 mg/L',
    description:
      'Disinfectants added to municipal water. Excessive levels produce harmful by-products.',
  },
  {
    name: 'Sulfate',
    range: '< 250 mg/L',
    description:
      'Naturally occurring mineral. High concentrations cause a bitter taste and can act as a laxative.',
  },
  {
    name: 'Conductivity',
    range: '< 400 µS/cm',
    description:
      "Measures water's ability to conduct electricity — a proxy for total ion concentration.",
  },
  {
    name: 'Organic Carbon',
    range: '< 2 mg/L',
    description:
      'Carbon from decaying organic matter. High levels can indicate contamination and support microbial growth.',
  },
  {
    name: 'Trihalomethanes',
    range: '< 80 µg/L',
    description:
      'By-products of chlorine disinfection. Long-term exposure above safe limits is a health risk.',
  },
  {
    name: 'Turbidity',
    range: '< 4 NTU',
    description:
      'Cloudiness caused by suspended particles. High turbidity may shelter pathogens from disinfection.',
  },
]

// ── How it works steps ───────────────────────────────────────────────────────
const STEPS = [
  {
    number: '1',
    title: 'Collect your measurements',
    body:
      'Obtain the nine water-quality parameters from your water analysis report, home testing kit, or sensor device.',
  },
  {
    number: '2',
    title: 'Enter them into the form',
    body:
      'Navigate to the Analysis page and fill in all nine fields. The form validates each value to the expected numeric range.',
  },
  {
    number: '3',
    title: 'Receive your screening result',
    body:
      'Our Random Forest model returns a potability prediction with a confidence score. Log in to save your results over time.',
  },
]

// ── Awareness tips ───────────────────────────────────────────────────────────
const TIPS = [
  'Boil water for at least 1 minute if you are unsure of its safety.',
  'Test well water at least once a year for bacteria, nitrates, and pH.',
  'Never consume water with a strong chemical smell or unusual colour.',
  'A screening tool does not replace certified laboratory water testing.',
  'Report suspected contamination to your local water authority immediately.',
]

export default function HomePage() {
  return (
    <div className="bg-aqua-50">

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="bg-gradient-to-br from-aqua-700 via-aqua-600 to-aqua-500 text-white">
        <div className="max-w-5xl mx-auto px-4 py-20 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight mb-4">
            Know Your Water.<br className="hidden sm:block" /> Protect Your Health.
          </h1>
          <p className="text-aqua-100 text-lg md:text-xl max-w-2xl mx-auto mb-8 leading-relaxed">
            AquaPura uses machine learning to give you a fast, preliminary water-potability
            screening — helping communities and individuals make informed decisions about
            their water supply.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/analysis"
              className="inline-block bg-white text-aqua-700 font-bold px-8 py-3
                rounded-xl hover:bg-aqua-50 transition-colors shadow"
            >
              Start Analysis
            </Link>
            <Link
              to="/register"
              className="inline-block border-2 border-white text-white font-bold px-8 py-3
                rounded-xl hover:bg-white/10 transition-colors"
            >
              Create Free Account
            </Link>
          </div>
        </div>
      </section>

      {/* ── Water awareness banner ─────────────────────────────────────────── */}
      <section className="bg-white border-y border-aqua-100">
        <div className="max-w-5xl mx-auto px-4 py-10 text-center">
          <p className="text-xs font-semibold text-aqua-500 uppercase tracking-widest mb-2">
            Why it matters
          </p>
          <h2 className="text-2xl font-bold text-aqua-800 mb-4">
            2.2 billion people lack access to safe drinking water
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
            According to the WHO and UNICEF, contaminated water is linked to diseases such
            as cholera, dysentery, and typhoid. AquaPura aligns with{' '}
            <span className="font-semibold text-aqua-600">UN SDG 6</span> — ensuring
            availability and sustainable management of clean water and sanitation for all.
          </p>
        </div>
      </section>

      {/* ── Parameter info cards ──────────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4 py-14">
        <p className="text-xs font-semibold text-aqua-500 uppercase tracking-widest mb-2 text-center">
          What we measure
        </p>
        <h2 className="text-2xl font-bold text-aqua-800 mb-2 text-center">
          Nine key water-quality parameters
        </h2>
        <p className="text-gray-500 text-sm text-center mb-8">
          These measurements map directly to the fields our AI model was trained on.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {PARAMETERS.map((p) => (
            <div
              key={p.name}
              className="bg-white rounded-xl border border-aqua-100 p-4 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-aqua-800 text-sm">{p.name}</span>
                <span className="text-xs bg-aqua-50 text-aqua-600 font-mono px-2 py-0.5 rounded-full">
                  {p.range}
                </span>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed">{p.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ─────────────────────────────────────────────────── */}
      <section className="bg-white border-y border-aqua-100">
        <div className="max-w-5xl mx-auto px-4 py-14">
          <p className="text-xs font-semibold text-aqua-500 uppercase tracking-widest mb-2 text-center">
            Simple to use
          </p>
          <h2 className="text-2xl font-bold text-aqua-800 mb-10 text-center">
            How it works — three steps
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {STEPS.map((s) => (
              <div key={s.number} className="text-center">
                <div className="w-12 h-12 rounded-full bg-aqua-600 text-white text-xl
                  font-bold flex items-center justify-center mx-auto mb-4">
                  {s.number}
                </div>
                <h3 className="font-semibold text-aqua-800 mb-2">{s.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{s.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Awareness tips ───────────────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4 py-14">
        <p className="text-xs font-semibold text-aqua-500 uppercase tracking-widest mb-2 text-center">
          Stay safe
        </p>
        <h2 className="text-2xl font-bold text-aqua-800 mb-8 text-center">
          Water safety tips
        </h2>
        <ul className="max-w-2xl mx-auto space-y-3">
          {TIPS.map((tip) => (
            <li key={tip} className="flex gap-3 items-start">
              <span className="mt-1 w-4 h-4 rounded-full bg-aqua-100 text-aqua-600
                flex items-center justify-center shrink-0 text-xs font-bold">
                ✓
              </span>
              <span className="text-sm text-gray-600">{tip}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* ── Final CTA ─────────────────────────────────────────────────────── */}
      <section className="bg-gradient-to-r from-aqua-600 to-aqua-700 text-white">
        <div className="max-w-5xl mx-auto px-4 py-16 text-center">
          <h2 className="text-3xl font-bold mb-3">Ready to check your water?</h2>
          <p className="text-aqua-100 mb-8 max-w-xl mx-auto">
            Run a free screening now. Create an account to track your results
            and monitor water quality over time.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/analysis"
              className="inline-block bg-white text-aqua-700 font-bold px-8 py-3
                rounded-xl hover:bg-aqua-50 transition-colors shadow"
            >
              Analyse Water Now
            </Link>
            <Link
              to="/register"
              className="inline-block border-2 border-white text-white font-bold px-8 py-3
                rounded-xl hover:bg-white/10 transition-colors"
            >
              Register for Free
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
