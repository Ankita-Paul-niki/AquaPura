/**
 * DashboardPage
 *
 * Welcome message, account info, analysis history list, and logout button.
 * Only accessible to authenticated users (protected by ProtectedRoute in App.jsx).
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { fetchAnalyses } from '../services/api'

export default function DashboardPage() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  const [analyses, setAnalyses] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [fetchErr, setFetchErr] = useState(null)

  useEffect(() => {
    if (!token) return
    fetchAnalyses(token)
      .then(setAnalyses)
      .catch((err) => setFetchErr(err.message))
      .finally(() => setLoading(false))
  }, [token])

  const handleLogout = () => {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">

      {/* Welcome */}
      <div className="flex items-start justify-between flex-wrap gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-aqua-800">
            Welcome, {user?.full_name?.split(' ')[0] ?? 'there'} 👋
          </h1>
          <p className="text-sm text-gray-500 mt-1">{user?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="text-sm font-medium text-red-500 hover:text-red-700 transition-colors
            border border-red-200 rounded-lg px-4 py-2 hover:bg-red-50"
        >
          Logout
        </button>
      </div>

      {/* Account info card */}
      <div className="bg-white rounded-2xl border border-aqua-100 p-6 mb-8 shadow-sm">
        <h2 className="font-semibold text-aqua-800 mb-3">Account</h2>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">Full name</dt>
            <dd className="font-medium text-gray-800">{user?.full_name}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Email</dt>
            <dd className="font-medium text-gray-800">{user?.email}</dd>
          </div>
        </dl>
      </div>

      {/* Analysis history */}
      <div className="bg-white rounded-2xl border border-aqua-100 shadow-sm">
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-aqua-50">
          <h2 className="font-semibold text-aqua-800">
            Analysis History
            {!loading && (
              <span className="ml-2 text-xs font-normal text-gray-400">
                ({analyses.length} {analyses.length === 1 ? 'record' : 'records'})
              </span>
            )}
          </h2>
          <Link
            to="/analysis"
            className="text-sm font-medium text-aqua-600 hover:underline"
          >
            New analysis →
          </Link>
        </div>

        <div className="p-6">
          {loading && (
            <p className="text-sm text-gray-400 text-center py-4">Loading history…</p>
          )}
          {fetchErr && (
            <p className="text-sm text-red-500 text-center py-4">{fetchErr}</p>
          )}
          {!loading && !fetchErr && analyses.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 text-sm">No analyses saved yet.</p>
              <Link
                to="/analysis"
                className="mt-3 inline-block text-sm font-medium text-aqua-600 hover:underline"
              >
                Run your first analysis
              </Link>
            </div>
          )}
          {!loading && analyses.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="text-xs text-gray-400 uppercase border-b border-gray-100">
                    <th className="pb-2 pr-4">Date</th>
                    <th className="pb-2 pr-4">Result</th>
                    <th className="pb-2 pr-4">Confidence</th>
                    <th className="pb-2 pr-4">pH</th>
                    <th className="pb-2">Turbidity</th>
                  </tr>
                </thead>
                <tbody>
                  {analyses.map((a) => (
                    <tr key={a.id} className="border-b border-gray-50 last:border-0">
                      <td className="py-2.5 pr-4 text-gray-500 whitespace-nowrap">
                        {new Date(a.timestamp).toLocaleDateString()}
                      </td>
                      <td className="py-2.5 pr-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full
                            text-xs font-semibold ${
                              a.potable_label === 1
                                ? 'bg-emerald-50 text-emerald-700'
                                : 'bg-red-50 text-red-700'
                            }`}
                        >
                          {a.potable_label === 1 ? 'Potable' : 'Not Potable'}
                        </span>
                      </td>
                      <td className="py-2.5 pr-4 text-gray-700">
                        {a.probability_potable != null
                          ? `${(a.probability_potable * 100).toFixed(1)}%`
                          : '—'}
                      </td>
                      <td className="py-2.5 pr-4 text-gray-700">
                        {a.ph?.toFixed(2) ?? '—'}
                      </td>
                      <td className="py-2.5 text-gray-700">
                        {a.turbidity?.toFixed(2) ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
