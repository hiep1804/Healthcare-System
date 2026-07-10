import { Navbar } from '../components/Navbar.js';
import { SubscriptionAPI, getErrorMessage } from '../api.js';

export const SubscriptionsPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Service Plans</h1>
        <p class="text-muted">Choose a subscription plan that fits your needs.</p>
      </div>

      <div id="plansList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading plans... (Ensure Subscription Service 8009 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachSubscriptionsListeners = async () => {
  const container = document.getElementById('plansList');
  if (!container) return;

  try {
    const data = await SubscriptionAPI.getPlans();
    const plans = data.results || data;
    
    if (plans.length === 0) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No subscription plans found in database.</div>`;
      return;
    }

    container.innerHTML = plans.map(p => `
      <div class="stat-card glass-panel" style="align-items: center; text-align: center; padding: 2.5rem 1.5rem;">
        <h2 style="color: var(--primary-blue); font-size: 1.5rem; margin-bottom: 0.5rem;">${p.name}</h2>
        <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">$${p.price_per_month} <span style="font-size: 1rem; font-weight: normal; color: var(--text-muted);">/ mo</span></div>
        <p style="margin-bottom: 2rem; font-size: 0.95rem; color: var(--text-muted); min-height: 40px;">${p.description || 'Premium healthcare benefits.'}</p>
        <button class="btn btn-primary" style="width: 100%;" onclick="alert('Proceed to payment for ${p.name}')">Select Plan</button>
      </div>
    `).join('');
  } catch (e) {
    const msg = getErrorMessage(e, 'Failed to load plans.');
    container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">${msg}</div>`;
  }
};
