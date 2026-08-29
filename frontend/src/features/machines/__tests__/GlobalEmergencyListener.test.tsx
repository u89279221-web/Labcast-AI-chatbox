import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { GlobalEmergencyListener } from '../GlobalEmergencyListener'
import * as wsClient from '@/lib/ws-client'
import * as toastHook from '@/hooks/use-toast'

vi.mock('@/lib/ws-client', () => ({
  useLiveEvents: vi.fn(),
  useWsStatus: vi.fn().mockReturnValue(true),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: vi.fn(),
}))

describe('GlobalEmergencyListener', () => {
  let mockToast: any

  beforeEach(() => {
    mockToast = vi.fn()
    vi.mocked(toastHook.useToast).mockReturnValue({
      toast: mockToast,
      dismiss: vi.fn(),
      toasts: []
    })
    vi.clearAllMocks()
  })

  it('shows a destructive toast when an emergency event is received', () => {
    // We mock useLiveEvents to instantly trigger its callback when rendered
    vi.mocked(wsClient.useLiveEvents).mockImplementation((topic, callback) => {
      if (topic === 'labcast/machine/+/emergency') {
        callback({ machine_id: 'TEST-123', emergency: true })
      }
    })

    render(<GlobalEmergencyListener />)

    expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({
      title: '⚠️ EMERGENCY TRIGGERED',
      variant: 'destructive',
    }))
  })

  it('shows a cleared toast when emergency is lifted', () => {
    vi.mocked(wsClient.useLiveEvents).mockImplementation((topic, callback) => {
      if (topic === 'labcast/machine/+/emergency') {
        callback({ machine_id: 'TEST-123', emergency: false })
      }
    })

    render(<GlobalEmergencyListener />)

    expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({
      title: 'Emergency Cleared',
    }))
  })
})
