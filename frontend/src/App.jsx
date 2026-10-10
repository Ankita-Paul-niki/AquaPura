/**
 * AquaPura — Root App component
 *
 * Wires up BrowserRouter, the AuthProvider, the shared Navbar/Footer,
 * and the per-page route table.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { AuthProvider } from './contexts/AuthContext'
import { useAuth }      from './hooks/useAuth'
import Navbar           from './components/Navbar'
import { ChatWidget }   from './components/ChatWidget'

import HomePage      from './pages/HomePage'
import AnalysisPage  from './pages/AnalysisPage'
import AboutPage     from './pages/AboutPage'
import LoginPage     from './pages/LoginPage'
import RegisterPage  from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'

/** Route that requires authentication; redirects to /login otherwise. */
function ProtectedRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

function AppShell() {
  return (
    <div className="min-h-screen bg-aqua-50 flex flex-col">
      <Navbar />

      <div className="flex-1">
        <Routes>
          <Route path="/"          element={<HomePage />} />
          <Route path="/analysis"  element={<AnalysisPage />} />
          <Route path="/about"     element={<AboutPage />} />
          <Route path="/login"     element={<LoginPage />} />
          <Route path="/register"  element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      {/* Footer */}
      <footer className="border-t border-aqua-100 bg-white mt-12">
        <div className="max-w-5xl mx-auto px-4 py-4 text-center text-xs text-gray-400">
          AquaPura — preliminary screening only. Not a substitute for
          accredited laboratory water-quality testing.
        </div>
      </footer>

      {/* AI Chatbot — available on all pages */}
      <ChatWidgetWrapper />
    </div>
  )
}

/** Wraps ChatWidget so it can read the current prediction result from context if needed. */
function ChatWidgetWrapper() {
  // ChatWidget currently accepts predictionResult as a prop.
  // In the multi-page layout we pass null; the chatbot still works for general questions.
  // Phase F wires the actual result through context if needed.
  return <ChatWidget predictionResult={null} />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </BrowserRouter>
  )
}
