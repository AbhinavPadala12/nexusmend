import React, { useState, useEffect, useRef } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts'

const SERVICES = [
  'service_orders',
  'service_payments',
  'service_auth',
  'service_notifications'
]

const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH:     '#f97316',
  MEDIUM:   '#eab308',
  LOW:      '#22c55e'
}

const STATUS_COLORS = {
  healthy:  '#22c55e',
  warning:  '#eab308',
  critical: '#ef4444',
  unknown:  '#6b7280'
}

function useSimulatedData() {
  const [incidents, setIncidents]       = useState([])
  const [metrics, setMetrics]           = useState([])
  const [services, setServices]         = useState({})
  const [prs, setPrs]                   = useState([])
  const [stats, setStats]               = useState({
    totalIncidents: 0,
    prsCreated: 0,
    avgConfidence: 92,
    uptime: 99.7
  })
  const counterRef = useRef(0)

  useEffect(() => {
    const initialServices = {}
    SERVICES.forEach(s => {
      initialServices[s] = {
        status:       'healthy',
        errorRate:    0,
        lastIncident: null
      }
    })
    setServices(initialServices)

    const interval = setInterval(() => {
      counterRef.current += 1
      const t = counterRef.current

      const newMetric = {
        time: new Date().toLocaleTimeString(),
        orders:        Math.floor(Math.random() * 40 + 10),
        payments:      Math.floor(Math.random() * 35 + 8),
        auth:          Math.floor(Math.random() * 50 + 15),
        notifications: Math.floor(Math.random() * 30 + 5),
      }
      setMetrics(prev => [...prev.slice(-20), newMetric])

      if (t % 8 === 0) {
        const svc      = SERVICES[Math.floor(Math.random() * SERVICES.length)]
        const severity = ['CRITICAL','HIGH','HIGH','MEDIUM'][Math.floor(Math.random()*4)]
        const patterns = [
          'Database connectivity issue',
          'Session storage infrastructure failure',
          'Payment gateway timeout',
          'Email infrastructure failure',
          'Authentication token lifecycle issue'
        ]
        const pattern = patterns[Math.floor(Math.random() * patterns.length)]
        const newIncident = {
          id:         `INC-${Date.now()}`,
          service:    svc,
          severity,
          pattern,
          confidence: Math.floor(Math.random() * 10 + 88),
          timestamp:  new Date().toLocaleTimeString(),
          status:     'detected'
        }

        setIncidents(prev => [newIncident, ...prev.slice(0, 19)])
        setServices(prev => ({
          ...prev,
          [svc]: {
            ...prev[svc],
            status:       severity === 'CRITICAL' ? 'critical' : 'warning',
            errorRate:    Math.floor(Math.random() * 30 + 20),
            lastIncident: newIncident.pattern
          }
        }))

        setStats(prev => ({
          ...prev,
          totalIncidents: prev.totalIncidents + 1
        }))

        setTimeout(() => {
          const prNumber = Math.floor(Math.random() * 900 + 100)
          const newPr = {
            id:         `PR-${prNumber}`,
            number:     prNumber,
            title:      `[NexusMend Auto-Fix] ${severity}: ${pattern}`,
            service:    svc,
            severity,
            confidence: newIncident.confidence,
            url:        `https://github.com/AbhinavPadala12/nexusmend/pull/${prNumber}`,
            timestamp:  new Date().toLocaleTimeString(),
            branch:     `nexusmend/auto-fix-${Date.now()}`
          }

          setPrs(prev => [newPr, ...prev.slice(0, 9)])
          setIncidents(prev =>
            prev.map(i =>
              i.id === newIncident.id ? { ...i, status: 'fixed' } : i
            )
          )
          setServices(prev => ({
            ...prev,
            [svc]: { ...prev[svc], status: 'healthy', errorRate: 0 }
          }))
          setStats(prev => ({
            ...prev,
            prsCreated:    prev.prsCreated + 1,
            avgConfidence: Math.floor(Math.random() * 5 + 89)
          }))
        }, 6000)
      }
    }, 1500)

    return () => clearInterval(interval)
  }, [])

  return { incidents, metrics, services, prs, stats }
}

function StatCard({ label, value, sub, color }) {
  return (
    <div style={{
      background:   '#1a1a2e',
      border:       `1px solid ${color}33`,
      borderRadius: 12,
      padding:      '20px 24px',
      flex:         1,
      minWidth:     160
    }}>
      <div style={{ fontSize: 28, fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: 14, color: '#94a3b8', marginTop: 4 }}>{label}</div>
      {sub && <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

function ServiceCard({ name, info }) {
  const color = STATUS_COLORS[info.status] || '#6b7280'
  const displayName = name.replace('service_', '').toUpperCase()
  return (
    <div style={{
      background:   '#1a1a2e',
      border:       `1px solid ${color}44`,
      borderRadius: 10,
      padding:      '14px 18px',
      flex:         1,
      minWidth:     140
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          width: 10, height: 10,
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 6px ${color}`
        }}/>
        <span style={{ fontWeight: 600, fontSize: 13 }}>{displayName}</span>
      </div>
      <div style={{ fontSize: 12, color, marginTop: 6, textTransform: 'uppercase' }}>
        {info.status}
      </div>
      {info.errorRate > 0 && (
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
          Error rate: {info.errorRate}%
        </div>
      )}
      {info.lastIncident && (
        <div style={{
          fontSize: 10, color: '#64748b',
          marginTop: 4, lineHeight: 1.3
        }}>
          {info.lastIncident}
        </div>
      )}
    </div>
  )
}

function IncidentRow({ incident }) {
  const color = SEVERITY_COLORS[incident.severity] || '#6b7280'
  return (
    <div style={{
      display:      'flex',
      alignItems:   'center',
      gap:          12,
      padding:      '10px 0',
      borderBottom: '1px solid #1e293b',
      fontSize:     13
    }}>
      <div style={{
        background:   `${color}22`,
        color,
        padding:      '2px 8px',
        borderRadius: 4,
        fontSize:     11,
        fontWeight:   600,
        minWidth:     70,
        textAlign:    'center'
      }}>
        {incident.severity}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ color: '#e2e8f0', fontWeight: 500 }}>
          {incident.pattern}
        </div>
        <div style={{ color: '#64748b', fontSize: 11, marginTop: 2 }}>
          {incident.service} · {incident.timestamp}
        </div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ color: '#22c55e', fontSize: 11 }}>
          {incident.confidence}% confidence
        </div>
        <div style={{
          fontSize: 11,
          color: incident.status === 'fixed' ? '#22c55e' : '#f97316',
          marginTop: 2
        }}>
          {incident.status === 'fixed' ? '✓ PR Created' : '⟳ Analyzing'}
        </div>
      </div>
    </div>
  )
}

function PRRow({ pr }) {
  const color = SEVERITY_COLORS[pr.severity] || '#6b7280'
  return (
    <div style={{
      padding:      '10px 0',
      borderBottom: '1px solid #1e293b',
      fontSize:     13
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ color: '#22c55e', fontSize: 11, fontWeight: 600 }}>
          #{pr.number}
        </span>
        <span style={{
          background:   `${color}22`,
          color,
          padding:      '1px 6px',
          borderRadius: 4,
          fontSize:     10,
          fontWeight:   600
        }}>
          {pr.severity}
        </span>
        <span style={{ color: '#94a3b8', fontSize: 11 }}>
          {pr.confidence}% confidence
        </span>
      </div>
      <div style={{ color: '#e2e8f0', marginTop: 4, lineHeight: 1.4 }}>
        {pr.title.replace('[NexusMend Auto-Fix] ', '')}
      </div>
      <div style={{ color: '#64748b', fontSize: 11, marginTop: 3 }}>
        {pr.service} · {pr.timestamp}
      </div>
    </div>
  )
}

export default function App() {
  const { incidents, metrics, services, prs, stats } = useSimulatedData()
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setTick(p => p + 1), 1000)
    return () => clearInterval(t)
  }, [])

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: '24px 20px' }}>

      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        marginBottom:   28
      }}>
        <div>
          <h1 style={{
            fontSize:   28,
            fontWeight: 700,
            background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            NexusMend
          </h1>
          <div style={{ color: '#64748b', fontSize: 14, marginTop: 2 }}>
            Autonomous Microservice Healing System
          </div>
        </div>
        <div style={{
          display:    'flex',
          alignItems: 'center',
          gap:        8,
          background: '#1a1a2e',
          padding:    '8px 16px',
          borderRadius: 8,
          border:     '1px solid #22c55e33'
        }}>
          <div style={{
            width: 8, height: 8,
            borderRadius: '50%',
            background: '#22c55e',
            boxShadow: '0 0 6px #22c55e'
          }}/>
          <span style={{ color: '#22c55e', fontSize: 13, fontWeight: 600 }}>
            LIVE
          </span>
          <span style={{ color: '#64748b', fontSize: 12 }}>
            {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
        <StatCard
          label="Total incidents"
          value={stats.totalIncidents}
          sub="Detected by AI"
          color="#6366f1"
        />
        <StatCard
          label="PRs auto-created"
          value={stats.prsCreated}
          sub="Zero human intervention"
          color="#22c55e"
        />
        <StatCard
          label="Avg confidence"
          value={`${stats.avgConfidence}%`}
          sub="RCA accuracy"
          color="#8b5cf6"
        />
        <StatCard
          label="System uptime"
          value={`${stats.uptime}%`}
          sub="Self-healing active"
          color="#06b6d4"
        />
      </div>

      <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
        {Object.entries(services).map(([name, info]) => (
          <ServiceCard key={name} name={name} info={info} />
        ))}
      </div>

      <div style={{
        background:   '#1a1a2e',
        borderRadius: 12,
        padding:      '20px 24px',
        marginBottom: 24,
        border:       '1px solid #1e293b'
      }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: '#94a3b8' }}>
          Error rate over time
        </h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={metrics}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#475569" fontSize={11} />
            <YAxis stroke="#475569" fontSize={11} />
            <Tooltip
              contentStyle={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 8,
                fontSize: 12
              }}
            />
            <Line type="monotone" dataKey="orders"        stroke="#6366f1" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="payments"      stroke="#22c55e" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="auth"          stroke="#f97316" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="notifications" stroke="#8b5cf6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: 20, marginTop: 12, fontSize: 12, color: '#64748b' }}>
          <span style={{ color: '#6366f1' }}>— Orders</span>
          <span style={{ color: '#22c55e' }}>— Payments</span>
          <span style={{ color: '#f97316' }}>— Auth</span>
          <span style={{ color: '#8b5cf6' }}>— Notifications</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        <div style={{
          flex:         1,
          minWidth:     300,
          background:   '#1a1a2e',
          borderRadius: 12,
          padding:      '20px 24px',
          border:       '1px solid #1e293b'
        }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: '#94a3b8' }}>
            Live incidents
          </h2>
          {incidents.length === 0 ? (
            <div style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
              Monitoring all services...
            </div>
          ) : (
            incidents.map(inc => <IncidentRow key={inc.id} incident={inc} />)
          )}
        </div>

        <div style={{
          flex:         1,
          minWidth:     300,
          background:   '#1a1a2e',
          borderRadius: 12,
          padding:      '20px 24px',
          border:       '1px solid #1e293b'
        }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: '#94a3b8' }}>
            Auto-generated PRs
          </h2>
          {prs.length === 0 ? (
            <div style={{ color: '#475569', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
              Waiting for first incident...
            </div>
          ) : (
            prs.map(pr => <PRRow key={pr.id} pr={pr} />)
          )}
        </div>
      </div>

      <div style={{
        textAlign:  'center',
        marginTop:  32,
        color:      '#334155',
        fontSize:   12
      }}>
        NexusMend · Built by Abhinav Padala ·
        github.com/AbhinavPadala12/nexusmend
      </div>
    </div>
  )
}