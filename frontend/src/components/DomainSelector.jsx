import { useState } from 'react';

/**
 * DomainSelector — Tab bar for switching between campus, retail, travel domains.
 */

const DOMAINS = [
    { id: 'campus', label: 'Campus', icon: '🎓' },
    { id: 'retail', label: 'Retail', icon: '🛍️' },
    { id: 'travel', label: 'Travel', icon: '✈️' },
];

export default function DomainSelector({ active, onChange }) {
    return (
        <div className="domain-tabs">
            {DOMAINS.map((d) => (
                <button
                    key={d.id}
                    className={`domain-tab ${active === d.id ? 'active' : ''}`}
                    onClick={() => onChange(d.id)}
                >
                    <span className="tab-icon">{d.icon}</span>
                    {d.label}
                </button>
            ))}
        </div>
    );
}
