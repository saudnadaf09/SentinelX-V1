import { FormEvent, useState } from 'react'
import { api } from '../services/api'
import { errText, fmtTime, relTime, useApi } from '../services/hooks'
import { useAuth } from '../auth/AuthContext'
import { Button, Card, Empty, ErrorBox, Field, Loading, Modal, Mono, PageHeader, Select, StatusBadge } from '../components/ui'

export default function Assets() {
  const { can } = useAuth()
  const { data, error, reload } = useApi(() => api.get('/assets'), [], 15000)
  const [reg, setReg] = useState(false), [keys, setKeys] = useState<any>(null)
  return (
    <>
      <PageHeader title="Endpoints" subtitle="Registered lab systems and their collectors. Register only systems you are authorized to monitor."
        actions={can('assets:write') && <Button variant="primary" onClick={() => setReg(true)}>Register endpoint</Button>} />
      <ErrorBox error={error} onRetry={reload} />
      <Card className="!p-0">
        {!data ? <Loading /> : data.items.length === 0 ? <Empty title="No endpoints registered" hint="Register a lab endpoint, then create a collector API key for it." /> : (
          <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">Host</th><th className="th">Platform</th><th className="th">Collector</th><th className="th">Last seen</th><th className="th">Events</th><th className="th">Isolation</th><th className="th" /></tr></thead>
            <tbody>{data.items.map((a: any) => (
              <tr key={a.id}><td className="td">{a.hostname}<div className="text-xs text-muted">{(a.tags || []).join(', ')}</div></td><td className="td">{a.platform}</td>
                <td className="td"><StatusBadge value={a.status} /></td><td className="td text-muted" title={fmtTime(a.last_seen_at)}>{relTime(a.last_seen_at)}</td>
                <td className="td">{a.events_received}</td><td className="td text-muted">{a.isolation_state === 'none' ? '-' : a.isolation_state}</td>
                <td className="td text-right">{can('keys:manage') && <Button onClick={() => setKeys(a)}>API keys</Button>}</td></tr>))}</tbody></table></div>
        )}
      </Card>
      {reg && <Register onClose={() => setReg(false)} onDone={() => { setReg(false); reload() }} />}
      {keys && <Keys asset={keys} onClose={() => setKeys(null)} />}
    </>
  )
}

function Register({ onClose, onDone }: any) {
  const [hostname, setHostname] = useState(''), [platform, setPlatform] = useState('windows'), [owner, setOwner] = useState('')
  const [authorized, setAuthorized] = useState(false), [err, setErr] = useState('')
  async function submit(e: FormEvent) {
    e.preventDefault(); setErr('')
    try { await api.post('/assets/register', { hostname, platform, owner: owner || null, authorized }); onDone() } catch (x: any) { setErr(errText(x)) }
  }
  return (
    <Modal title="Register endpoint" onClose={onClose}>
      <form onSubmit={submit}>
        {err && <div role="alert" className="mb-3 text-bad">{err}</div>}
        <Field label="Hostname" hint="Letters, digits, dot, dash, underscore"><input className="field" required pattern="[A-Za-z0-9._-]+" value={hostname} onChange={(e) => setHostname(e.target.value)} /></Field>
        <Field label="Platform"><Select value={platform} onChange={setPlatform} options={['windows', 'linux', 'network']} /></Field>
        <Field label="Owner (optional)"><input className="field" value={owner} onChange={(e) => setOwner(e.target.value)} /></Field>
        <label className="mb-4 flex items-start gap-2"><input type="checkbox" className="mt-1" checked={authorized} onChange={(e) => setAuthorized(e.target.checked)} />
          <span>I am authorized to monitor this system, and it is a lab or test system (not a personal, college, employer or public system).</span></label>
        <div className="flex justify-end gap-2"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary" disabled={!authorized}>Register</Button></div>
      </form>
    </Modal>
  )
}

function Keys({ asset, onClose }: any) {
  const { data, reload } = useApi(() => api.get(`/assets/${asset.id}/keys`), [asset.id])
  const [name, setName] = useState('collector'), [fresh, setFresh] = useState<string | null>(null), [err, setErr] = useState('')
  return (
    <Modal wide title={`Collector keys - ${asset.hostname}`} onClose={onClose}>
      {err && <div role="alert" className="mb-3 text-bad">{err}</div>}
      {fresh && <div className="mb-4 rounded-md border border-ok/40 bg-ok/10 p-3"><div className="mb-1 text-ok">Copy this key now. It will not be shown again.</div><Mono>{fresh}</Mono>
        <div className="mt-2"><Button onClick={() => navigator.clipboard?.writeText(fresh)}>Copy</Button></div></div>}
      <div className="mb-4 flex gap-2"><input className="field" value={name} onChange={(e) => setName(e.target.value)} aria-label="Key name" />
        <Button variant="primary" onClick={async () => { setErr(''); try { const k = await api.post(`/assets/${asset.id}/keys`, { name }); setFresh(k.api_key); reload() } catch (e: any) { setErr(errText(e)) } }}>Create key</Button></div>
      {!data ? <Loading /> : data.items.length === 0 ? <p className="text-muted">No keys yet.</p> : (
        <table className="w-full"><thead><tr><th className="th">Name</th><th className="th">Prefix</th><th className="th">State</th><th className="th">Expires</th><th className="th">Last used</th><th className="th" /></tr></thead>
          <tbody>{data.items.map((k: any) => (<tr key={k.id}><td className="td">{k.name}</td><td className="td"><Mono>sxk_{k.prefix}_...</Mono></td><td className="td"><StatusBadge value={k.state} /></td>
            <td className="td text-muted">{fmtTime(k.expires_at)}</td><td className="td text-muted">{relTime(k.last_used_at)}</td>
            <td className="td">{k.state === 'active' && <Button variant="danger" onClick={async () => { await api.post(`/assets/keys/${k.id}/revoke`); reload() }}>Revoke</Button>}</td></tr>))}</tbody></table>)}
      <p className="mt-3 text-xs text-muted">Send events with header <Mono>X-API-Key</Mono> to <Mono>POST /api/v1/ingest/events/batch</Mono>. See docs/ for the envelope format.</p>
    </Modal>
  )
}
