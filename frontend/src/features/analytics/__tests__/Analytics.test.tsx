import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AnalyticsDashboard } from '../AnalyticsDashboard'
import * as api from '../api'

vi.mock('../api', () => ({
  useAnalyticsSummary: vi.fn(),
  useAuditLogs: vi.fn(),
}))

// Mock recharts because its responsive container and SVG elements can be tricky in JSDOM
vi.mock('recharts', async () => {
  const OriginalModule = await vi.importActual('recharts')
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
    BarChart: () => <div data-testid="bar-chart" />,
    AreaChart: () => <div data-testid="area-chart" />,
  }
})

describe('AnalyticsDashboard', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    vi.clearAllMocks()
  })

  it('renders stats correctly from mocked summary response', async () => {
    const mockSummary = {
      chats_per_machine: {
        'MAC-1': 15,
        'MAC-2': 5,
      },
      total_emergency_activations: 42,
      active_devices: 3
    }

    const mockLogs = [
      {
        id: 'log-1',
        timestamp: '2026-08-10T12:00:00Z',
        user_id: 'admin',
        action: 'emergency_toggle',
        target_id: 'MAC-1',
      }
    ]

    vi.mocked(api.useAnalyticsSummary).mockReturnValue({
      data: mockSummary,
      isLoading: false,
    } as any)

    vi.mocked(api.useAuditLogs).mockReturnValue({
      data: mockLogs,
      isLoading: false,
    } as any)

    render(
      <QueryClientProvider client={queryClient}>
        <AnalyticsDashboard />
      </QueryClientProvider>
    )

    // Check stats cards
    expect(await screen.findByText('42')).toBeInTheDocument() // Emergency activations
    expect(await screen.findByText('3')).toBeInTheDocument() // Active devices
    expect(await screen.findByText('20')).toBeInTheDocument() // Total chats (15 + 5)

    // Check charts rendered
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
    expect(screen.getByTestId('area-chart')).toBeInTheDocument()

    // Check Audit Log table
    expect(screen.getByText('Audit Log')).toBeInTheDocument()
    expect(screen.getByText('emergency_toggle')).toBeInTheDocument()
  })
})
