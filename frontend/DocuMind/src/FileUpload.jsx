import { useRef, useState } from 'react'
import axios from 'axios'
import API_BASE_URL from './apiConfig'

function FileUpload({ onSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')
  const fileInputRef = useRef(null)

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) {
      return
    }

    if (
      selectedFile.type !== 'application/pdf' &&
      !selectedFile.name.toLowerCase().endsWith('.pdf')
    ) {
      setFile(null)
      setStatus('error')
      setMessage('Please select a PDF file.')
      return
    }

    setFile(selectedFile)
    setStatus('idle')
    setMessage('')
  }

  const handleFileChange = (event) => {
    validateAndSetFile(event.target.files?.[0])
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const handleDrop = (event) => {
    event.preventDefault()
    validateAndSetFile(event.dataTransfer.files?.[0])
  }

  const handleUpload = async () => {
    if (!file) {
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setStatus('idle')
    setMessage('')

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setStatus('success')
      setMessage('Document ready to query!')
      onSuccess?.()
    } catch (error) {
      setStatus('error')
      setMessage(
        error.response?.data?.detail ||
          error.message ||
          'Failed to upload document.',
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="w-full max-w-xl">
      <div
        role="button"
        tabIndex={0}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            fileInputRef.current?.click()
          }
        }}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className="flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-white px-6 py-8 text-center transition hover:border-blue-500 hover:bg-blue-50"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileChange}
          className="hidden"
        />

        <p className="text-base font-semibold text-slate-900">
          Drop your PDF here
        </p>
        <p className="mt-2 text-sm text-slate-600">
          or click to select a document
        </p>

        {file && (
          <p className="mt-4 max-w-full truncate rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-800">
            {file.name}
          </p>
        )}
      </div>

      <button
        type="button"
        onClick={handleUpload}
        disabled={uploading || !file}
        className="mt-4 w-full rounded-md bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-600"
      >
        {uploading ? 'Uploading...' : 'Upload Document'}
      </button>

      {message && (
        <p
          className={`mt-3 rounded-md px-3 py-2 text-sm font-medium ${
            status === 'success'
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {message}
        </p>
      )}
    </div>
  )
}

export default FileUpload
