import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const passwordStrength = (p: string) => {
    if (p.length >= 12 && /[A-Z]/.test(p) && /[0-9]/.test(p) && /[^A-Za-z0-9]/.test(p)) return 'strong'
    if (p.length >= 8) return 'medium'
    return 'weak'
  }
  const strength = passwordStrength(password)
  const strengthColor = strength === 'strong' ? 'text-emerald-400' : strength === 'medium' ? 'text-yellow-400' : 'text-red-400'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (password !== confirm) { setError('Passwords do not match'); return }
    if (password.length < 8) { setError('Password must be at least 8 characters'); return }
    setLoading(true)
    try {
      const resp = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: name, email, password }),
      })
      const data = await resp.json()
      if (!resp.ok) { setError(data.detail || 'Registration failed') }
      else { navigate('/login?registered=true') }
    } catch { setError('Network error. Please try again.') }
    finally { setLoading(false) }
  }

  return (
    <div className='min-h-screen bg-bg-base flex flex-col justify-center px-6'>
      <div className='mx-auto w-full max-w-md'>
        <Link to='/' className='flex items-center justify-center gap-2.5 mb-8'>
          <img src='/evolvixos-logo.png' alt='EvolvixOS' className='h-12 w-auto' />
        </Link>
        <div className='rounded-2xl border border-border bg-bg-surface p-8'>
          <h1 className='text-2xl font-bold text-text-primary text-center'>Create your account</h1>
          <p className='text-sm text-text-secondary text-center mt-2'>Start building with autonomous AI engineers</p>
          {error && (
            <div className='mt-4 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400'>
              <AlertCircle className='h-4 w-4 flex-shrink-0' /> {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className='mt-6 space-y-4'>
            <div>
              <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Full Name</label>
              <div className='relative'>
                <User className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
                <input type='text' required value={name} onChange={e => setName(e.target.value)} placeholder='Rojs Gordons' className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
              </div>
            </div>
            <div>
              <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Email</label>
              <div className='relative'>
                <Mail className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
                <input type='email' required value={email} onChange={e => setEmail(e.target.value)} placeholder='you@company.com' className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
              </div>
            </div>
            <div>
              <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Password</label>
              <div className='relative'>
                <Lock className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
                <input type='password' required value={password} onChange={e => setPassword(e.target.value)} placeholder='At least 8 characters' className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
              </div>
              {password && <p className={`text-xs mt-1 ${strengthColor}`}>Password strength: {strength}</p>}
            </div>
            <div>
              <label className='text-sm font-medium text-text-secondary mb-1.5 block'>Confirm Password</label>
              <div className='relative'>
                <Lock className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary' />
                <input type='password' required value={confirm} onChange={e => setConfirm(e.target.value)} placeholder='Repeat your password' className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
              </div>
              {confirm && password === confirm && <p className='text-xs mt-1 text-emerald-400 flex items-center gap-1'><CheckCircle className='h-3 w-3' /> Passwords match</p>}
            </div>
            <Button type='submit' disabled={loading} className='w-full' size='md'>
              {loading ? 'Creating account...' : 'Create Free Account'}
              {!loading && <ArrowRight className='h-4 w-4 ml-2' />}
            </Button>
          </form>
          <p className='text-center text-xs text-text-tertiary mt-4'>By signing up, you agree to our Terms of Service and Privacy Policy.</p>
          <p className='text-center text-sm text-text-tertiary mt-4'>
            Already have an account?{' '}
            <Link to='/login' className='font-medium text-brand hover:text-brand/80 transition-colors'>Sign in</Link>
          </p>
        </div>
        <Link to='/' className='block text-center text-sm text-text-tertiary mt-6 hover:text-text-secondary transition-colors'>← Back to home</Link>
      </div>
    </div>
  )
}
