import { Navbar } from '../components/Navbar.js';
import { InsuranceAPI, getErrorMessage } from '../api.js';

export const InsurancePage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Insurance</h1>
        <p class="text-muted">Manage your health insurance policies and claims.</p>
      </div>

      <div id="insuranceList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading policies... (Ensure Insurance Service 8010 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachInsuranceListeners = async () => {
  const container = document.getElementById('insuranceList');
  if (!container) return;

  try {
    const data = await InsuranceAPI.getPolicies();
    const policies = data.results || data;
    
    if (policies.length === 0) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No insurance policies found.</div>`;
      return;
    }

    container.innerHTML = policies.map(p => `
      <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1.5rem;">
        <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-bottom: 0.5rem;">Provider: ${p.provider_name}</h3>
        <p style="margin-bottom: 0.5rem; font-size: 0.95rem;"><strong>Policy Number:</strong> ${p.policy_number}</p>
        <span style="display: inline-block; padding: 4px 10px; background: ${p.is_active ? '#def7ec' : '#fde8e8'}; color: ${p.is_active ? '#03543f' : '#9b1c1c'}; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
          ${p.is_active ? 'ACTIVE' : 'INACTIVE'}
        </span>
      </div>
    `).join('');
  } catch (e) {
    const msg = getErrorMessage(e, 'Failed to load policies.');
    container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">${msg}</div>`;
  }
};
