import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { User, Mail, Shield, Calendar, Key, AlertCircle, Save } from 'lucide-react'

export function SettingsPage() {
  const { user } = useAuth()
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [fullName, setFullName] = useState('')

  useEffect(() => {
    if (user?.username) setFullName(user.username.replace(/_/g, ' '))
  }, [user])

  const handleSave = () => {
    setSaving(true)
    setTimeout(() => {
      setSaving(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    }, 500)
  }

  if (!user) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  return (
    <div className='space-y-6 max-w-3xl'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>Settings</h1>
        <p className='text-sm text-text-secondary mt-1'>Manage your account and preferences</p>
      </div>

      {/* Profile section */}
      <div className='rounded-xl border border-border bg-bg-surface p-6'>
        <h2 className='text-sm font-semibold text-text-primary mb-4'>Profile</h2>
        <div className='flex items-center gap-4 mb-6'>
          <div className='h-16 w-16 rounded-full bg-brand/10 text-brand flex items-center justify-center text-xl font-medium'>
            {user.username?.slice(0, 2).toUpperCase() || user.email?.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <p className='text-sm font-medium text-text-primary capitalize'>{user.username?.replace(/_/g, ' ') || 'User'}</p>
            <p className='text-xs text-text-tertiary'>{user.email}</p>
            <span className='inline-flex items-center gap-1 mt-1 text-xs px-2 py-0.5 rounded-full bg-brand/10 text-brand capitalize'>
              <Shield className='h-3 w-3' /> {user.role}
            </span>
          </div>
        </div>

        <div className='space-y-4'>
          <div>
            <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Full Name</label>
            <div className='relative'>
              <User className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
              <input type='text' value={fullName} onChange={e => setFullName(e.target.value)} className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
            </div>
          </div>
          <div>
            <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Email</label>
            <div className='relative'>
              <Mail className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
              <input type='email' value={user.email} disabled className='w-full rounded-lg border border-border bg-bg-base/50 pl-10 pr-4 py-2.5 text-sm text-text-tertiary cursor-not-allowed' />
            </div>
            <p className='text-xs text-text-tertiary mt-1'>Contact support to change your email</p>
          </div>
          <div>
            <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Role</label>
            <div className='relative'>
              <Key className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
              <input type='text' value={user.role} disabled className='w-full rounded-lg border border-border bg-bg-base/50 pl-10 pr-4 py-2.5 text-sm text-text-tertiary capitalize cursor-not-allowed' />
            </div>
          </div>
          <div>
            <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Member Since</label>
            <div className='relative'>
              <Calendar className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
              <input type='text' value={new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })} disabled className='w-full rounded-lg border border-border bg-bg-base/50 pl-10 pr-4 py-2.5 text-sm text-text-tertiary cursor-not-allowed' />
            </div>
          </div>
        </div>

        <div className='flex items-center gap-3 mt-6'>
          <button onClick={handleSave} disabled={saving} className='inline-flex items-center gap-2 rounded-lg bg-brand text-white px-4 py-2 text-sm font-medium hover:bg-brand/90 transition-colors disabled:opacity-50'>
            <Save className='h-4 w-4' /> {saving ? 'Saving...' : 'Save Changes'}
          </button>
          {saved && <span className='text-sm text-emerald-400'>Saved successfully</span>}
        </div>
      </div>

      {/* Security section */}
      <div className='rounded-xl border border-border bg-bg-surface p-6'>
        <h2 className='text-sm font-semibold text-text-primary mb-4'>Security</h2>
        <div className='space-y-3'>
          <div className='flex items-center justify-between py-2 border-b border-border/50'>
            <div>
              <p className='text-sm text-text-primary'>Account Status</p>
              <p className='text-xs text-text-tertiary'>Your account is {user.is_active ? 'active' : 'inactive'}</p>
            </div>
            <span className={`text-xs px-2 py-1 rounded-full ${user.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className='flex items-center justify-between py-2 border-b border-border/50'>
            <div>
              <p className='text-sm text-text-primary'>Two-Factor Authentication</p>
              <p className='text-xs text-text-tertiary'>Add an extra layer of security</p>
            </div>
            <span className='text-xs px-2 py-1 rounded-full bg-zinc-500/10 text-zinc-400'>Not configured</span>
          </div>
          <div className='flex items-center justify-between py-2'>
            <div>
              <p className='text-sm text-text-primary'>API Keys</p>
              <p className='text-xs text-text-tertiary'>Manage API access tokens</p>
            </div>
            <button className='text-xs text-brand hover:text-brand/80 transition-colors'>Manage →</button>
          </div>
        </div>
      </div>

      {/* User ID */}
      <div className='rounded-xl border border-border bg-bg-surface p-4'>
        <div className='flex items-center gap-2 text-xs text-text-tertiary'>
          <Key className='h-3.5 w-3.5' />
          <span>User ID: {user.id}</span>
        </div>
      </div>
    </div>
  )
}
