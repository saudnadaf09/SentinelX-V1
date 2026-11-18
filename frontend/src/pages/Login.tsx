import { FormEvent, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { errText } from '../services/hooks'

const OWNER = {
  name: 'Saud Nadaf',
  line: '2nd-year B.Tech CSE (Cybersecurity) student, Darbhanga College of Engineering (DCE), Darbhanga',
  email: 'saudnadaf.infosec@proton.me',
  linkedin: 'https://www.linkedin.com/in/saud-nadaf-41b015343/',
  github: 'https://github.com/saudnadaf09',
}

const features = [
  ['Detect', '12 versioned YAML rules over Sysmon, Windows Security, Linux auth and Suricata telemetry.'],
  ['Correlate', 'Alerts from different rules are grouped into incidents, with the reason written down.'],
  ['Investigate', 'ATT&CK mapping, evidence snapshots, and an AI assistant that can never act on its own.'],
  ['Respond', 'Dry-run, two-person approval and full audit. Lab-only, simulated actions.'],
]

function Mark() {
  return (
    <svg width="34" height="34" viewBox="0 0 32 32" aria-hidden="true">
      <path d="M16 2 4 7v9c0 7.2 5 12.4 12 14 7-1.6 12-6.8 12-14V7L16 2Z" fill="#141b24" stroke="#6aa6ff" strokeWidth="1.6" />
      <path d="M10 16.5l4 4 8-9" fill="none" stroke="#6aa6ff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export default function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true); setError('')
    try { await login(email, password) } catch (err: any) { setError(errText(err)) } finally { setBusy(false) }
  }

  return (
    <div className="grid min-h-full lg:grid-cols-[1.15fr_1fr]">
      {/* Brand + owner panel */}
      <section className="relative hidden flex-col justify-between overflow-hidden border-r border-line bg-panel p-10 lg:flex"
        style={{ backgroundImage: 'radial-gradient(1200px 500px at -10% -10%, rgba(106,166,255,0.14), transparent 60%), linear-gradient(rgba(42,53,68,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(42,53,68,0.35) 1px, transparent 1px)', backgroundSize: 'auto, 44px 44px, 44px 44px' }}>
        <div className="flex items-center gap-3"><Mark /><div><div className="text-xl font-semibold tracking-tight">SentinelX</div><div className="text-xs text-muted">AI-assisted SIEM and XDR-lite platform</div></div></div>

        <div className="max-w-xl">
          <h1 className="text-4xl font-semibold leading-tight tracking-tight">From raw telemetry to an explained incident, in one console.</h1>
          <ul className="mt-8 space-y-4">
            {features.map(([t, d]) => (
              <li key={t} className="flex gap-4"><span className="mt-0.5 w-24 shrink-0 text-xs font-semibold uppercase tracking-wider text-accent">{t}</span><span className="text-fg/85">{d}</span></li>
            ))}
          </ul>
        </div>

        <div className="rounded-lg border border-line bg-ink/70 p-5 backdrop-blur">
          <div className="text-xs uppercase tracking-wider text-muted">Designed and built by</div>
          <div className="mt-1 text-lg font-semibold">{OWNER.name}</div>
          <p className="mt-1 text-sm text-muted">{OWNER.line}</p>
          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-sm">
            <a href={`mailto:${OWNER.email}`}>{OWNER.email}</a>
            <a href={OWNER.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn</a>
            <a href={OWNER.github} target="_blank" rel="noopener noreferrer">GitHub</a>
          </div>
        </div>
      </section>

      {/* Sign-in */}
      <main className="flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-6 flex items-center gap-3 lg:hidden"><Mark /><span className="text-xl font-semibold">SentinelX</span></div>
          <h2 className="text-2xl font-semibold">Sign in</h2>
          <p className="mb-6 mt-1 text-muted">Authorized analysts and administrators only. Activity on this system is logged.</p>
          <form onSubmit={submit} className="rounded-lg border border-line bg-panel p-6">
            {error && <div role="alert" className="mb-4 rounded-md border border-bad/40 bg-bad/10 px-3 py-2 text-bad">{error}</div>}
            <label className="mb-4 block"><span className="mb-1 block text-xs text-muted">Email</span>
              <input className="field" type="email" autoComplete="username" required autoFocus value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" /></label>
            <label className="mb-5 block"><span className="mb-1 block text-xs text-muted">Password</span>
              <div className="relative">
                <input className="field pr-16" type={show ? 'text' : 'password'} autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
                <button type="button" onClick={() => setShow(!show)} aria-pressed={show} className="absolute inset-y-0 right-2 my-auto h-7 rounded px-2 text-xs text-muted hover:bg-raised hover:text-fg">{show ? 'Hide' : 'Show'}</button>
              </div></label>
            <button disabled={busy} className="w-full rounded-md bg-accent py-2.5 font-medium text-ink hover:brightness-110 disabled:opacity-60">{busy ? 'Signing in...' : 'Sign in'}</button>
          </form>
          <p className="mt-4 text-xs text-muted">Need access or a demo walkthrough? Email <a href={`mailto:${OWNER.email}`}>{OWNER.email}</a>.</p>

          <div className="mt-8 rounded-lg border border-line p-4 text-sm lg:hidden">
            <div className="font-medium">{OWNER.name}</div><div className="text-muted">{OWNER.line}</div>
            <div className="mt-2 flex gap-4"><a href={OWNER.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn</a><a href={OWNER.github} target="_blank" rel="noopener noreferrer">GitHub</a></div>
          </div>
        </div>
        <footer className="mt-10 max-w-sm text-center text-xs text-muted">
          &copy; 2026 {OWNER.name}. All rights reserved. Proprietary software: copying, modification, redistribution or hosting
          without written permission is prohibited. Lab and educational use; response actions are simulated.
        </footer>
      </main>
    </div>
  )
}
