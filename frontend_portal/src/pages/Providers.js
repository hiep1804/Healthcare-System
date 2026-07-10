import { Navbar } from '../components/Navbar.js';
import { ProviderAPI, getErrorMessage } from '../api.js';

export const ProvidersPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Find a Doctor</h1>
        <p class="text-muted">Search for healthcare providers across different specialties.</p>
      </div>

      <div id="providerList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading providers... (Ensure Provider Service 8003 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachProvidersListeners = async () => {
  const providerList = document.getElementById('providerList');
  if (!providerList) return;

  try {
    const data = await ProviderAPI.getProviders();
    const providers = data.results || data;
    
    if (providers.length === 0) {
      providerList.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No providers found in the database.</div>`;
      return;
    }

    providerList.innerHTML = providers.map(p => `
      <div class="stat-card glass-panel" style="align-items: flex-start;">
        <h3 style="color: var(--primary-blue); font-size: 1.1rem;">${p.first_name} ${p.last_name}</h3>
        <p style="margin-bottom: 0.5rem;"><strong>Specialty:</strong> ${p.specialty_name || p.specialty || 'General'}</p>
        <p style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-muted);">Clinic: ${p.clinic_name || 'N/A'}</p>
        <button class="btn btn-primary" onclick="alert('Booking appointment for provider ${p.id} - requires Appointment Service integration')">Book Appointment</button>
      </div>
    `).join('');
  } catch (e) {
    providerList.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Failed to load providers. Is Provider Service (8003) running?</div>`;
  }
};
