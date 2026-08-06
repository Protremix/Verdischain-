import { useState } from 'react'
import { FolderGit2, GitBranch, Users, Star, Plus, LayoutGrid, List } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/cn'

const projects = [
  { name: 'Verdis Chain', description: 'Carbon-negative blockchain with DPoS consensus', language: 'Rust', stars: 342, branch: 'main', team: 8, status: 'active', updated: '2h ago' },
  { name: 'EvolvixOS', description: 'AI engineering platform for software systems', language: 'TypeScript', stars: 187, branch: 'main', team: 5, status: 'active', updated: '1h ago' },
  { name: 'Verdiscan', description: 'Block explorer with dark Solscan-style UI', language: 'React', stars: 94, branch: 'develop', team: 3, status: 'active', updated: '5h ago' },
  { name: 'AegisOS', description: 'Security operations platform', language: 'Python', stars: 76, branch: 'main', team: 4, status: 'maintenance', updated: '2d ago' },
  { name: 'Anerium', description: 'Fintech payment platform', language: 'Go', stars: 156, branch: 'main', team: 6, status: 'archived', updated: '1mo ago' },
  { name: 'Verdis Wallet', description: 'Native Android wallet — zero dependencies', language: 'Kotlin', stars: 89, branch: 'main', team: 2, status: 'active', updated: '3h ago' },
]

const langColors: Record<string, string> = {
  Rust: 'bg-orange-500',
  TypeScript: 'bg-blue-500',
  React: 'bg-cyan-500',
  Python: 'bg-yellow-500',
  Go: 'bg-sky-500',
  Kotlin: 'bg-purple-500',
}

export function ProjectsPage() {
  const [view, setView] = useState<'grid' | 'list'>('grid')

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Projects</h1>
          <p className="mt-1 text-sm text-text-secondary">{projects.length} projects · {projects.filter(p => p.status === 'active').length} active</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-lg border border-border bg-bg-surface p-0.5">
            <button
              onClick={() => setView('grid')}
              className={cn('h-8 w-8 flex items-center justify-center rounded-md transition-colors', view === 'grid' ? 'bg-bg-hover text-text-primary' : 'text-text-tertiary')}
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setView('list')}
              className={cn('h-8 w-8 flex items-center justify-center rounded-md transition-colors', view === 'list' ? 'bg-bg-hover text-text-primary' : 'text-text-tertiary')}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
          <Button size="sm" icon={<Plus className="h-4 w-4" />}>New Project</Button>
        </div>
      </div>

      {view === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map(project => (
            <Card key={project.name} hover padding="md">
              <div className="flex items-start gap-3 mb-3">
                <div className="h-10 w-10 rounded-lg bg-bg-hover flex items-center justify-center flex-shrink-0">
                  <FolderGit2 className="h-5 w-5 text-text-secondary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-text-primary truncate">{project.name}</h3>
                  <p className="text-xs text-text-tertiary mt-0.5 line-clamp-2">{project.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 text-xs text-text-tertiary">
                <span className="flex items-center gap-1">
                  <span className={cn('h-2.5 w-2.5 rounded-full', langColors[project.language])} />
                  {project.language}
                </span>
                <span className="flex items-center gap-1"><Star className="h-3 w-3" />{project.stars}</span>
                <span className="flex items-center gap-1"><Users className="h-3 w-3" />{project.team}</span>
                <span className="flex items-center gap-1"><GitBranch className="h-3 w-3" />{project.branch}</span>
              </div>
              <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
                <Badge variant={project.status === 'active' ? 'success' : project.status === 'maintenance' ? 'warning' : 'default'} dot>
                  {project.status}
                </Badge>
                <span className="text-xs text-text-tertiary">{project.updated}</span>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card padding="none" className="overflow-hidden">
          <div className="divide-y divide-border">
            {projects.map(project => (
              <div key={project.name} className="flex items-center gap-4 p-4 hover:bg-bg-hover transition-colors cursor-pointer">
                <div className="h-10 w-10 rounded-lg bg-bg-hover flex items-center justify-center flex-shrink-0">
                  <FolderGit2 className="h-5 w-5 text-text-secondary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-text-primary">{project.name}</h3>
                  <p className="text-xs text-text-tertiary">{project.description}</p>
                </div>
                <div className="hidden sm:flex items-center gap-4 text-xs text-text-tertiary">
                  <span className="flex items-center gap-1"><span className={cn('h-2.5 w-2.5 rounded-full', langColors[project.language])} />{project.language}</span>
                  <span className="flex items-center gap-1"><Star className="h-3 w-3" />{project.stars}</span>
                  <span className="flex items-center gap-1"><Users className="h-3 w-3" />{project.team}</span>
                </div>
                <Badge variant={project.status === 'active' ? 'success' : project.status === 'maintenance' ? 'warning' : 'default'} dot>
                  {project.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
