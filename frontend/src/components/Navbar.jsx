/**
 * Navbar
 *
 * Top navigation bar with responsive hamburger menu for mobile.
 * Shows Login / Register when unauthenticated.
 * Shows Dashboard / Logout when authenticated.
 */

import { useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Navbar() {
  const { user, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)

  const navLinkClass = ({ isActive }) =>
    `text-sm font-medium transition-colors ${
      isActive
        ? 'text-aqua-600 border-b-2 border-aqua-500 pb-0.5'
        : 'text-gray-600 hover:text-aqua-600'
    }`

  return (
    <header className="bg-white border-b border-aqua-100 shadow-sm sticky top-0 z-40">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <span className="text-2xl" aria-hidden="true">💧</span>
          <div>
            <span className="text-lg font-bold text-aqua-700 leading-tight block">
              AquaPura
            </span>
            <span className="text-xs text-aqua-500 hidden sm:block">
              AI-powered water quality assessment
            </span>
          </div>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-6 ml-6" aria-label="Main navigation">
          <NavLink to="/"         className={navLinkClass} end>Home</NavLink>
          <NavLink to="/analysis" className={navLinkClass}>Analysis</NavLink>
          <NavLink to="/about"    className={navLinkClass}>About</NavLink>
        </nav>

        {/* SDG badge */}
        <div className="ml-auto hidden sm:flex">
          <span className="inline-flex items-center gap-1.5 rounded-full
            bg-aqua-100 px-3 py-1 text-xs font-semibold text-aqua-700">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 inline-block" />
            SDG 6: Clean Water
          </span>
        </div>

        {/* Auth buttons (desktop) */}
        <div className="hidden md:flex items-center gap-2 ml-4">
          {user ? (
            <>
              <NavLink to="/dashboard" className={navLinkClass}>
                {user.full_name?.split(' ')[0] ?? 'Dashboard'}
              </NavLink>
              <button
                onClick={logout}
                className="text-sm font-medium text-gray-500 hover:text-red-500 transition-colors"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className="text-sm font-medium text-aqua-600 hover:text-aqua-700 transition-colors"
              >
                Login
              </NavLink>
              <NavLink
                to="/register"
                className="text-sm font-medium bg-aqua-600 text-white px-3 py-1.5
                  rounded-lg hover:bg-aqua-700 transition-colors"
              >
                Register
              </NavLink>
            </>
          )}
        </div>

        {/* Hamburger (mobile) */}
        <button
          className="md:hidden ml-auto p-2 rounded-lg text-gray-500 hover:bg-aqua-50"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
        >
          {menuOpen ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <nav
          className="md:hidden border-t border-aqua-100 bg-white px-4 py-3 flex flex-col gap-3"
          aria-label="Mobile navigation"
        >
          <NavLink to="/"         className={navLinkClass} end   onClick={() => setMenuOpen(false)}>Home</NavLink>
          <NavLink to="/analysis" className={navLinkClass}       onClick={() => setMenuOpen(false)}>Analysis</NavLink>
          <NavLink to="/about"    className={navLinkClass}       onClick={() => setMenuOpen(false)}>About</NavLink>
          <hr className="border-aqua-100" />
          {user ? (
            <>
              <NavLink to="/dashboard" className={navLinkClass} onClick={() => setMenuOpen(false)}>
                Dashboard
              </NavLink>
              <button
                onClick={() => { logout(); setMenuOpen(false) }}
                className="text-sm font-medium text-left text-red-500 hover:text-red-600"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login"    className={navLinkClass} onClick={() => setMenuOpen(false)}>Login</NavLink>
              <NavLink to="/register" className={navLinkClass} onClick={() => setMenuOpen(false)}>Register</NavLink>
            </>
          )}
        </nav>
      )}
    </header>
  )
}
