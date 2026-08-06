import { useState } from 'react'
import { Bot, Send, Sparkles, Code2, Building2, Shield, Compass, Cpu } from 'lucide-react'
import { cn } from '@/lib/cn'
import { Badge } from '@/components/ui/Badge'

const agents = [
  { id: 'cto', name: 'AI CTO', icon: Cpu, description: 'Architecture & strategy decisions' },
  { id: 'architect', name: 'AI Architect', icon: Building2, description: 'Code review & system design' },
  { id: 'planner', name: 'AI Planner', icon: Compass, description: 'Roadmaps & sprint planning' },
  { id: 'reviewer', name: 'AI Reviewer', icon: Shield, description: 'Security & quality audits' },
  { id: 'developer', name: 'AI Developer', icon: Code2, description: 'Code generation & refactoring' },
]

const mockMessages = [
  { role: 'user' as const, content: 'Review the DPoS consensus implementation. Are there any security concerns?' },
  { role: 'assistant' as const, content: 'I\'ve reviewed the DPoS consensus implementation. Here\'s my analysis:\n\n**Security Assessment: 8.5/10**\n\n✅ Validator set rotation is properly bounded (max 101 slots)\n✅ Stake locking with 7-day unbonding period\n✅ Slashing mechanism for misbehavior (5% penalty)\n⚠️ Validator selection entropy could be improved — consider using a VRF instead of simple stake-weighted selection\n⚠️ No explicit mechanism for chain reorganization protection\n\n**Recommendation:** Implement a VRF-based validator selection to prevent stake concentration attacks. Consider adding a finality gadget (GRANDPA) for improved chain security.\n\nShall I generate the implementation for VRF-based selection?' },
]

export function AIWorkspacePage() {
  const [activeAgent, setActiveAgent] = useState('cto')
  const [messages, setMessages] = useState(mockMessages)
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim()) return
    setMessages([...messages, { role: 'user', content: input }])
    setInput('')
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I\'m analyzing your request. This is a simulated response — the AI agent will provide a detailed analysis once connected to the GPT-4o backend.'
      }])
    }, 1000)
  }

  const currentAgent = agents.find(a => a.id === activeAgent)!

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">AI Workspace</h1>
          <p className="mt-1 text-sm text-text-secondary">Intelligent engineering assistance</p>
        </div>
        <Badge variant="brand" dot>5 agents online</Badge>
      </div>

      <div className="flex-1 flex gap-4 min-h-0">
        <div className="w-64 flex-shrink-0 space-y-1.5 hidden sm:block">
          {agents.map(agent => (
            <button
              key={agent.id}
              onClick={() => setActiveAgent(agent.id)}
              className={cn(
                'w-full flex items-center gap-3 rounded-lg p-3 text-left transition-all',
                activeAgent === agent.id
                  ? 'bg-brand/10 border border-brand/20'
                  : 'border border-transparent hover:bg-bg-hover'
              )}
            >
              <div className={cn(
                'h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0',
                activeAgent === agent.id ? 'bg-brand text-white' : 'bg-bg-hover text-text-secondary'
              )}>
                <agent.icon className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">{agent.name}</p>
                <p className="text-xs text-text-tertiary truncate">{agent.description}</p>
              </div>
            </button>
          ))}
        </div>

        <div className="flex-1 flex flex-col rounded-xl border border-border bg-bg-surface overflow-hidden">
          <div className="flex items-center gap-3 px-4 h-14 border-b border-border">
            <div className="h-8 w-8 rounded-lg bg-brand-gradient flex items-center justify-center">
              <currentAgent.icon className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-text-primary">{currentAgent.name}</p>
              <p className="text-xs text-text-tertiary">{currentAgent.description}</p>
            </div>
            <div className="ml-auto">
              <Badge variant="success" dot>Active</Badge>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={cn('flex gap-3 animate-fade-in-up', msg.role === 'user' && 'flex-row-reverse')}>
                <div className={cn(
                  'h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0',
                  msg.role === 'user'
                    ? 'bg-bg-hover text-text-secondary'
                    : 'bg-brand-gradient text-white'
                )}>
                  {msg.role === 'user' ? <span className="text-xs font-medium">RG</span> : <Sparkles className="h-4 w-4" />}
                </div>
                <div className={cn(
                  'max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed',
                  msg.role === 'user'
                    ? 'bg-brand text-white'
                    : 'bg-bg-hover text-text-primary'
                )}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-border p-3">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
                placeholder={`Message ${currentAgent.name}...`}
                rows={1}
                className="flex-1 resize-none rounded-lg bg-bg-input border border-border px-4 py-2.5 text-sm
                  text-text-primary placeholder:text-text-tertiary
                  focus:outline-none focus:border-brand focus:ring-2 focus:ring-brand/15
                  transition-all max-h-32"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="h-10 w-10 flex items-center justify-center rounded-lg bg-brand text-white
                  hover:bg-brand-hover disabled:opacity-40 disabled:pointer-events-none
                  transition-all active:scale-95 flex-shrink-0"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
