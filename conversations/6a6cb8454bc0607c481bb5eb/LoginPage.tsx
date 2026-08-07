import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowRight, Mail, Lock, AlertCircle, CheckCircle } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/Button'

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const justRegistered = searchParams.get('registered') === 'true'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/app')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='min-h-screen bg-bg-base flex flex-col justify-center px-6'>
      <div className='mx-auto w-full max-w-md'>
        <Link to='/' className='flex items-center justify-center gap-2.5 mb-8'>
          <img src='/evolvixos-logo.png' alt='EvolvixOS' className='h-12 w-auto' />
        </Link>
        <div className='rounded-2xl border border-border bg-bg-surface p-8'>
          <h1 className='text-2xl font-bold text-text-primary text-center'>Welcome back</h1>
          <p className='text-sm text-text-secondary text-center mt-2'>Sign in to your EvolvixOS account</p>
          {justRegistered && (
            <div className='mt-4 flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400'>
              <CheckCircle className='h-4 w-4 flex-shrink-0' /> Account created! Please sign in.
            </div>
          )}
          {error && (
            <div className='mt-4 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400'>
              <AlertCircle className='h-4 w-4 flex-shrink-0' /> {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className='mt-6 space-y-4'>
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
                <input type='password' required value={password} onChange={e => setPassword(e.target.value)} placeholder='••••••••' className='w-full rounded-lg border border-border bg-bg-base pl-10 pr-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-colors' />
              </div>
            </div>
            <Button type='submit' disabled={loading} className='w-full' size='md'>
              {loading ? 'Signing in...' : 'Sign In'}
              {!loading && <ArrowRight className='h-4 w-4 ml-2' />}
            </Button>
          </form>
          <p className='text-center text-sm text-text-tertiary mt-6'>
            Don't have an account?{' '}
            <Link to='/register' className='font-medium text-brand hover:text-brand/80 transition-colors'>Sign up free</Link>
          </p>
        </div>
        <Link to='/' className='block text-center text-sm text-text-tertiary mt-6 hover:text-text-secondary transition-colors'>← Back to home</Link>
      </div>
    </div>
  )
}
