import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'
import App from './App'

vi.mock('axios')

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Element.prototype.scrollIntoView = vi.fn()
  })

  it('switches from upload to chat after a successful document upload', async () => {
    const user = userEvent.setup()
    axios.post.mockResolvedValueOnce({ data: { status: 'success' } })

    const { container } = render(<App />)
    const input = container.querySelector('input[type="file"]')
    const file = new File(['pdf'], 'doc.pdf', { type: 'application/pdf' })

    expect(screen.getByText('DocuMind')).toBeInTheDocument()
    expect(screen.getByText('AI-powered document Q&A')).toBeInTheDocument()

    await user.upload(input, file)
    await user.click(screen.getByRole('button', { name: 'Upload Document' }))

    expect(
      await screen.findByPlaceholderText('Ask a question about your document'),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Upload new document' })).toBeInTheDocument()
  })

  it('returns to upload mode when Upload new document is clicked', async () => {
    const user = userEvent.setup()
    axios.post.mockResolvedValueOnce({ data: { status: 'success' } })

    const { container } = render(<App />)
    const input = container.querySelector('input[type="file"]')
    const file = new File(['pdf'], 'doc.pdf', { type: 'application/pdf' })

    await user.upload(input, file)
    await user.click(screen.getByRole('button', { name: 'Upload Document' }))
    await user.click(await screen.findByRole('button', { name: 'Upload new document' }))

    expect(screen.getByText('Drop your PDF here')).toBeInTheDocument()
  })
})
