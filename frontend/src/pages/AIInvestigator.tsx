import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import { errText, fmtTime, useApi } from '../services/hooks'
import { useAuth } from '../auth/AuthContext'
import { Button, Card, Empty, ErrorBox, Mono, PageHeader, Select, SeverityBadge } from '../components/ui'

function List({ items }: { items?: string[] }) {
  return items?.length ? <ul className="list-disc pl-5">{items.map((x, i) => <li key={i}>{x}</li>)}</ul> : <span className="text-muted">None</span>
}

export function Analysis({ inv }: { inv: any }) {
  const o = inv.output
  return (
    <div className="space-y-4">
      <div className="rounded-md border border-line bg-raised px-3 py-2 text-xs text-muted">
        Mode: <b className="text-fg">{inv.mode}</b>{inv.model ? ` · ${inv.model}` : ''} · prompt {inv.prompt_version} · {fmtTime(inv.created_at)}
        {inv.note && <div className="mt-1 text-warn">{inv.note}</div>}
        <div className="mt-1">Advisory only. This analysis cannot change the detection verdict or run any action.</div>
      </div>
      <Card title="Summary"><p>{o.summary}</p></Card>
      <Card title="Evidence cited">{o.evidence?.length ? <ul className="space-y-2">{o.evidence.map((e: any) => <li key={e.event_id}><Mono>{e.event_id}</Mono><div>{e.observation}</div></li>)}</ul> : <span className="text-muted">No events cited.</span>}</Card>
      <Card title="Assessment"><p>{o.assessment}</p></Card>
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Possible benign explanations"><List items={o.benign_explanations} /></Card>
        <Card title="Suggested next checks"><List items={o.next_checks} /></Card>
      </div>
      <Card title="ATT&CK context"><p>{o.attack_context}</p></Card>
      <Card title="Limitations"><List items={o.limitations} /></Card>
    </div>
  )
}

export default function AIInvestigator() {
  const { can } = useAuth()
  const [sp, setSp] = useSearchParams()
  const alertId = sp.get('alert') || ''
  const { data: alerts } = useApi(() => api.get('/alerts', { size: 100 }), [])
  const { data: status } = useApi(() => api.get('/ai/status'), [])
  const { data: hist, reload } = useApi(() => api.get('/ai/investigations'), [])
  const [inv, setInv] = useState<any>(null), [busy, setBusy] = useState(false), [err, setErr] = useState<any>(null)

  async function run() {
    setBusy(true); setErr(null)
    try { setInv(await api.post(`/ai/investigate/${alertId}`)); reload() } catch (e) { setErr(e) } finally { setBusy(false) }
  }
  return (
    <>
      <PageHeader title="AI Investigator" subtitle="Evidence-grounded explanations, benign alternatives and next checks for an alert. Optional: without an AI provider, a rule-based analysis is produced instead." />
      {status && <div className={`mb-4 rounded-md border px-3 py-2 ${status.configured ? 'border-ok/40 bg-ok/10 text-ok' : 'border-line bg-panel text-muted'}`}>
        {status.configured ? `AI provider: ${status.provider} (${status.model}). Evidence is redacted before it is sent.` : 'No AI provider configured (AI_PROVIDER=disabled). Rule-based analysis will be used. See SETUP.md to enable one.'}</div>}
      <Card className="mb-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[18rem] flex-1"><span className="mb-1 block text-xs text-muted">Alert</span>
            <Select value={alertId} onChange={(v) => { const n = new URLSearchParams(); if (v) n.set('alert', v); setSp(n); setInv(null) }} placeholder="Select an alert"
              options={(alerts?.items || []).map((a: any) => ({ value: a.id, label: `[${a.severity}] ${a.title} - ${a.host_name || ''}` }))} /></div>
          <Button variant="primary" disabled={!alertId || busy || !can('ai:use')} onClick={run}>{busy ? 'Analyzing...' : 'Investigate'}</Button>
          {alertId && <Link to={`/alerts/${alertId}`}>Open alert</Link>}
        </div>
        {!can('ai:use') && <p className="mt-2 text-xs text-muted">Your role can view past investigations but not run new ones.</p>}
      </Card>
      <ErrorBox error={err} />
      {inv && <div className="mb-6"><Analysis inv={inv} /></div>}
      <Card title="Investigation history" className="!p-0">
        {!hist || hist.items.length === 0 ? <Empty title="No investigations yet" /> : (
          <table className="w-full"><thead><tr><th className="th">When</th><th className="th">Alert</th><th className="th">Mode</th><th className="th" /></tr></thead>
            <tbody>{hist.items.map((h: any) => (<tr key={h.id}><td className="td text-muted">{fmtTime(h.created_at)}</td><td className="td"><Link to={`/alerts/${h.alert_id}`}>{h.alert_title}</Link></td><td className="td">{h.mode}</td>
              <td className="td text-right"><Button onClick={() => setInv(h)}>View</Button></td></tr>))}</tbody></table>)}
      </Card>
    </>
  )
}
