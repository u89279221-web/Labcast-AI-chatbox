import { useEffect, useState } from 'react'

type EventCallback = (payload: any) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private subscribers: Map<string, Set<EventCallback>> = new Map()
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private baseReconnectDelay = 1000
  private isConnected = false
  private connectionListeners: Set<(connected: boolean) => void> = new Set()

  public connect(token: string) {
    if (this.ws?.readyState === WebSocket.OPEN) return

    this.token = token
    const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('http', 'ws') || 'ws://localhost:8000'
    const wsUrl = `${baseUrl}/ws/events?token=${token}`

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.isConnected = true
      this.notifyConnectionListeners(true)
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.topic && data.payload) {
          this.notifySubscribers(data.topic, data.payload)
        }
      } catch (error) {
        console.error('Failed to parse WS message:', error)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.isConnected = false
      this.notifyConnectionListeners(false)
      this.scheduleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  public disconnect() {
    if (this.ws) {
      this.ws.onclose = null // Prevent reconnect loop
      this.ws.close()
      this.ws = null
      this.isConnected = false
      this.notifyConnectionListeners(false)
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts || !this.token) {
      console.log('Max reconnect attempts reached or no token available')
      return
    }

    const delay = this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts)
    this.reconnectAttempts++
    
    console.log(`Reconnecting in ${delay}ms... (Attempt ${this.reconnectAttempts})`)
    setTimeout(() => {
      if (this.token) {
        this.connect(this.token)
      }
    }, delay)
  }

  public subscribe(topicPattern: string, callback: EventCallback) {
    if (!this.subscribers.has(topicPattern)) {
      this.subscribers.set(topicPattern, new Set())
    }
    this.subscribers.get(topicPattern)!.add(callback)

    return () => {
      const callbacks = this.subscribers.get(topicPattern)
      if (callbacks) {
        callbacks.delete(callback)
        if (callbacks.size === 0) {
          this.subscribers.delete(topicPattern)
        }
      }
    }
  }

  private notifySubscribers(topic: string, payload: any) {
    // Simple wildcard matching: labcast/machine/+/emergency matches labcast/machine/123/emergency
    this.subscribers.forEach((callbacks, pattern) => {
      const regexPattern = pattern.replace(/\+/g, '[^/]+').replace(/#/g, '.*')
      const regex = new RegExp(`^${regexPattern}$`)
      
      if (regex.test(topic)) {
        callbacks.forEach(callback => callback(payload))
      }
    })
  }

  public onConnectionChange(callback: (connected: boolean) => void) {
    this.connectionListeners.add(callback)
    callback(this.isConnected)
    
    return () => {
      this.connectionListeners.delete(callback)
    }
  }

  private notifyConnectionListeners(connected: boolean) {
    this.connectionListeners.forEach(callback => callback(connected))
  }
  
  public getIsConnected() {
    return this.isConnected
  }
}

export const wsClient = new WebSocketClient()

// React Hook
export function useLiveEvents<T = any>(topicPattern: string, callback: (payload: T) => void) {
  useEffect(() => {
    const unsubscribe = wsClient.subscribe(topicPattern, callback)
    return () => unsubscribe()
  }, [topicPattern, callback])
}

// React Hook for connection status
export function useWsStatus() {
  const [isConnected, setIsConnected] = useState(wsClient.getIsConnected())

  useEffect(() => {
    return wsClient.onConnectionChange(setIsConnected)
  }, [])

  return isConnected
}
