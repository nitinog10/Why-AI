import { useState } from 'react';

/**
 * RecommendationCard — Displays a single recommendation with score,
 * meta info, tags, and expandable WHY explanations.
 */
export default function RecommendationCard({ item, rank }) {
    const [expanded, setExpanded] = useState(false);

    const scorePercent = Math.round(item.score * 100);
    const bd = item.score_breakdown || {};

    return (
        <div className={`rec-card ${item.is_discovery ? 'discovery' : ''}`}>
            {/* Top Row: Name + Score */}
            <div className="card-top">
                <div className="card-info">
                    <div className="card-name">
                        {item.name}
                        {item.is_discovery && (
                            <span className="discovery-badge">🔍 Discovery</span>
                        )}
                    </div>
                    <div className="card-category">{item.category}</div>
                </div>
                <div className="card-score">
                    <div className="score-circle">{scorePercent}</div>
                    <span className="score-label">Score</span>
                </div>
            </div>

            {/* Description */}
            <p className="card-desc">{item.description}</p>

            {/* Meta: Price, Time */}
            <div className="card-meta">
                <div className="meta-item">
                    <span className="meta-icon">💰</span>
                    <span className="meta-value">₹{item.price}</span>
                </div>
                <div className="meta-item">
                    <span className="meta-icon">⏱️</span>
                    <span className="meta-value">{item.time_minutes} min</span>
                </div>
                <div className="meta-item">
                    <span className="meta-icon">🛋️</span>
                    Comfort: <span className="meta-value">{Math.round(item.comfort_score * 100)}%</span>
                </div>
                <div className="meta-item">
                    <span className="meta-icon">🗺️</span>
                    Explore: <span className="meta-value">{Math.round(item.exploration_score * 100)}%</span>
                </div>
            </div>

            {/* Tags */}
            <div className="card-tags">
                {item.tags.map((tag) => (
                    <span key={tag} className="tag">
                        {tag}
                    </span>
                ))}
            </div>

            {/* Score Breakdown Mini Bars */}
            <div className="score-breakdown">
                <div className="breakdown-item">
                    <div className="breakdown-bar-bg">
                        <div
                            className="breakdown-bar-fill budget"
                            style={{ width: `${(bd.budget_efficiency || 0) * 100}%` }}
                        />
                    </div>
                    <span className="breakdown-label">Budget {Math.round((bd.budget_efficiency || 0) * 100)}%</span>
                </div>
                <div className="breakdown-item">
                    <div className="breakdown-bar-bg">
                        <div
                            className="breakdown-bar-fill time"
                            style={{ width: `${(bd.time_efficiency || 0) * 100}%` }}
                        />
                    </div>
                    <span className="breakdown-label">Time {Math.round((bd.time_efficiency || 0) * 100)}%</span>
                </div>
                <div className="breakdown-item">
                    <div className="breakdown-bar-bg">
                        <div
                            className="breakdown-bar-fill alignment"
                            style={{ width: `${(bd.alignment || 0) * 100}%` }}
                        />
                    </div>
                    <span className="breakdown-label">Fit {Math.round((bd.alignment || 0) * 100)}%</span>
                </div>
            </div>

            {/* WHY Section */}
            <div className="why-section">
                <button className="why-toggle" onClick={() => setExpanded(!expanded)}>
                    <span>💡</span>
                    Why this?
                    <span className={`arrow ${expanded ? 'open' : ''}`}>▼</span>
                </button>

                {expanded && (
                    <div className="why-details">
                        {/* Why Recommended */}
                        <div className="why-block recommended">
                            <div className="why-block-title">
                                <span>✅</span> Why Recommended
                            </div>
                            <p>{item.why_recommended}</p>
                        </div>

                        {/* Tradeoffs */}
                        <div className="why-block tradeoffs">
                            <div className="why-block-title">
                                <span>⚖️</span> Tradeoffs
                            </div>
                            <p>{item.tradeoffs}</p>
                        </div>

                        {/* Why Others Lower */}
                        {item.why_others_lower && (
                            <div className="why-block others">
                                <div className="why-block-title">
                                    <span>📊</span> Why Others Ranked Lower
                                </div>
                                <p>{item.why_others_lower}</p>
                            </div>
                        )}

                        {/* Discovery Explanation */}
                        {item.is_discovery && item.discovery_reason && (
                            <div className="discovery-explanation">
                                <span className="disc-icon">🔍</span>
                                <span>{item.discovery_reason}</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
