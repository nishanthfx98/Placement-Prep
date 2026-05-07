import { useState, useEffect, useRef } from 'react'
import './App.css'

const API = 'http://localhost:5000/api'

const COMPANY_COLORS = {
  google:    { bg: '#1a3a2a', color: '#34d399', label: 'G' },
  amazon:    { bg: '#2a1a0a', color: '#fb923c', label: 'A' },
  microsoft: { bg: '#0a1a3a', color: '#60a5fa', label: 'M' },
  apple:     { bg: '#1a1a1a', color: '#a3a3a3', label: '🍎' },
  netflix:   { bg: '#2a0a0a', color: '#ef4444', label: 'N' },
  tcs:       { bg: '#0a2a1a', color: '#4ade80', label: 'T' },
  accenture: { bg: '#1a0a2a', color: '#c084fc', label: 'Ac' },
  zoho:      { bg: '#0a1a2a', color: '#38bdf8', label: 'Z' },
}

const QUICK_PROMPTS = [
  'Show easy problems for Google',
  'Top Amazon questions',
  'TCS stats',
  'Tips for Microsoft',
  'Give me array problems',
  'HR interview questions',
  'How to prepare in 30 days?',
  'Give me aptitude questions',
]

function formatMessage(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

function FitBar({ fit }) {
  const color = fit >= 70 ? '#22c55e' : fit >= 40 ? '#f59e0b' : '#ef4444'
  return (
    <div style={{ marginTop: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 3 }}>
        <span style={{ color: '#94a3b8' }}>Fit Score</span>
        <span style={{ color, fontWeight: 700 }}>{fit}%</span>
      </div>
      <div style={{ background: '#0f172a', borderRadius: 4, height: 6, overflow: 'hidden' }}>
        <div style={{ width: `${fit}%`, background: color, height: '100%', borderRadius: 4, transition: 'width 0.6s ease' }} />
      </div>
    </div>
  )
}

function SkillsTab() {
  const [input, setInput] = useState('')
  const [skills, setSkills] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [expandedRole, setExpandedRole] = useState(null)
  const [filterCompany, setFilterCompany] = useState('all')

  const addSkill = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      const s = input.trim().replace(/,$/, '')
      if (s && !skills.includes(s)) setSkills(prev => [...prev, s])
      setInput('')
    }
  }

  const removeSkill = (s) => setSkills(prev => prev.filter(x => x !== s))

  const analyze = async () => {
    if (!skills.length) return
    setLoading(true)
    setResults(null)
    setExpandedRole(null)
    try {
      const res = await fetch(`${API}/skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills })
      })
      setResults(await res.json())
    } catch {
      alert('Could not connect to backend.')
    }
    setLoading(false)
  }

  // Flatten all roles for "best matches" view
  const allRoles = results
    ? Object.entries(results).flatMap(([company, roles]) =>
        Object.entries(roles).map(([role, data]) => ({ company, role, ...data }))
      ).sort((a, b) => b.fit - a.fit)
    : []

  const companies = results ? Object.keys(results) : []

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>💡 Skill Analyzer & Career Roadmap</h1>
        <p>Enter your skills to see how well you fit each role across all companies</p>
      </div>

      {/* Skill Input */}
      <div className="skills-input-box">
        <div className="skills-tags">
          {skills.map(s => (
            <span key={s} className="skill-tag">
              {s} <button onClick={() => removeSkill(s)}>×</button>
            </span>
          ))}
          <input
            className="skill-input-inline"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={addSkill}
            placeholder={skills.length ? 'Add more skills...' : 'Type a skill and press Enter (e.g. Python, SQL, React)'}
          />
        </div>
        <div style={{ display: 'flex', gap: 10, marginTop: 12, alignItems: 'center' }}>
          <button className="send-btn" onClick={analyze} disabled={loading || !skills.length}>
            {loading ? 'Analyzing...' : '🔍 Analyze My Skills'}
          </button>
          {skills.length > 0 && (
            <button className="filter-btn" onClick={() => { setSkills([]); setResults(null) }}>Clear</button>
          )}
          <span style={{ fontSize: 12, color: '#475569' }}>{skills.length} skill{skills.length !== 1 ? 's' : ''} added</span>
        </div>
        <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {['Python', 'Java', 'SQL', 'Machine Learning', 'React', 'AWS', 'Data Structures', 'System Design'].map(s => (
            <button key={s} className="quick-prompt" onClick={() => !skills.includes(s) && setSkills(p => [...p, s])}>
              + {s}
            </button>
          ))}
        </div>
      </div>

      {results && (
        <>
          {/* Top Matches */}
          <div style={{ marginBottom: 24 }}>
            <h3 style={{ color: '#f1f5f9', marginBottom: 12, fontSize: 15 }}>🏆 Best Role Matches (All Companies)</h3>
            <div className="stats-grid">
              {allRoles.slice(0, 8).map(({ company, role, fit, description }) => {
                const style = COMPANY_COLORS[company] || { bg: '#1e293b', color: '#38bdf8' }
                return (
                  <div key={`${company}-${role}`} className="stat-card"
                    onClick={() => setExpandedRole(expandedRole === `${company}-${role}` ? null : `${company}-${role}`)}>
                    <div className="stat-card-header">
                      <span className="stat-card-icon" style={{ background: style.bg, color: style.color }}>
                        {COMPANY_COLORS[company]?.label}
                      </span>
                      <div>
                        <div style={{ fontSize: 12, fontWeight: 600, color: '#e2e8f0' }}>{role}</div>
                        <div style={{ fontSize: 11, color: '#64748b' }}>{company.charAt(0).toUpperCase() + company.slice(1)}</div>
                      </div>
                    </div>
                    <FitBar fit={fit} />
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 8 }}>{description}</div>
                    {expandedRole === `${company}-${role}` && (
                      <RoadmapDetail data={results[company][role]} />
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Per-Company Breakdown */}
          <div style={{ marginBottom: 12, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: 12, color: '#64748b' }}>Filter:</span>
            <button className={`filter-btn ${filterCompany === 'all' ? 'active' : ''}`} onClick={() => setFilterCompany('all')}>All</button>
            {companies.map(c => (
              <button key={c} className={`filter-btn ${filterCompany === c ? 'active' : ''}`} onClick={() => setFilterCompany(c)}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </button>
            ))}
          </div>

          {companies.filter(c => filterCompany === 'all' || c === filterCompany).map(company => (
            <div key={company} style={{ marginBottom: 24 }}>
              <h3 style={{ color: COMPANY_COLORS[company]?.color || '#38bdf8', marginBottom: 12, fontSize: 15 }}>
                {company.charAt(0).toUpperCase() + company.slice(1)}
              </h3>
              <div className="stats-grid">
                {Object.entries(results[company]).map(([role, data]) => (
                  <div key={role} className="stat-card"
                    onClick={() => setExpandedRole(expandedRole === `${company}-${role}` ? null : `${company}-${role}`)}>
                    <div style={{ fontWeight: 600, fontSize: 13, color: '#e2e8f0', marginBottom: 8 }}>{role}</div>
                    <FitBar fit={data.fit} />
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 6 }}>{data.description}</div>
                    {expandedRole === `${company}-${role}` && <RoadmapDetail data={data} />}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  )
}

function RoadmapDetail({ data }) {
  return (
    <div style={{ marginTop: 12, borderTop: '1px solid #334155', paddingTop: 12 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: '#38bdf8', marginBottom: 8 }}>📍 Roadmap</div>
      {data.roadmap.map((step, i) => (
        <div key={i} style={{ fontSize: 12, color: '#94a3b8', marginBottom: 6, lineHeight: 1.5 }}
          dangerouslySetInnerHTML={{ __html: step.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#e2e8f0">$1</strong>') }} />
      ))}
      {data.missing_required.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 11, color: '#ef4444', fontWeight: 600, marginBottom: 4 }}>Missing Required Skills:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {data.missing_required.map(s => (
              <span key={s} style={{ background: '#450a0a', color: '#ef4444', padding: '2px 8px', borderRadius: 4, fontSize: 11 }}>{s}</span>
            ))}
          </div>
        </div>
      )}
      {data.missing_good_to_have.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 11, color: '#f59e0b', fontWeight: 600, marginBottom: 4 }}>Good to Have (Missing):</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {data.missing_good_to_have.slice(0, 5).map(s => (
              <span key={s} style={{ background: '#451a03', color: '#f59e0b', padding: '2px 8px', borderRadius: 4, fontSize: 11 }}>{s}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState('chat')
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [messages, setMessages] = useState([{
    role: 'bot', type: 'text',
    text: "👋 Hi! I'm your **Placement Prep AI**.\n\nI can help you with:\n• 🎯 Company-specific LeetCode problems\n• 🧠 Aptitude & reasoning questions\n• 🎤 Interview preparation tips\n• 📅 Study plans & strategies\n• 💡 Skill analysis & career roadmap\n\nTry: *'Give me array problems'*, *'HR interview tips'*, *'30-day plan'*\nOr go to the **💡 Skills** tab to analyze your skills!",
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState([])
  const [problems, setProblems] = useState([])
  const [diffFilter, setDiffFilter] = useState('All')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/stats`).then(r => r.json()).then(setStats).catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedCompany) {
      const url = diffFilter === 'All'
        ? `${API}/problems/${selectedCompany}?limit=50`
        : `${API}/problems/${selectedCompany}?difficulty=${diffFilter}&limit=50`
      fetch(url).then(r => r.json()).then(setProblems).catch(() => {})
    }
  }, [selectedCompany, diffFilter])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', type: 'text', text: msg }])
    setLoading(true)
    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'bot', ...data }])
    } catch {
      setMessages(prev => [...prev, { role: 'bot', type: 'text', text: '❌ Could not connect to server.' }])
    }
    setLoading(false)
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-logo">
          <h2>🎯 PlacementAI</h2>
          <p>Your interview prep assistant</p>
        </div>
        <div className="sidebar-section">Companies</div>
        {Object.entries(COMPANY_COLORS).map(([company, style]) => (
          <button key={company} className={`company-btn ${selectedCompany === company ? 'active' : ''}`}
            onClick={() => { setSelectedCompany(company); setTab('problems') }}>
            <span className="company-icon" style={{ background: style.bg, color: style.color }}>{style.label}</span>
            {company.charAt(0).toUpperCase() + company.slice(1)}
          </button>
        ))}
      </div>

      {/* Main */}
      <div className="main">
        <div className="tabs">
          <button className={`tab-btn ${tab === 'chat' ? 'active' : ''}`} onClick={() => setTab('chat')}>💬 Chat</button>
          <button className={`tab-btn ${tab === 'dashboard' ? 'active' : ''}`} onClick={() => setTab('dashboard')}>📊 Dashboard</button>
          <button className={`tab-btn ${tab === 'skills' ? 'active' : ''}`} onClick={() => setTab('skills')}>💡 Skills</button>
          {selectedCompany && (
            <button className={`tab-btn ${tab === 'problems' ? 'active' : ''}`} onClick={() => setTab('problems')}>
              📋 {selectedCompany.charAt(0).toUpperCase() + selectedCompany.slice(1)} Problems
            </button>
          )}
        </div>

        {/* Chat Tab */}
        {tab === 'chat' && (
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <div className="message-avatar">{msg.role === 'bot' ? '🤖' : '👤'}</div>
                  <div className="message-bubble">
                    <div dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }} />
                    {(msg.type === 'problems' || msg.type === 'dsa_problems') && msg.problems && (
                      <div className="chat-problems">
                        {msg.problems.map((p, j) => (
                          <div key={j} className="chat-problem-item">
                            <span className={`badge badge-${(p.Difficulty || p.difficulty)?.toLowerCase()}`}>
                              {p.Difficulty || p.difficulty}
                            </span>
                            <a href={p.URL || p.url} target="_blank" rel="noreferrer">{p.Title || p.title}</a>
                            {p['Frequency %'] && <span style={{ color: '#64748b', fontSize: 11 }}>⚡{p['Frequency %']}%</span>}
                          </div>
                        ))}
                      </div>
                    )}
                    {msg.type === 'stats' && msg.data && (
                      <div className="chat-stats-grid">
                        {msg.data.map((s, j) => (
                          <div key={j} className="chat-stat-item">
                            <div className="company-name">{s.company}</div>
                            <div>Total: {s.total}</div>
                            <div style={{ color: '#22c55e' }}>Easy: {s.easy}</div>
                            <div style={{ color: '#f59e0b' }}>Medium: {s.medium}</div>
                            <div style={{ color: '#ef4444' }}>Hard: {s.hard}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message bot">
                  <div className="message-avatar">🤖</div>
                  <div className="message-bubble">
                    <div className="typing-indicator">
                      <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-area">
              <div className="quick-prompts">
                {QUICK_PROMPTS.map((p, i) => (
                  <button key={i} className="quick-prompt" onClick={() => sendMessage(p)}>{p}</button>
                ))}
              </div>
              <div className="chat-input-row">
                <input className="chat-input" value={input} onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKey} placeholder="Ask about problems, aptitude, interview tips, study plans..."
                  disabled={loading} />
                <button className="send-btn" onClick={() => sendMessage()} disabled={loading || !input.trim()}>Send</button>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Tab */}
        {tab === 'dashboard' && (
          <div className="dashboard">
            <div className="dashboard-header">
              <h1>📊 Placement Dashboard</h1>
              <p>Overview of all company problem sets — click a card to explore</p>
            </div>
            <div className="stats-grid">
              {stats.map((s, i) => {
                const company = s.company.toLowerCase()
                const style = COMPANY_COLORS[company] || { bg: '#1e293b', color: '#38bdf8', label: s.company[0] }
                return (
                  <div key={i} className="stat-card" onClick={() => { setSelectedCompany(company); setTab('problems') }}>
                    <div className="stat-card-header">
                      <span className="stat-card-icon" style={{ background: style.bg, color: style.color }}>{style.label}</span>
                      <span className="stat-card-name">{s.company}</span>
                    </div>
                    <div className="stat-row"><span>Total Problems</span><span>{s.total}</span></div>
                    <div className="stat-row"><span style={{ color: '#22c55e' }}>Easy</span><span>{s.easy}</span></div>
                    <div className="stat-row"><span style={{ color: '#f59e0b' }}>Medium</span><span>{s.medium}</span></div>
                    <div className="stat-row"><span style={{ color: '#ef4444' }}>Hard</span><span>{s.hard}</span></div>
                    <div className="stat-row"><span>Avg Acceptance</span><span>{s.avg_acceptance}%</span></div>
                    <div className="diff-bar" style={{ marginTop: 12 }}>
                      <div className="diff-bar-easy" style={{ flex: s.easy }} />
                      <div className="diff-bar-medium" style={{ flex: s.medium }} />
                      <div className="diff-bar-hard" style={{ flex: s.hard }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Skills Tab */}
        {tab === 'skills' && <SkillsTab />}

        {/* Problems Tab */}
        {tab === 'problems' && selectedCompany && (
          <div className="dashboard">
            <div className="problems-section">
              <div className="problems-header">
                <h3>
                  <span style={{ color: COMPANY_COLORS[selectedCompany]?.color }}>
                    {selectedCompany.charAt(0).toUpperCase() + selectedCompany.slice(1)}
                  </span> Problems — Easy to Hard
                </h3>
                <div className="filter-group">
                  {['All', 'Easy', 'Medium', 'Hard'].map(d => (
                    <button key={d} className={`filter-btn ${diffFilter === d ? 'active' : ''}`}
                      onClick={() => setDiffFilter(d)}>{d}</button>
                  ))}
                </div>
              </div>
              <table className="problems-table">
                <thead>
                  <tr><th>#</th><th>Title</th><th>Difficulty</th><th>Acceptance</th><th>Frequency</th></tr>
                </thead>
                <tbody>
                  {problems.map((p, i) => (
                    <tr key={i}>
                      <td style={{ color: '#475569' }}>{p.ID}</td>
                      <td><a className="problem-link" href={p.URL} target="_blank" rel="noreferrer">{p.Title}</a></td>
                      <td><span className={`badge badge-${p.Difficulty?.toLowerCase()}`}>{p.Difficulty}</span></td>
                      <td>{p['Acceptance %']}%</td>
                      <td>⚡ {p['Frequency %']}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
