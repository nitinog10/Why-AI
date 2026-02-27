/**
 * ConstraintPanel — Sliders, presets, query input, and submit button.
 * Controls all user-facing constraint inputs.
 */

const PRESETS = [
    { id: 'student', label: 'Student', icon: '📚', desc: 'Budget + time focused' },
    { id: 'saver', label: 'Saver', icon: '💰', desc: 'Maximum savings' },
    { id: 'explorer', label: 'Explorer', icon: '🧭', desc: 'Discovery first' },
];

const DOMAIN_PLACEHOLDERS = {
    campus: 'e.g. "quick vegetarian lunch under ₹100"',
    retail: 'e.g. "birthday gift for a tech enthusiast"',
    travel: 'e.g. "something fun during a 2-hour layover"',
};

export default function ConstraintPanel({
    domain,
    query,
    onQueryChange,
    budget,
    onBudgetChange,
    time,
    onTimeChange,
    comfortExploration,
    onComfortExplorationChange,
    preset,
    onPresetChange,
    onSubmit,
    loading,
}) {
    // Budget ranges per domain
    const budgetConfig = {
        campus: { min: 10, max: 500, step: 10 },
        retail: { min: 100, max: 30000, step: 100 },
        travel: { min: 50, max: 5000, step: 50 },
    };

    const timeConfig = {
        campus: { min: 5, max: 120, step: 5 },
        retail: { min: 5, max: 60, step: 5 },
        travel: { min: 10, max: 300, step: 10 },
    };

    const bc = budgetConfig[domain] || budgetConfig.campus;
    const tc = timeConfig[domain] || timeConfig.campus;

    const formatBudget = (v) => {
        if (v >= 1000) return `₹${(v / 1000).toFixed(v % 1000 === 0 ? 0 : 1)}K`;
        return `₹${v}`;
    };

    const comfortLabel =
        comfortExploration < 0.3
            ? 'Comfort'
            : comfortExploration > 0.7
                ? 'Exploration'
                : 'Balanced';

    return (
        <div className="constraint-panel">
            <div className="panel-title">
                <span className="icon">⚙️</span>
                Your Constraints
            </div>

            {/* Query Input */}
            <div className="query-section">
                <label className="query-label">What are you looking for?</label>
                <textarea
                    className="query-input"
                    placeholder={DOMAIN_PLACEHOLDERS[domain]}
                    value={query}
                    onChange={(e) => onQueryChange(e.target.value)}
                />
            </div>

            {/* Budget Slider */}
            <div className="slider-group">
                <div className="slider-header">
                    <span className="slider-label">💸 Budget</span>
                    <span className="slider-value">{formatBudget(budget)}</span>
                </div>
                <input
                    type="range"
                    className="slider-input"
                    min={bc.min}
                    max={bc.max}
                    step={bc.step}
                    value={budget}
                    onChange={(e) => onBudgetChange(Number(e.target.value))}
                />
                <div className="slider-endpoints">
                    <span>{formatBudget(bc.min)}</span>
                    <span>{formatBudget(bc.max)}</span>
                </div>
            </div>

            {/* Time Slider */}
            <div className="slider-group">
                <div className="slider-header">
                    <span className="slider-label">⏱️ Time Available</span>
                    <span className="slider-value">{time} min</span>
                </div>
                <input
                    type="range"
                    className="slider-input"
                    min={tc.min}
                    max={tc.max}
                    step={tc.step}
                    value={time}
                    onChange={(e) => onTimeChange(Number(e.target.value))}
                />
                <div className="slider-endpoints">
                    <span>{tc.min} min</span>
                    <span>{tc.max} min</span>
                </div>
            </div>

            {/* Comfort ↔ Exploration Slider */}
            <div className="slider-group">
                <div className="slider-header">
                    <span className="slider-label">🎯 Preference</span>
                    <span className="slider-value">{comfortLabel}</span>
                </div>
                <input
                    type="range"
                    className="slider-input"
                    min={0}
                    max={1}
                    step={0.05}
                    value={comfortExploration}
                    onChange={(e) => onComfortExplorationChange(Number(e.target.value))}
                />
                <div className="slider-endpoints">
                    <span>🛋️ Comfort</span>
                    <span>🗺️ Explore</span>
                </div>
            </div>

            {/* Presets */}
            <div className="presets-section">
                <div className="presets-label">Quick Presets</div>
                <div className="presets-grid">
                    {PRESETS.map((p) => (
                        <button
                            key={p.id}
                            className={`preset-btn ${preset === p.id ? 'active' : ''}`}
                            onClick={() => onPresetChange(preset === p.id ? null : p.id)}
                            title={p.desc}
                        >
                            <span className="preset-icon">{p.icon}</span>
                            {p.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Submit */}
            <button className="submit-btn" onClick={onSubmit} disabled={loading}>
                {loading ? (
                    <>
                        <div className="spinner" />
                        Thinking...
                    </>
                ) : (
                    <>🔍 Get Recommendations</>
                )}
            </button>
        </div>
    );
}
