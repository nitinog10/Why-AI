import { useState } from 'react';
import './index.css';
import DomainSelector from './components/DomainSelector';
import ConstraintPanel from './components/ConstraintPanel';
import RecommendationCard from './components/RecommendationCard';
import { getRecommendations } from './api';

/**
 * App — Root component for WHY.AI
 * Manages domain, constraints, and recommendation state.
 */

// Default constraints per domain
const DOMAIN_DEFAULTS = {
  campus: { budget: 200, time: 30 },
  retail: { budget: 2000, time: 30 },
  travel: { budget: 1000, time: 120 },
};

export default function App() {
  // Domain state
  const [domain, setDomain] = useState('campus');

  // Constraint state
  const [query, setQuery] = useState('');
  const [budget, setBudget] = useState(DOMAIN_DEFAULTS.campus.budget);
  const [time, setTime] = useState(DOMAIN_DEFAULTS.campus.time);
  const [comfortExploration, setComfortExploration] = useState(0.5);
  const [preset, setPreset] = useState(null);

  // Results state
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Switch domain → reset constraints to domain defaults
  const handleDomainChange = (newDomain) => {
    setDomain(newDomain);
    setBudget(DOMAIN_DEFAULTS[newDomain].budget);
    setTime(DOMAIN_DEFAULTS[newDomain].time);
    setComfortExploration(0.5);
    setPreset(null);
    setResults(null);
    setError(null);
  };

  // Submit recommendation request
  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRecommendations({
        query,
        constraints: { budget, time, comfort_vs_exploration: comfortExploration },
        domain,
        preset,
      });
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-inner">
          <div className="app-logo">
            <div className="logo-icon">W</div>
            <div className="logo-text">
              <h1>WHY.AI</h1>
              <span>Constraint-Aware Consumer Intelligence</span>
            </div>
          </div>
          <DomainSelector active={domain} onChange={handleDomainChange} />
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {/* Left: Constraint Panel */}
        <ConstraintPanel
          domain={domain}
          query={query}
          onQueryChange={setQuery}
          budget={budget}
          onBudgetChange={setBudget}
          time={time}
          onTimeChange={setTime}
          comfortExploration={comfortExploration}
          onComfortExplorationChange={setComfortExploration}
          preset={preset}
          onPresetChange={setPreset}
          onSubmit={handleSubmit}
          loading={loading}
        />

        {/* Right: Results */}
        <div className="results-area">
          {error && (
            <div style={{
              padding: '16px',
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              borderRadius: '12px',
              color: '#f43f5e',
              marginBottom: '20px',
              fontSize: '14px',
            }}>
              ⚠️ {error}
            </div>
          )}

          {!results && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">🧠</div>
              <div className="empty-title">Ready to help you decide</div>
              <div className="empty-subtitle">
                Set your constraints using the sliders, describe what you're looking for,
                and hit "Get Recommendations". Every suggestion will explain <strong>WHY</strong> it was chosen.
              </div>
            </div>
          )}

          {results && (
            <>
              <div className="results-header">
                <div className="results-title">
                  Recommendations
                </div>
                <div className="results-meta">
                  <strong>{results.recommendations.length}</strong> results from {results.total_items} items
                  {results.filtered_out > 0 && (
                    <> · {results.filtered_out} filtered by constraints</>
                  )}
                </div>
              </div>

              <div className="rec-cards">
                {results.recommendations.map((item, i) => (
                  <RecommendationCard key={item.id} item={item} rank={i + 1} />
                ))}
              </div>

              {results.recommendations.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">🚫</div>
                  <div className="empty-title">No options match your constraints</div>
                  <div className="empty-subtitle">
                    Try increasing your budget or time limit.
                    All {results.filtered_out} items were filtered out by your hard constraints.
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        WHY.AI — No black-box recommendations. Every decision is transparent and constraint-aware.
      </footer>
    </div>
  );
}
