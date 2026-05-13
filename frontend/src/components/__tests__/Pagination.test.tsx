/**
 * Tests for Pagination component.
 * Actual props: { page, size, total, onPageChange }
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Pagination from '../Pagination'

describe('Pagination', () => {
  it('renders showing X-Y of Z text', () => {
    const onPageChange = vi.fn()
    render(<Pagination page={1} size={10} total={50} onPageChange={onPageChange} />)

    expect(screen.getByText(/Mostrando 1-10 de 50/)).toBeInTheDocument()
  })

  it('renders navigation buttons', () => {
    const onPageChange = vi.fn()
    render(<Pagination page={1} size={10} total={50} onPageChange={onPageChange} />)

    expect(screen.getByText('Anterior')).toBeInTheDocument()
    expect(screen.getByText('Siguiente')).toBeInTheDocument()
  })

  it('disables previous button on first page', () => {
    const onPageChange = vi.fn()
    render(<Pagination page={1} size={10} total={50} onPageChange={onPageChange} />)

    const prevButton = screen.getByText('Anterior')
    expect(prevButton).toBeDisabled()
  })

  it('disables next button on last page', () => {
    const onPageChange = vi.fn()
    render(<Pagination page={5} size={10} total={50} onPageChange={onPageChange} />)

    const nextButton = screen.getByText('Siguiente')
    expect(nextButton).toBeDisabled()
  })

  it('returns null when totalPages <= 1', () => {
    const onPageChange = vi.fn()
    const { container } = render(<Pagination page={1} size={10} total={5} onPageChange={onPageChange} />)
    expect(container.innerHTML).toBe('')
  })

  it('calls onPageChange when clicking next', () => {
    const onPageChange = vi.fn()
    render(<Pagination page={2} size={10} total={50} onPageChange={onPageChange} />)

    fireEvent.click(screen.getByText('Siguiente'))
    expect(onPageChange).toHaveBeenCalledWith(3)
  })

  it('calls onPageChange when clicking previous', () => {
    const onPageChange = vi.fn()
    render(<Pagination page={3} size={10} total={50} onPageChange={onPageChange} />)

    fireEvent.click(screen.getByText('Anterior'))
    expect(onPageChange).toHaveBeenCalledWith(2)
  })
})
