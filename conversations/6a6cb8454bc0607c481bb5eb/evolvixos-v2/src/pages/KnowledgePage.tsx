import { BookOpen, Search, FileText, Code2, BookMarked, Plus } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'

const docs = [
  { title: 'Architecture Overview', category: 'Engineering', icon: FileText, description: 'System architecture, design decisions, and ADRs', updated: '2h ago' },
  { title: 'API Reference', category: 'Developer', icon: Code2, description: 'Full REST API documentation with examples', updated: '5h ago' },
  { title: 'Deployment Guide', category: 'Operations', icon: FileText, description: 'Step-by-step production deployment', updated: '1d ago' },
  { title: 'Security Practices', category: 'Security', icon: FileText, description: 'Security policies, headers, and rate limiting', updated: '3d ago' },
  { title: 'Verdis Whitepaper', category: 'Blockchain', icon: BookMarked, description: 'Complete Verdis blockchain specification', updated: '1w ago' },
  { title: 'Developer Onboarding', category: 'Guide', icon: FileText, description: 'Get started with EvolvixOS development', updated: '2w ago' },
  { title: 'Troubleshooting', category: 'Guide', icon: FileText, description: 'Common issues and runbooks', updated: '2w ago' },
  { title: 'Smart Contract Standards', category: 'Blockchain', icon: Code2, description: 'VRC-20, VRC-721, VRC-1155 token standards', updated: '1mo ago' },
]

export function KnowledgePage() {
  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Knowledge Base</h1>
          <p className="mt-1 text-sm text-text-secondary">Documentation, architecture decisions, and engineering knowledge</p>
        </div>
      </div>

      <Input placeholder="Search documentation..." icon={<Search className="h-4 w-4" />} />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {docs.map(doc => (
          <Card key={doc.title} hover padding="md">
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-bg-hover flex items-center justify-center flex-shrink-0">
                <doc.icon className="h-5 w-5 text-text-secondary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge>{doc.category}</Badge>
                </div>
                <h3 className="text-sm font-semibold text-text-primary">{doc.title}</h3>
                <p className="text-xs text-text-tertiary mt-1 line-clamp-2">{doc.description}</p>
                <p className="text-xs text-text-tertiary mt-2">Updated {doc.updated}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
