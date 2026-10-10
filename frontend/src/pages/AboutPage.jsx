/**
 * AboutPage
 *
 * Describes AquaPura's mission, the problem it addresses, how the platform
 * works accurately, how to register, and the trust / limitations notice.
 */

import { Link } from 'react-router-dom'

const PLATFORM_STEPS = [
  {
    title: 'Water sample measurements',
    body:
      'You provide nine physico-chemical measurements — pH, hardness, total dissolved solids, chloramines, sulfate, conductivity, organic carbon, trihalomethanes, and turbidity.',
  },
  {
    title: 'Random Forest classifier',
    body:
      'A Random Forest model (100 trees) trained on the publicly available Kaggle Water Potability dataset (3,276 labelled samples) processes your inputs and outputs a binary potability label with a probability score.',
  },
  {
    title: 'Preliminary result',
    body:
      'You receive a "Potable" or "Not Potable" classification and the model\'s confidence percentage. This is a screening aid, not a certified safety assessment.',
  },
  {
    title: 'Saved history (registered users)',
    body:
      'Registered and logged-in users can save each analysis automatically. The Dashboard displays a full list of past submissions so you can track changes over time.',
  },
]

const REGISTER_STEPS = [
  'Click "Register" in the navigation bar.',
  'Enter your full name, email address, and a password (minimum 8 characters).',
  'Submit the form — your account is created immediately.',
  'Log in with your email and password.',
  'Run an analysis — it will be saved to your Dashboard automatically.',
]

export default function AboutPage() {
  return (
    <div className="bg-aqua-50">

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="bg-gradient-to-b from-aqua-700 to-aqua-600 text-white">
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <h1 className="text-4xl font-extrabold mb-4">About AquaPura</h1>
          <p className="text-aqua-100 text-lg max-w-2xl mx-auto leading-relaxed">
            A student AI/ML project demonstrating how machine learning can support
            access to safe drinking water — aligned with United Nations Sustainable
            Development Goal 6.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 py-14 space-y-14">

        {/* ── Mission ───────────────────────────────────────────────────── */}
        <section>
          <SectionLabel>Our mission</SectionLabel>
          <h2 className="text-2xl font-bold text-aqua-800 mb-4">
            Making water quality information accessible
          </h2>
          <p className="text-gray-600 leading-relaxed">
            AquaPura was built to demonstrate how artificial intelligence and machine
            learning can help surface water-quality information quickly and accessibly.
            We believe that the first step toward safer water is awareness — understanding
            what the measurements from your tap, well, or sensor actually mean.
          </p>
        </section>

        {/* ── Problem ───────────────────────────────────────────────────── */}
        <section className="bg-white rounded-2xl border border-aqua-100 p-8">
          <SectionLabel>The problem</SectionLabel>
          <h2 className="text-2xl font-bold text-aqua-800 mb-4">
            Unsafe water is a global challenge
          </h2>
          <div className="space-y-4 text-gray-600 leading-relaxed">
            <p>
              The WHO estimates that 2.2 billion people currently lack access to safely
              managed drinking water. Waterborne diseases — cholera, typhoid, and
              dysentery — are responsible for hundreds of thousands of deaths annually,
              with the burden falling disproportionately on low-income communities.
            </p>
            <p>
              Access to water testing is often expensive and slow. Laboratory tests take
              days and require trained personnel. AquaPura is not a replacement for those
              tests, but it is a fast, zero-cost screening step that can inform whether
              further professional testing is warranted.
            </p>
          </div>
        </section>

        {/* ── How we help ────────────────────────────────────────────────── */}
        <section>
          <SectionLabel>How we help</SectionLabel>
          <h2 className="text-2xl font-bold text-aqua-800 mb-4">
            Fast preliminary screening
          </h2>
          <p className="text-gray-600 leading-relaxed mb-4">
            AquaPura lets anyone with nine water-quality readings receive an instant
            potability estimate. This is useful for:
          </p>
          <ul className="space-y-2">
            {[
              'Households with private wells who want a quick check before arranging laboratory testing.',
              'Field workers and NGOs assessing water sources in areas without laboratory access.',
              'Students and educators learning about water-quality indicators and machine learning.',
              'Researchers comparing parameter sets across multiple sample sites.',
            ].map((item) => (
              <li key={item} className="flex gap-3 text-gray-600 text-sm">
                <span className="mt-0.5 text-aqua-500 font-bold shrink-0">→</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* ── How the platform works ─────────────────────────────────────── */}
        <section className="bg-white rounded-2xl border border-aqua-100 p-8">
          <SectionLabel>Technical transparency</SectionLabel>
          <h2 className="text-2xl font-bold text-aqua-800 mb-6">
            How the platform works
          </h2>
          <div className="space-y-6">
            {PLATFORM_STEPS.map((s, i) => (
              <div key={s.title} className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-aqua-600 text-white text-sm
                  font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-aqua-800 mb-1">{s.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{s.body}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 bg-aqua-50 rounded-xl p-4 text-xs text-gray-500 leading-relaxed">
            <span className="font-semibold text-gray-600">Model performance — </span>
            Training-set cross-validation ROC-AUC: 0.70. Test-set accuracy: ~65%.
            The training dataset contains 3,276 samples. Labels were not verified
            by any certified water authority. Performance may not generalise to all
            geographic or seasonal water conditions.
          </div>
        </section>

        {/* ── How to register ────────────────────────────────────────────── */}
        <section>
          <SectionLabel>Getting started</SectionLabel>
          <h2 className="text-2xl font-bold text-aqua-800 mb-4">
            How to register and save your analyses
          </h2>
          <ol className="space-y-3">
            {REGISTER_STEPS.map((step, i) => (
              <li key={step} className="flex gap-3 items-start">
                <span className="w-6 h-6 rounded-full bg-aqua-100 text-aqua-700
                  font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <span className="text-sm text-gray-600">{step}</span>
              </li>
            ))}
          </ol>
          <div className="mt-6">
            <Link
              to="/register"
              className="inline-block bg-aqua-600 text-white font-bold px-6 py-2.5
                rounded-xl hover:bg-aqua-700 transition-colors text-sm"
            >
              Create your account
            </Link>
          </div>
        </section>

        {/* ── Trust & limitations ────────────────────────────────────────── */}
        <section className="bg-amber-50 border border-amber-200 rounded-2xl p-8">
          <SectionLabel color="text-amber-600">Important limitations</SectionLabel>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Trust, but verify
          </h2>
          <div className="space-y-3 text-sm text-gray-600 leading-relaxed">
            <p>
              <span className="font-semibold">AquaPura is not a certified water testing laboratory.</span>{' '}
              Results are generated by a machine-learning model and are indicative only.
              They have not been validated against real-world water sources by any
              regulatory or public-health authority.
            </p>
            <p>
              <span className="font-semibold">Do not make health or safety decisions solely on the basis of these results.</span>{' '}
              If you have concerns about the safety of your water supply, contact your
              local water utility, public health department, or an accredited laboratory.
            </p>
            <p>
              <span className="font-semibold">The model has known limitations:</span> it was
              trained on one dataset with unverified labels, it does not account for
              biological contaminants (bacteria, viruses), heavy metals, or radiological
              hazards, and its accuracy is approximately 65% on held-out data.
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}

function SectionLabel({ children, color = 'text-aqua-500' }) {
  return (
    <p className={`text-xs font-semibold ${color} uppercase tracking-widest mb-2`}>
      {children}
    </p>
  )
}
