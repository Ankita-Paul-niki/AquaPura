/**
 * ChatWidget component
 *
 * A collapsible chat panel docked to the bottom-right of the screen.
 * Opens/closes with a floating button.  Passes the latest prediction
 * result to the backend so the assistant can give context-aware replies.
 *
 * Props
 * -----
 * predictionResult  — latest PredictionResponse object, or null
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { sendChatMessage } from '../services/api'

// ── Suggested questions shown when the chat is empty ──────────────────────────
const SUGGESTIONS = [
  'What does my water-quality result mean?',
  'Why was my sample classified as not potable?',
  'What does pH mean?',
  'Which parameters does AquaPura analyse?',
  'What should I do after a not-potable result?',
]

// Render assistant reply text: convert **bold** and newlines to JSX.
function FormattedText({ text }) {
  return (
    <span>
      {text.split('\n').map((line, li) => {
        // Bold: **text**
        const parts = line.split(/(\*\*[^*]+\*\*)/)
        return (
          <span key={li}>
            {li > 0 && <br />}
            {parts.map((part, pi) =>
              part.startsWith('**') && part.endsWith('**') ? (
                <strong key={pi}>{part.slice(2, -2)}</strong>
              ) : (
                part
              ),
            )}
          </span>
        )
      })}
    </span>
  )
}

export function ChatWidget({ predictionResult }) {
  const [open,     setOpen]     = useState(false)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text:
        "Hi! I'm the **AquaPura AI Assistant**. 👋\n\n" +
        'I can explain water-quality parameters and help you understand your assessment results.\n\n' +
        'Try one of the suggested questions below, or type your own.',
    },
  ])
  const [input,    setInput]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState(null)

  const bottomRef  = useRef(null)
  const inputRef   = useRef(null)
  const listRef    = useRef(null)

  // Scroll to latest message whenever messages or open state change
  useEffect(() => {
    if (open && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, open])

  // Focus the input when the panel opens
  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus()
    }
  }, [open])

  const send = useCallback(async (text) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setError(null)
    setMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setInput('')
    setLoading(true)

    try {
      const data = await sendChatMessage(trimmed, predictionResult ?? null)
      setMessages((prev) => [...prev, { role: 'assistant', text: data.reply }])
    } catch (err) {
      setError(err.message ?? 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [loading, predictionResult])

  function handleSubmit(e) {
    e.preventDefault()
    send(input)
  }

  function handleSuggestion(text) {
    send(text)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  function clearChat() {
    setMessages([
      {
        role: 'assistant',
        text:
          "Chat cleared. I'm still here to help! Ask me anything about water quality or your assessment result.",
      },
    ])
    setError(null)
  }

  const showSuggestions = messages.length <= 1

  return (
    <>
      {/* ── Floating toggle button ─────────────────────────────────────────── */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Close AI Assistant' : 'Open AI Assistant'}
        aria-expanded={open}
        className={[
          'fixed bottom-5 right-5 z-50',
          'w-14 h-14 rounded-full shadow-lg',
          'flex items-center justify-center text-2xl',
          'bg-aqua-600 text-white',
          'hover:bg-aqua-700 active:bg-aqua-800',
          'focus:outline-none focus:ring-2 focus:ring-aqua-400 focus:ring-offset-2',
          'transition-all duration-200',
          open ? 'rotate-90' : '',
        ].join(' ')}
      >
        {open ? '✕' : '💬'}
      </button>

      {/* ── Chat panel ────────────────────────────────────────────────────── */}
      {open && (
        <div
          role="dialog"
          aria-label="AquaPura AI Assistant"
          className={[
            'fixed bottom-24 right-5 z-50',
            'w-[calc(100vw-2.5rem)] max-w-sm',
            'bg-white rounded-2xl shadow-2xl border border-aqua-100',
            'flex flex-col',
            'overflow-hidden',
          ].join(' ')}
          style={{ height: '520px' }}
        >
          {/* Header */}
          <div className="bg-aqua-600 text-white px-4 py-3 flex items-center gap-2 shrink-0">
            <span className="text-lg" aria-hidden="true">💧</span>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm leading-tight truncate">AquaPura AI Assistant</p>
              <p className="text-aqua-200 text-xs">Educational water-quality guidance</p>
            </div>
            <button
              onClick={clearChat}
              title="Start a new conversation"
              aria-label="Start a new conversation"
              className="text-aqua-200 hover:text-white text-xs underline underline-offset-2
                focus:outline-none focus:ring-1 focus:ring-white rounded px-1"
            >
              New chat
            </button>
          </div>

          {/* Message list */}
          <div
            ref={listRef}
            className="flex-1 overflow-y-auto px-3 py-3 space-y-3"
            aria-live="polite"
            aria-label="Chat messages"
          >
            {messages.map((msg, i) => (
              <div
                key={i}
                className={[
                  'flex',
                  msg.role === 'user' ? 'justify-end' : 'justify-start',
                ].join(' ')}
              >
                <div
                  className={[
                    'max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed',
                    msg.role === 'user'
                      ? 'bg-aqua-600 text-white rounded-br-sm'
                      : 'bg-aqua-50 text-gray-800 border border-aqua-100 rounded-bl-sm',
                  ].join(' ')}
                >
                  <FormattedText text={msg.text} />
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-aqua-50 border border-aqua-100 rounded-2xl rounded-bl-sm
                  px-3 py-2 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-aqua-400 animate-bounce [animation-delay:0ms]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-aqua-400 animate-bounce [animation-delay:150ms]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-aqua-400 animate-bounce [animation-delay:300ms]" />
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div role="alert" className="text-xs text-red-600 bg-red-50 border border-red-200
                rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Suggested questions (shown while conversation is empty) */}
          {showSuggestions && !loading && (
            <div className="px-3 pb-2 shrink-0">
              <p className="text-xs text-gray-400 mb-1.5 font-medium">Suggested questions</p>
              <div className="flex flex-col gap-1">
                {SUGGESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleSuggestion(q)}
                    className="text-left text-xs text-aqua-700 bg-aqua-50 hover:bg-aqua-100
                      border border-aqua-200 rounded-lg px-2.5 py-1.5
                      focus:outline-none focus:ring-1 focus:ring-aqua-400
                      transition-colors leading-snug"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input bar */}
          <form
            onSubmit={handleSubmit}
            className="border-t border-aqua-100 px-3 py-2 flex gap-2 shrink-0 bg-white"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about water quality…"
              disabled={loading}
              aria-label="Chat message input"
              maxLength={1000}
              className="flex-1 rounded-lg border border-aqua-200 px-3 py-2 text-sm
                bg-white text-gray-800 placeholder-gray-400
                focus:outline-none focus:ring-2 focus:ring-aqua-400 focus:border-aqua-400
                disabled:bg-gray-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              aria-label="Send message"
              className="px-3 py-2 rounded-lg bg-aqua-600 text-white text-sm font-semibold
                hover:bg-aqua-700 active:bg-aqua-800
                focus:outline-none focus:ring-2 focus:ring-aqua-400 focus:ring-offset-1
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors shrink-0"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  )
}
