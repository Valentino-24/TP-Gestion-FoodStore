/**
 * Tests for ProductCard component.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import ProductCard from '../ProductCard'

// Mock react-router-dom Link
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    Link: vi.fn().mockImplementation(({ to, children, className }) => (
      <a href={to} className={className}>
        {children}
      </a>
    )),
  }
})

const baseProduct = {
  id: 1,
  nombre: 'Coca-Cola',
  descripcion: 'Refresco de cola 500ml',
  precio: 2.50,
  categoria_id: 1,
  imagen_url: 'http://example.com/coke.jpg',
  activo: true,
  creado_en: '2024-01-01T00:00:00Z',
  actualizado_en: '2024-01-01T00:00:00Z',
}

describe('ProductCard', () => {
  it('renders product name and price', () => {
    render(
      <BrowserRouter>
        <ProductCard product={baseProduct} />
      </BrowserRouter>
    )

    expect(screen.getByText('Coca-Cola')).toBeInTheDocument()
    expect(screen.getByText('$2.50')).toBeInTheDocument()
  })

  it('renders category badge', () => {
    render(
      <BrowserRouter>
        <ProductCard product={baseProduct} />
      </BrowserRouter>
    )

    expect(screen.getByText(/Cat\. 1/)).toBeInTheDocument()
  })

  it('renders image when imagen_url is provided', () => {
    render(
      <BrowserRouter>
        <ProductCard product={baseProduct} />
      </BrowserRouter>
    )

    const img = screen.getByAltText('Coca-Cola')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', 'http://example.com/coke.jpg')
  })
})
