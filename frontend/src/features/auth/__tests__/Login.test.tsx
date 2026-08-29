import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Login } from '../Login'
import { BrowserRouter } from 'react-router-dom'
import * as useAuthModule from '../useAuth'

// Mock the useAuth hook
vi.mock('../useAuth', () => ({
  useAuth: vi.fn(),
}))

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form properly', () => {
    vi.mocked(useAuthModule.useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      isLoggingIn: false,
      logout: vi.fn(),
    })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    expect(screen.getByPlaceholderText('m@example.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('calls login on submit', () => {
    const mockLogin = vi.fn()
    vi.mocked(useAuthModule.useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: mockLogin,
      isLoggingIn: false,
      logout: vi.fn(),
    })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const emailInput = screen.getByPlaceholderText('m@example.com')
    const passwordInput = screen.getByLabelText(/password/i)
    const button = screen.getByRole('button', { name: /login/i })

    fireEvent.change(emailInput, { target: { value: 'admin@test.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(button)

    expect(mockLogin).toHaveBeenCalledWith({
      email: 'admin@test.com',
      password: 'password123',
    })
  })

  it('disables button when logging in', () => {
    vi.mocked(useAuthModule.useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      isLoggingIn: true,
      logout: vi.fn(),
    })

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )

    const button = screen.getByRole('button', { name: /logging in/i })
    expect(button).toBeDisabled()
  })
})
