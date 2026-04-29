import { useState } from 'react'
import ChatInterface from './ChatInterface'
import FileUpload from './FileUpload'
import './App.css'

function App() {
  const [docReady, setDocReady] = useState(false)

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8 text-slate-950">
      <div className="mx-auto flex w-full max-w-[800px] flex-col gap-6">
        <header className="text-center">
          <h1 className="text-4xl font-bold tracking-normal text-slate-950">
            DocuMind
          </h1>
          <p className="mt-2 text-base text-slate-600">
            AI-powered document Q&amp;A
          </p>
        </header>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          {!docReady ? (
            <div className="flex justify-center">
              <FileUpload onSuccess={() => setDocReady(true)} />
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setDocReady(false)}
                  className="text-sm font-medium text-blue-600 transition hover:text-blue-800"
                >
                  Upload new document
                </button>
              </div>
              <ChatInterface />
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default App
