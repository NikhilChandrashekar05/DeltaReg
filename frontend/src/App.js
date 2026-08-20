import { useState } from 'react';

const styles = {
  app: { fontFamily: 'Inter, sans-serif', background: '#f8fafc', minHeight: '100vh', padding: '2rem' },
  header: { background: '#1e3a5f', color: 'white', padding: '1.5rem 2rem', borderRadius: '12px', marginBottom: '2rem' },
  headerTitle: { margin: 0, fontSize: '24px', fontWeight: '600' },
  headerSub: { margin: '4px 0 0', fontSize: '14px', opacity: 0.8 },
  card: { background: 'white', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem', border: '1px solid #e2e8f0' },
  cardTitle: { fontSize: '16px', fontWeight: '600', color: '#1e3a5f', marginBottom: '1rem', borderBottom: '2px solid #e53e3e', paddingBottom: '8px' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' },
  label: { fontSize: '13px', fontWeight: '500', color: '#4a5568', marginBottom: '4px', display: 'block' },
  input: { width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e0', fontSize: '14px', boxSizing: 'border-box', outline: 'none' },
  textarea: { width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e0', fontSize: '14px', boxSizing: 'border-box', height: '80px', resize: 'vertical' },
  button: { background: '#e53e3e', color: 'white', border: 'none', padding: '12px 32px', borderRadius: '8px', fontSize: '15px', fontWeight: '600', cursor: 'pointer', marginTop: '1rem' },
  metricRow: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' },
  metric: { background: '#f8fafc', borderRadius: '10px', padding: '1rem', border: '1px solid #e2e8f0', textAlign: 'center' },
  metricVal: { fontSize: '22px', fontWeight: '700', color: '#1e3a5f' },
  metricLabel: { fontSize: '12px', color: '#718096', marginTop: '4px' },
  badge: { display: 'inline-block', padding: '3px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '500', marginRight: '6px' },
  ruleCard: { background: '#f8fafc', borderRadius: '8px', padding: '12px', marginBottom: '8px', borderLeft: '3px solid #1e3a5f' },
  posCard: { background: '#f8fafc', borderRadius: '8px', padding: '12px', marginBottom: '8px', borderLeft: '3px solid #e53e3e' },
  tag: { fontSize: '11px', background: '#ebf8ff', color: '#2b6cb0', padding: '2px 8px', borderRadius: '12px', marginRight: '4px', display: 'inline-block', marginBottom: '4px' },
  high: { background: '#fff5f5', color: '#c53030' },
  medium: { background: '#fffaf0', color: '#c05621' },
  loading: { textAlign: 'center', padding: '2rem', color: '#718096', fontSize: '15px' }
};

function App() {
  const [concept, setConcept] = useState('CET1');
  const [oldClause, setOldClause] = useState('Banks must hold 8% capital against risk-weighted assets');
  const [newClause, setNewClause] = useState('Banks must hold 10% capital against risk-weighted assets');
  const [oldRisk, setOldRisk] = useState('0.08');
  const [newRisk, setNewRisk] = useState('0.10');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [graphData, setGraphData] = useState(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);

  async function handleSubmit() {
    setLoading(true);
    setResult(null);
    const response = await fetch('http://localhost:8000/impact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        changed_concept: concept,
        old_clause: oldClause,
        new_clause: newClause,
        old_risk_weight: parseFloat(oldRisk),
        new_risk_weight: parseFloat(newRisk)
      })
    });
    const data = await response.json();
    setResult(data);
    setLoading(false);
  }

  async function handleRunPipeline() {
    setPipelineRunning(true);
    await fetch('http://localhost:8000/run-pipeline', { method: 'POST' });
    await fetchGraphData();
    setPipelineRunning(false);
  }

  async function fetchGraphData() {
    const response = await fetch('http://localhost:8000/graph-data');
    const data = await response.json();
    setGraphData(data);
  }

  return (
    <div style={styles.app}>
      <div style={styles.header}>
        <h1 style={styles.headerTitle}>DeltaReg — Regulatory Change Intelligence</h1>
        <p style={styles.headerSub}>Detect regulatory changes and map impact to portfolio positions in real time</p>
      </div>

      <div style={styles.card}>
        <div style={styles.cardTitle}>Live Regulatory Ontology Pipeline</div>
        <p style={{ fontSize: '13px', color: '#718096', marginBottom: '12px' }}>
          Pulls live documents from the Federal Register API and automatically expands the regulatory knowledge graph using Claude.
        </p>
        <button style={styles.button} onClick={handleRunPipeline} disabled={pipelineRunning}>
          {pipelineRunning ? 'Running pipeline...' : 'Run Live Pipeline'}
        </button>

        {graphData && (
          <div style={{ marginTop: '1.5rem' }}>
            <div style={{ fontSize: '13px', fontWeight: '600', color: '#1e3a5f', marginBottom: '8px' }}>
              Auto-Extracted Rules ({graphData.rules.length})
            </div>
            {graphData.rules.map((r, i) => (
              <div key={i} style={styles.ruleCard}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#1e3a5f' }}>{r.rule_id} — {r.regulator}</div>
                <div style={{ marginTop: '6px' }}>
                  {r.concepts.map(c => <span key={c} style={styles.tag}>{c}</span>)}
                </div>
              </div>
            ))}

            <div style={{ fontSize: '13px', fontWeight: '600', color: '#1e3a5f', margin: '16px 0 8px' }}>
              Concept Dependencies ({graphData.dependencies.length})
            </div>
            {graphData.dependencies.map((d, i) => (
              <div key={i} style={{ fontSize: '13px', color: '#4a5568', padding: '6px 0', borderBottom: '1px solid #e2e8f0' }}>
                {d.from_concept} → {d.to_concept}
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={styles.card}>
        <div style={styles.cardTitle}>Regulatory Change Input</div>
        <div style={{ marginBottom: '1rem' }}>
          <label style={styles.label}>Changed Concept</label>
          <input style={styles.input} value={concept} onChange={e => setConcept(e.target.value)} placeholder="e.g. CET1" />
        </div>
        <div style={styles.grid}>
          <div>
            <label style={styles.label}>Old Clause</label>
            <textarea style={styles.textarea} value={oldClause} onChange={e => setOldClause(e.target.value)} placeholder="Previous regulation text..." />
          </div>
          <div>
            <label style={styles.label}>New Clause</label>
            <textarea style={styles.textarea} value={newClause} onChange={e => setNewClause(e.target.value)} placeholder="Updated regulation text..." />
          </div>
          <div>
            <label style={styles.label}>Old Risk Weight</label>
            <input style={styles.input} value={oldRisk} onChange={e => setOldRisk(e.target.value)} placeholder="e.g. 0.08" />
          </div>
          <div>
            <label style={styles.label}>New Risk Weight</label>
            <input style={styles.input} value={newRisk} onChange={e => setNewRisk(e.target.value)} placeholder="e.g. 0.10" />
          </div>
        </div>
        <button style={styles.button} onClick={handleSubmit} disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Impact Analysis'}
        </button>
      </div>

      {loading && <div style={styles.loading}>Running pipeline — graph traversal → LLM extraction → portfolio mapping...</div>}

      {result && (
        <>
          <div style={styles.metricRow}>
            <div style={styles.metric}>
              <div style={styles.metricVal}>{result.impacted_rules.length}</div>
              <div style={styles.metricLabel}>Rules Impacted</div>
            </div>
            <div style={styles.metric}>
              <div style={styles.metricVal}>{result.impacted_positions.length}</div>
              <div style={styles.metricLabel}>Positions Affected</div>
            </div>
            <div style={styles.metric}>
              <div style={{ ...styles.metricVal, color: '#e53e3e' }}>
                ${result.total_additional_capital.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
              <div style={styles.metricLabel}>Additional Capital Required</div>
            </div>
          </div>

          <div style={styles.card}>
            <div style={styles.cardTitle}>LLM Extraction — What Changed</div>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ ...styles.badge, background: '#ebf8ff', color: '#2b6cb0' }}>{result.extraction.change_type}</span>
              <span style={{ ...styles.badge, background: '#fff5f5', color: '#c53030' }}>{result.extraction.direction}</span>
              <span style={{ ...styles.badge, background: '#f0fff4', color: '#276749' }}>{result.extraction.magnitude} impact</span>
            </div>
            <p style={{ fontSize: '14px', color: '#4a5568', margin: '8px 0' }}>{result.extraction.what_changed}</p>
            <div style={{ marginTop: '8px' }}>
              {result.extraction.affected_instruments.map(i => <span key={i} style={styles.tag}>{i}</span>)}
            </div>
          </div>

          <div style={styles.card}>
            <div style={styles.cardTitle}>Impacted Rules — Neo4j Cascade</div>
            {result.impacted_rules.map((r, i) => (
              <div key={i} style={styles.ruleCard}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#1e3a5f' }}>{r.rule_id}</div>
                <div style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
                  Regulator: {r.regulator} | Via: {r.downstream_concept}
                </div>
              </div>
            ))}
          </div>

          <div style={styles.card}>
            <div style={styles.cardTitle}>Portfolio Impact — Capital Delta</div>
            {result.impacted_positions.map((p, i) => (
              <div key={i} style={styles.posCard}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#1e3a5f' }}>{p.instrument_type}</div>
                    <div style={{ fontSize: '12px', color: '#718096', marginTop: '2px' }}>{p.business_line} | Notional: ${p.notional.toLocaleString()}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '15px', fontWeight: '700', color: '#e53e3e' }}>
                      +${p.additional_capital_required.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                    <span style={{ ...styles.badge, ...(p.materiality === 'high' ? styles.high : styles.medium), fontSize: '11px' }}>
                      {p.materiality}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;