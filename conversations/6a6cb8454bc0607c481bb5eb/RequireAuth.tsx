import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className='min-h-screen bg-bg-base flex items-center justify-center'>
        <div className='flex flex-col items-center gap-3'>
          <div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' />
          <p className='text-sm text-text-tertiary'>Loading EvolvixOS…</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to='/login' replace />
  }

  return <>{children}</>
}
