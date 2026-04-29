import { useEffect, useRef, useState } from 'react'
import axios from 'axios'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [openSources, setOpenSources] = useState({})
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const toggleSources = (messageIndex) => {
    setOpenSources((current) => ({
      ...current,
      [messageIndex]: !current[messageIndex],
    }))
  }

  const handleSend = async () => {
    const question = input.trim()

    if (!question || loading) {
      return
    }

    setMessages((current) => [
      ...current,
      { role: 'user', content: question },
    ])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/query', {
        question,
      })

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: response.data.answer,
          sources: response.data.sources || [],
        },
      ])
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content:
            error.response?.data?.detail ||
            error.message ||
            'Failed to get an answer.',
          sources: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[32rem] w-full max-w-3xl flex-col overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((message, index) => {
          const isUser = message.role === 'user'
          const hasSources = !isUser && message.sources && message.sources.length > 0

          return (
            <div
              key={`${message.role}-${index}`}
              className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 text-sm leading-6 ${
                  isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>

                {hasSources && (
                  <div className="mt-3 border-t border-slate-200 pt-3">
                    <button
                      type="button"
                      onClick={() => toggleSources(index)}
                      className="text-xs font-semibold text-slate-700 hover:text-slate-950"
                    >
                      {openSources[index] ? 'Hide Sources' : 'Show Sources'}
                    </button>

                    {openSources[index] && (
                      <div className="mt-2 space-y-2">
                        {message.sources.map((source, sourceIndex) => (
                          <p
                            key={`${index}-source-${sourceIndex}`}
                            className="rounded-md bg-white px-3 py-2 text-xs leading-5 text-slate-700"
                          >
                            {source}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-lg bg-slate-100 px-4 py-3 text-sm text-slate-700">
              Thinking
              <span className="ml-1 inline-flex w-6 justify-between align-middle">
                <span className="animate-bounce">.</span>
                <span className="animate-bounce [animation-delay:150ms]">.</span>
                <span className="animate-bounce [animation-delay:300ms]">.</span>
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-slate-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Ask a question about your document"
            className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100 disabled:text-slate-500"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-600"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
