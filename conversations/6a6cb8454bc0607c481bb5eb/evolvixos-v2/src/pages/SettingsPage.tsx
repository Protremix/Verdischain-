import { Settings, User, KeyRound, Bell, Palette, Globe } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export function SettingsPage() {
  return (
    <div className="space-y-6 animate-fade-in-up max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Settings</h1>
        <p className="mt-1 text-sm text-text-secondary">Manage your account and platform preferences</p>
      </div>

      <Card padding="md">
        <CardHeader>
          <div className="flex items-center gap-2">
            <User className="h-4.5 w-4.5 text-text-secondary" />
            <CardTitle>Profile</CardTitle>
          </div>
        </CardHeader>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input label="Full Name" defaultValue="Rojs Gordons" />
          <Input label="Email" defaultValue="rojs@protremix.com" />
          <Input label="Organization" defaultValue="Protremix" />
          <Input label="Role" defaultValue="Founder & CEO" />
        </div>
        <div className="mt-4">
          <Button size="sm">Save Changes</Button>
        </div>
      </Card>

      <Card padding="md">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Palette className="h-4.5 w-4.5 text-text-secondary" />
            <CardTitle>Appearance</CardTitle>
          </div>
        </CardHeader>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-primary">Theme</p>
              <p className="text-xs text-text-tertiary">Dark mode is default with light mode support</p>
            </div>
            <Badge variant="brand" dot>Dark</Badge>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-primary">Accent Color</p>
              <p className="text-xs text-text-tertiary">Indigo — used across buttons, links, and highlights</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-lg bg-brand ring-2 ring-brand/30" />
              <div className="h-6 w-6 rounded-lg bg-success" />
              <div className="h-6 w-6 rounded-lg bg-warning" />
              <div className="h-6 w-6 rounded-lg bg-danger" />
            </div>
          </div>
        </div>
      </Card>

      <Card padding="md">
        <CardHeader>
          <div className="flex items-center gap-2">
            <KeyRound className="h-4.5 w-4.5 text-text-secondary" />
            <CardTitle>API Keys</CardTitle>
          </div>
        </CardHeader>
        <div className="space-y-2">
          <div className="flex items-center justify-between rounded-lg border border-border p-3">
            <div>
              <p className="text-sm font-medium text-text-primary">Production API Key</p>
              <p className="text-xs text-text-tertiary font-mono">evx_live_••••••••••3a7f</p>
            </div>
            <Badge variant="success" dot>Active</Badge>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-border p-3">
            <div>
              <p className="text-sm font-medium text-text-primary">Staging API Key</p>
              <p className="text-xs text-text-tertiary font-mono">evx_stg_••••••••••9c2e</p>
            </div>
            <Badge variant="success" dot>Active</Badge>
          </div>
        </div>
        <div className="mt-3">
          <Button variant="outline" size="sm">Generate New Key</Button>
        </div>
      </Card>

      <Card padding="md">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="h-4.5 w-4.5 text-text-secondary" />
            <CardTitle>Notifications</CardTitle>
          </div>
        </CardHeader>
        <div className="space-y-3">
          {['Deployment completions', 'Security alerts', 'AI agent activity', 'Weekly summary reports'].map(item => (
            <div key={item} className="flex items-center justify-between">
              <span className="text-sm text-text-primary">{item}</span>
              <div className="relative h-5 w-9 rounded-full bg-brand cursor-pointer transition-colors">
                <div className="absolute right-0.5 top-0.5 h-4 w-4 rounded-full bg-white transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
