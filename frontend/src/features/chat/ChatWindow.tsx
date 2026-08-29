import { useState, useRef, useEffect } from 'react'
import { useChatMutation } from './api'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Bot, User, Send, Loader2, BookOpen } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  text: string
  sourceSnippet?: string
}

interface ChatWindowProps {
  machineId: string
  title?: string
  className?: string
}

export function ChatWindow({ machineId, title = 'AI Assistant', className = '' }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      text: `Hello! I'm the AI assistant for machine ${machineId}. How can I help you today?`
    }
  ])
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const chatMutation = useChatMutation(machineId)

  useEffect(() => {
    setMessages([
      {
        id: 'welcome-' + machineId,
        role: 'assistant',
        text: `Hello! I'm the AI assistant for machine ${machineId}. How can I help you today?`
      }
    ])
  }, [machineId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: input.trim()
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')

    chatMutation.mutate(userMsg.text, {
      onSuccess: (data) => {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            text: data.answer,
            sourceSnippet: data.source_snippet
          }
        ])
      },
      onError: () => {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            text: 'Sorry, I encountered an error communicating with the server.'
          }
        ])
      }
    })
  }

  return (
    <Card className={`flex flex-col h-[600px] max-h-screen w-full mx-auto ${className}`}>
      <CardHeader className="border-b shrink-0 bg-muted/30">
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-6 bg-muted/10" ref={scrollRef}>
        {messages.map((msg) => {
          const isFallback = msg.text.includes('[fallback: no LLM configured]')
          
          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-[85%] ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
              }`}
            >
              <div
                className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                  msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                }`}
              >
                {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>
              
              <div className={`space-y-2 ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                <div
                  className={`px-4 py-2 rounded-lg text-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : isFallback 
                        ? 'bg-amber-100 text-amber-900 border border-amber-300 dark:bg-amber-900/30 dark:text-amber-200 dark:border-amber-700/50'
                        : 'bg-card border shadow-sm'
                  }`}
                >
                  {msg.text}
                </div>
                
                {msg.sourceSnippet && msg.sourceSnippet.trim() !== '' && (
                  <div className="bg-muted text-muted-foreground text-xs p-3 rounded-md border w-full mt-1 flex flex-col gap-1">
                    <div className="flex items-center gap-1 font-semibold uppercase tracking-wider text-[10px]">
                      <BookOpen className="h-3 w-3" /> Source Context
                    </div>
                    <div className="italic border-l-2 border-primary/40 pl-2 ml-1">
                      "{msg.sourceSnippet}"
                    </div>
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {chatMutation.isPending && (
          <div className="flex gap-3 max-w-[85%]">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-muted flex items-center justify-center">
              <Bot className="h-4 w-4" />
            </div>
            <div className="px-4 py-2 rounded-lg bg-card border shadow-sm flex items-center h-10">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="p-3 border-t bg-background shrink-0">
        <form
          className="flex w-full items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this machine..."
            className="flex-1"
            disabled={chatMutation.isPending}
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={!input.trim() || chatMutation.isPending}
            className="shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </CardFooter>
    </Card>
  )
}
