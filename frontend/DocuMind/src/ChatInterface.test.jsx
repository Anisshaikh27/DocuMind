import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'
import ChatInterface from './ChatInterface'

vi.mock('axios')

describe('ChatInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Element.prototype.scrollIntoView = vi.fn()
  })

  it('sends a question and shows the assistant answer with collapsible sources', async () => {
    const user = userEvent.setup()
    axios.post.mockResolvedValueOnce({
      data: {
        answer: 'This document is for API upload testing.',
        sources: ['DocuMind test document.'],
      },
    })

    render(<ChatInterface />)

    await user.type(
      screen.getByPlaceholderText('Ask a question about your document'),
      'What is this document used for?',
    )
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/query', {
      question: 'What is this document used for?',
    })
    expect(screen.getByText('What is this document used for?')).toBeInTheDocument()
    expect(
      await screen.findByText('This document is for API upload testing.'),
    ).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Show Sources' }))

    expect(screen.getByText('DocuMind test document.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Hide Sources' })).toBeInTheDocument()
  })
})
