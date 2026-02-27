/**
 * api.js — API client for WHY.AI backend
 */

const API_BASE = 'http://localhost:8000';

/**
 * Call POST /recommend
 * @param {object} params
 * @param {string} params.query - Natural language user intent
 * @param {object} params.constraints - { budget, time, comfort_vs_exploration }
 * @param {string} params.domain - campus | retail | travel
 * @param {string|null} params.preset - student | saver | explorer | null
 * @returns {Promise<object>} Recommendation response
 */
export async function getRecommendations({ query, constraints, domain, preset }) {
  const response = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query || '',
      constraints: {
        budget: constraints.budget,
        time: constraints.time,
        comfort_vs_exploration: constraints.comfort_vs_exploration,
      },
      domain,
      preset: preset || null,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error (${response.status}): ${error}`);
  }

  return response.json();
}
