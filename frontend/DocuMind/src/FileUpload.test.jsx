import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'
import FileUpload from './FileUpload'

vi.mock('axios')

describe('FileUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows an error when a non-PDF file is selected', async () => {
    render(<FileUpload />)
    const dropZone = screen.getByRole('button', { name: /drop your pdf here/i })
    const file = new File(['hello'], 'notes.txt', { type: 'text/plain' })

    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file],
      },
    })

    expect(screen.getByText('Please select a PDF file.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Upload Document' })).toBeDisabled()
  })

  it('uploads a PDF and calls onSuccess', async () => {
    const user = userEvent.setup()
    const onSuccess = vi.fn()
    axios.post.mockResolvedValueOnce({ data: { status: 'success' } })

    const { container } = render(<FileUpload onSuccess={onSuccess} />)
    const input = container.querySelector('input[type="file"]')
    const file = new File(['pdf'], 'doc.pdf', { type: 'application/pdf' })

    await user.upload(input, file)
    await user.click(screen.getByRole('button', { name: 'Upload Document' }))

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
        }),
      )
    })
    expect(await screen.findByText('Document ready to query!')).toBeInTheDocument()
    expect(onSuccess).toHaveBeenCalledTimes(1)
  })
})
