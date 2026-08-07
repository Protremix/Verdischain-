import { useState, useEffect } from 'react'
import { knowledge, type KnowledgeEntry, type KnowledgeStats, type DocsDashboard } from '@/lib/api'
import { BookOpen, FileText, HelpCircle, AlertCircle, Search, Tag } from 'lucide-react'

export function KnowledgePage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([])
  const [stats, setStats] = useState<KnowledgeStats | null>(null)
  const [docs, setDocs] = useState<DocsDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState<string | null>(null)

  useEffect(() => {
    Promise.allSettled([knowledge.list(), knowledge.stats(), knowledge.docsDashboard()])
      .then(([listR, statsR, docsR]) => {
        if (listR.status === 'fulfilled') setEntries(listR.value)
        else setError('Failed to load knowledge base')
        if (statsR.status === 'fulfilled') setStats(statsR.value)
        if (docsR.status === 'fulfilled') setDocs(docsR.value)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  const categories = stats ? Object.keys(stats.categories) : []
  const filtered = entries.filter(e => {
    const matchesSearch = !search || e.title.toLowerCase().includes(search.toLowerCase()) || e.content.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = !activeCategory || e.category === activeCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>Knowledge Base</h1>
        <p className='text-sm text-text-secondary mt-1'>Engineering knowledge, documentation, and best practices</p>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4' /> {error}
        </div>
      )}

      {/* Stats */}
      <div className='grid grid-cols-2 sm:grid-cols-4 gap-4'>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <BookOpen className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{stats?.total_entries || 0}</p>
          <p className='text-xs text-text-tertiary'>KB Entries</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <FileText className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{docs?.stats.total_docs || 0}</p>
          <p className='text-xs text-text-tertiary'>Documents</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <HelpCircle className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{docs?.stats.total_faqs || 0}</p>
          <p className='text-xs text-text-tertiary'>FAQs</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <FileText className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{docs?.stats.total_runbooks || 0}</p>
          <p className='text-xs text-text-tertiary'>Runbooks</p>
        </div>
      </div>

      {/* Search + Category filter */}
      <div className='flex flex-col sm:flex-row gap-3'>
        <div className='relative flex-1'>
          <Search className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
          <input type='text' value={search} onChange={e => setSearch(e.target.value)} placeholder='Search knowledge base...' className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
        </div>
        <div className='flex flex-wrap gap-2'>
          <button onClick={() => setActiveCategory(null)} className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${!activeCategory ? 'bg-brand/10 text-brand border-brand/20' : 'border-border text-text-tertiary hover:text-text-secondary'}`}>All</button>
          {categories.map(cat => (
            <button key={cat} onClick={() => setActiveCategory(cat)} className={`text-xs px-3 py-1.5 rounded-lg border capitalize transition-colors ${activeCategory === cat ? 'bg-brand/10 text-brand border-brand/20' : 'border-border text-text-tertiary hover:text-text-secondary'}`}>{cat}</button>
          ))}
        </div>
      </div>

      {/* Knowledge entries */}
      <div className='grid grid-cols-1 lg:grid-cols-2 gap-4'>
        {filtered.map((entry) => (
          <div key={entry.id} className='rounded-xl border border-border bg-bg-surface p-5'>
            <div className='flex items-start justify-between mb-2'>
              <h3 className='text-sm font-semibold text-text-primary'>{entry.title}</h3>
              <span className='text-xs px-2 py-0.5 rounded bg-bg-base text-text-tertiary border border-border capitalize'>{entry.category}</span>
            </div>
            <p className='text-xs text-text-secondary leading-relaxed'>{entry.content}</p>
            <div className='flex items-center gap-2 mt-3 flex-wrap'>
              {entry.tags?.map(tag => (
                <span key={tag} className='flex items-center gap-0.5 text-xs text-text-tertiary'>
                  <Tag className='h-2.5 w-2.5' /> {tag}
                </span>
              ))}
            </div>
            <div className='flex items-center justify-between mt-3 pt-3 border-t border-border/50'>
              <span className='text-xs text-text-tertiary'>Confidence: {(entry.confidence * 100).toFixed(0)}%</span>
              <span className='text-xs text-text-tertiary'>{entry.times_referenced} references</span>
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && !error && (
        <div className='text-center py-12 rounded-xl border border-border bg-bg-surface'>
          <BookOpen className='h-8 w-8 text-text-tertiary mx-auto mb-3' />
          <p className='text-sm text-text-tertiary'>{search ? 'No results found.' : 'No knowledge entries yet.'}</p>
        </div>
      )}

      {/* Recent docs */}
      {docs?.recent_docs && docs.recent_docs.length > 0 && (
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <h2 className='text-sm font-semibold text-text-primary mb-4'>Recent Documentation</h2>
          <div className='space-y-2'>
            {docs.recent_docs.slice(0, 5).map(doc => (
              <div key={doc.id} className='flex items-center justify-between py-2 border-b border-border/50 last:border-0'>
                <div>
                  <p className='text-sm text-text-primary'>{doc.title}</p>
                  <p className='text-xs text-text-tertiary'>{doc.description}</p>
                </div>
                <div className='flex items-center gap-2'>
                  <span className='text-xs text-text-tertiary capitalize'>{doc.category.replace(/_/g, ' ')}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${doc.status === 'published' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-500/10 text-zinc-400'}`}>{doc.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
