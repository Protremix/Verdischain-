import { useState, useEffect } from 'react'
import { projects, type Project, type ProjectStats } from '@/lib/api'
import { FolderGit2, Activity, AlertCircle, Globe, Github, ArrowUpRight, Server } from 'lucide-react'

export function ProjectsPage() {
  const [projectList, setProjectList] = useState<Project[]>([])
  const [stats, setStats] = useState<ProjectStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.allSettled([projects.list(), projects.stats()])
      .then(([listR, statsR]) => {
        if (listR.status === 'fulfilled') setProjectList(listR.value)
        else setError('Failed to load projects')
        if (statsR.status === 'fulfilled') setStats(statsR.value)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>Projects</h1>
        <p className='text-sm text-text-secondary mt-1'>Manage and monitor all your engineering projects</p>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4' /> {error}
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className='grid grid-cols-2 sm:grid-cols-4 gap-4'>
          <div className='rounded-xl border border-border bg-bg-surface p-4'>
            <FolderGit2 className='h-5 w-5 text-brand mb-2' />
            <p className='text-2xl font-bold text-text-primary'>{stats.total_projects}</p>
            <p className='text-xs text-text-tertiary'>Total Projects</p>
          </div>
          <div className='rounded-xl border border-border bg-bg-surface p-4'>
            <Activity className='h-5 w-5 text-emerald-400 mb-2' />
            <p className='text-2xl font-bold text-text-primary'>{stats.active}</p>
            <p className='text-xs text-text-tertiary'>Active</p>
          </div>
          <div className='rounded-xl border border-border bg-bg-surface p-4'>
            <Server className='h-5 w-5 text-amber-400 mb-2' />
            <p className='text-2xl font-bold text-text-primary'>{stats.paused}</p>
            <p className='text-xs text-text-tertiary'>Paused</p>
          </div>
          <div className='rounded-xl border border-border bg-bg-surface p-4'>
            <FolderGit2 className='h-5 w-5 text-zinc-400 mb-2' />
            <p className='text-2xl font-bold text-text-primary'>{stats.archived}</p>
            <p className='text-xs text-text-tertiary'>Archived</p>
          </div>
        </div>
      )}

      {/* Project cards */}
      {projectList.length === 0 && !error ? (
        <div className='text-center py-12 rounded-xl border border-border bg-bg-surface'>
          <FolderGit2 className='h-8 w-8 text-text-tertiary mx-auto mb-3' />
          <p className='text-sm text-text-tertiary'>No projects yet. Create one to get started.</p>
        </div>
      ) : (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-4'>
          {projectList.map((project) => (
            <div key={project.id} className='rounded-xl border border-border bg-bg-surface p-5'>
              <div className='flex items-start justify-between mb-3'>
                <div>
                  <h3 className='text-sm font-semibold text-text-primary'>{project.name}</h3>
                  <p className='text-xs text-text-tertiary mt-0.5'>{project.description}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${project.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-500/10 text-zinc-400'}`}>
                  {project.status}
                </span>
              </div>

              <div className='flex items-center gap-3 text-xs text-text-tertiary mb-3'>
                <span className='flex items-center gap-1 capitalize'>
                  <FolderGit2 className='h-3.5 w-3.5' /> {project.type}
                </span>
                {project.domain && (
                  <a href={`https://${project.domain}`} target='_blank' rel='noopener noreferrer' className='flex items-center gap-1 hover:text-text-secondary transition-colors'>
                    <Globe className='h-3.5 w-3.5' /> {project.domain}
                    <ArrowUpRight className='h-3 w-3' />
                  </a>
                )}
                {project.repository && (
                  <a href={project.repository} target='_blank' rel='noopener noreferrer' className='flex items-center gap-1 hover:text-text-secondary transition-colors'>
                    <Github className='h-3.5 w-3.5' /> Repo
                    <ArrowUpRight className='h-3 w-3' />
                  </a>
                )}
              </div>

              {project.config && Object.keys(project.config).length > 0 && (
                <div className='flex flex-wrap gap-1.5 mb-3'>
                  {Object.entries(project.config).slice(0, 5).map(([key, value]) => (
                    <span key={key} className='text-xs px-2 py-0.5 rounded bg-bg-base text-text-tertiary border border-border'>
                      {key.replace(/_/g, ' ')}: {String(value).slice(0, 20)}
                    </span>
                  ))}
                </div>
              )}

              <div className='flex flex-wrap gap-1.5'>
                {project.tags?.map((tag) => (
                  <span key={tag} className='text-xs px-2 py-0.5 rounded bg-brand/5 text-brand/70 border border-brand/10'>{tag}</span>
                ))}
              </div>

              <div className='flex items-center justify-between mt-3 pt-3 border-t border-border/50'>
                <span className='flex items-center gap-1.5 text-xs text-text-tertiary'>
                  <span className={`h-2 w-2 rounded-full ${project.health_status === 'healthy' ? 'bg-emerald-500' : project.health_status === 'degraded' ? 'bg-amber-500' : 'bg-zinc-500'}`} />
                  {project.health_status || 'unknown'}
                </span>
                <span className='text-xs text-text-tertiary'>Created {new Date(project.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
