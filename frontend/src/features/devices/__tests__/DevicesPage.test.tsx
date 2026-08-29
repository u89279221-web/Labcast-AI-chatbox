import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DevicesPage } from '../DevicesPage'
import * as wsClient from '@/lib/ws-client'

// Mock the API module
vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: [
        {
          id: 'dev-1',
          machine_id: 'mach-1',
          firmware_version: '1.0',
          last_seen: new Date().toISOString(),
          status: 'online',
          config_version: '1.0',
          wifi_signal: -50
        }
      ]
    })
  }
}))

// Mock WS status
vi.mock('@/lib/ws-client', () => ({
  useLiveEvents: vi.fn(),
  useWsStatus: vi.fn(),
}))

describe('DevicesPage', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })
    vi.clearAllMocks()
  })

  it('renders Live WebSocket status when connected', async () => {
    vi.mocked(wsClient.useWsStatus).mockReturnValue(true)

    render(
      <QueryClientProvider client={queryClient}>
        <DevicesPage />
      </QueryClientProvider>
    )

    expect(await screen.findByText(/Live WebSocket/i)).toBeInTheDocument()
  })

  it('falls back to Polling (REST) when websocket is disconnected', async () => {
    vi.mocked(wsClient.useWsStatus).mockReturnValue(false)

    render(
      <QueryClientProvider client={queryClient}>
        <DevicesPage />
      </QueryClientProvider>
    )

    expect(await screen.findByText(/Polling \(REST\)/i)).toBeInTheDocument()
  })
})
