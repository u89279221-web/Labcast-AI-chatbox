import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RoleGate } from '../RoleGate'
import { useAuthStore } from '../store'

describe('RoleGate Component', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, accessToken: null })
  })

  it('renders children if user role matches allowed roles', () => {
    useAuthStore.setState({
      user: { id: '1', email: 'admin@test.com', role: 'admin' },
      accessToken: 'token',
    })

    render(
      <RoleGate allowedRoles={['admin']}>
        <div data-testid="protected-content">Secret Content</div>
      </RoleGate>
    )

    expect(screen.getByTestId('protected-content')).toBeInTheDocument()
  })

  it('hides children if user role does not match allowed roles', () => {
    useAuthStore.setState({
      user: { id: '2', email: 'student@test.com', role: 'student' },
      accessToken: 'token',
    })

    render(
      <RoleGate allowedRoles={['admin', 'faculty']}>
        <div data-testid="protected-content">Secret Content</div>
      </RoleGate>
    )

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
  })

  it('hides children if user is not authenticated', () => {
    render(
      <RoleGate allowedRoles={['admin']}>
        <div data-testid="protected-content">Secret Content</div>
      </RoleGate>
    )

    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
  })
})
