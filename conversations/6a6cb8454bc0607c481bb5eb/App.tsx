import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/hooks/useAuth'
import { RequireAuth } from '@/components/RequireAuth'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { PricingPage } from '@/pages/PricingPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { AIWorkspacePage } from '@/pages/AIWorkspacePage'
import { ProjectsPage } from '@/pages/ProjectsPage'
import { MonitoringPage } from '@/pages/MonitoringPage'
import { SecurityPage } from '@/pages/SecurityPage'
import { DeploymentsPage } from '@/pages/DeploymentsPage'
import { KnowledgePage } from '@/pages/KnowledgePage'
import { SettingsPage } from '@/pages/SettingsPage'
import { PlaceholderPage } from '@/pages/PlaceholderPage'
import { BarChart3, Activity, Network, FileText } from 'lucide-react'

function AppShell() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className='min-h-screen bg-bg-base'>
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed(!collapsed)}
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />
      <div className={`transition-all duration-300 ${collapsed ? 'lg:pl-[60px]' : 'lg:pl-[240px]'}`}>
        <Topbar onMenuClick={() => setMobileOpen(true)} />
        <main className='p-4 lg:p-6 max-w-[1600px] mx-auto'>
          <Routes>
            <Route index element={<DashboardPage />} />
            <Route path='ai-workspace' element={<AIWorkspacePage />} />
            <Route path='projects' element={<ProjectsPage />} />
            <Route path='repositories' element={
              <PlaceholderPage title='Repositories' description='Browse and manage all connected repositories' icon={<Network className='h-7 w-7 text-text-tertiary' />} />
            } />
            <Route path='deployments' element={<DeploymentsPage />} />
            <Route path='knowledge' element={<KnowledgePage />} />
            <Route path='monitoring' element={<MonitoringPage />} />
            <Route path='security' element={<SecurityPage />} />
            <Route path='analytics' element={
              <PlaceholderPage title='Analytics' description='Engineering metrics, velocity, and insights' icon={<BarChart3 className='h-7 w-7 text-text-tertiary' />} />
            } />
            <Route path='activity' element={
              <PlaceholderPage title='Activity Feed' description='Real-time activity across all projects and agents' icon={<Activity className='h-7 w-7 text-text-tertiary' />} />
            } />
            <Route path='docs' element={
              <PlaceholderPage title='Documentation' description='Full developer documentation portal' icon={<FileText className='h-7 w-7 text-text-tertiary' />} />
            } />
            <Route path='settings' element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Landing page — no sidebar/topbar */}
        <Route path='/' element={<LandingPage />} />

        {/* Auth routes — standalone pages */}
        <Route path='/login' element={<LoginPage />} />
        <Route path='/register' element={<RegisterPage />} />
        <Route path='/pricing' element={<PricingPage />} />

        {/* App routes — auth-guarded with sidebar + topbar */}
        <Route path='/app/*' element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        } />
      </Routes>
    </AuthProvider>
  )
}
