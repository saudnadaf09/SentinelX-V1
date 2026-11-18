import { FormEvent, useState } from 'react'
import { api } from '../services/api'
import { errText, fmtTime, useApi } from '../services/hooks'
import { useAuth } from '../auth/AuthContext'
import { Button, Card, ErrorBox, Field, Loading, Modal, PageHeader, Select, StatusBadge } from '../components/ui'

export default function Settings() {
  const { user, can } = useAuth()
  return (
    <>
      <PageHeader title="Settings" />
      <div className="space-y-4">
        <Password />
        {can('users:manage') && <Users />}
        {can('settings:read') && <System />}
        {!can('settings:read') && <Card title="Account"><p>Signed in as {user?.email} ({user?.role}).</p></Card>}
      </div>
    </>
  )
}

function Password() {
  const [cur, setCur] = useState(''), [next, setNext] = useState(''), [msg, setMsg] = useState<{ ok: boolean; t: string } | null>(null)
  async function submit(e: FormEvent) {
    e.preventDefault(); setMsg(null)
    try { await api.post('/auth/change-password', { current_password: cur, new_password: next }); setCur(''); setNext(''); setMsg({ ok: true, t: 'Password changed. Other sessions were signed out.' }) } catch (x: any) { setMsg({ ok: false, t: errText(x) }) }
  }
  return (
    <Card title="Change password">
      <form onSubmit={submit} className="grid max-w-xl gap-3 md:grid-cols-2">
        <Field label="Current password"><input className="field" type="password" autoComplete="current-password" required value={cur} onChange={(e) => setCur(e.target.value)} /></Field>
        <Field label="New password (12+ characters)"><input className="field" type="password" autoComplete="new-password" required minLength={12} value={next} onChange={(e) => setNext(e.target.value)} /></Field>
        <div className="md:col-span-2"><Button variant="primary">Update password</Button>{msg && <span role="status" className={`ml-3 ${msg.ok ? 'text-ok' : 'text-bad'}`}>{msg.t}</span>}</div>
      </form>
    </Card>
  )
}

function Users() {
  const { data, error, reload } = useApi(() => api.get('/users'), [])
  const [adding, setAdding] = useState(false), [msg, setMsg] = useState('')
  async function patch(id: string, body: any) { setMsg(''); try { await api.patch(`/users/${id}`, body); reload() } catch (e: any) { setMsg(errText(e)) } }
  return (
    <Card title="Users and roles" actions={<Button onClick={() => setAdding(true)}>Add user</Button>}>
      {msg && <div role="alert" className="mb-2 text-bad">{msg}</div>}
      <ErrorBox error={error} onRetry={reload} />
      {!data ? <Loading /> : (
        <table className="w-full"><thead><tr><th className="th">Email</th><th className="th">Role</th><th className="th">Status</th><th className="th">Last login</th><th className="th" /></tr></thead>
          <tbody>{data.items.map((u: any) => (
            <tr key={u.id}><td className="td">{u.email}</td>
              <td className="td w-40"><Select value={u.role} onChange={(v) => patch(u.id, { role: v })} options={['admin', 'analyst', 'engineer', 'viewer']} /></td>
              <td className="td"><StatusBadge value={u.is_active ? 'active' : 'revoked'} /></td><td className="td text-muted">{fmtTime(u.last_login_at)}</td>
              <td className="td text-right"><Button onClick={() => patch(u.id, { is_active: !u.is_active })}>{u.is_active ? 'Deactivate' : 'Activate'}</Button></td></tr>))}</tbody></table>)}
      {adding && <AddUser onClose={() => setAdding(false)} onDone={() => { setAdding(false); reload() }} />}
    </Card>
  )
}

function AddUser({ onClose, onDone }: any) {
  const [email, setEmail] = useState(''), [role, setRole] = useState('analyst'), [pw, setPw] = useState(''), [err, setErr] = useState('')
  async function submit(e: FormEvent) { e.preventDefault(); setErr(''); try { await api.post('/users', { email, role, password: pw }); onDone() } catch (x: any) { setErr(errText(x)) } }
  return (
    <Modal title="Add user" onClose={onClose}>
      <form onSubmit={submit}>
        {err && <div role="alert" className="mb-3 text-bad">{err}</div>}
        <Field label="Email"><input className="field" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
        <Field label="Role"><Select value={role} onChange={setRole} options={['admin', 'analyst', 'engineer', 'viewer']} /></Field>
        <Field label="Initial password (12+ characters)"><input className="field" type="password" required minLength={12} autoComplete="new-password" value={pw} onChange={(e) => setPw(e.target.value)} /></Field>
        <div className="flex justify-end gap-2"><Button type="button" onClick={onClose}>Cancel</Button><Button variant="primary">Create user</Button></div>
      </form>
    </Modal>
  )
}

function System() {
  const { data, error } = useApi(() => api.get('/settings/system'), [])
  const { data: ready } = useApi(() => api.get('/health/ready'), [], 20000)
  if (error) return <ErrorBox error={error} />
  if (!data) return <Loading />
  const rows: [string, any][] = [['Version', data.version], ['Environment', data.environment], ['Queue backend', data.queue_backend], ['Event store', data.store_backend],
    ['Event retention (days)', data.event_retention_days], ['Collector key lifetime (days)', data.collector_key_ttl_days], ['Active rules', data.active_rules],
    ['Correlation window (s)', data.correlation_window_seconds], ['Response adapter', data.response_adapter + ' (simulation only)'], ['Approval window (min)', data.approval_ttl_minutes],
    ['AI provider', data.ai.configured ? `${data.ai.provider} / ${data.ai.model}` : 'disabled (rule-based analysis)']]
  return (
    <Card title="System (read-only; change values in .env and restart)">
      <dl className="grid gap-x-8 gap-y-2 md:grid-cols-2">{rows.map(([k, v]) => <div key={k} className="flex justify-between border-b border-line/50 py-1"><dt className="text-muted">{k}</dt><dd>{String(v)}</dd></div>)}</dl>
      {ready && <div className="mt-3 flex gap-4 text-xs">{Object.entries(ready.checks).map(([k, v]) => <span key={k} className={v ? 'text-ok' : 'text-bad'}>{k}: {v ? 'ok' : 'down'}</span>)}</div>}
    </Card>
  )
}
