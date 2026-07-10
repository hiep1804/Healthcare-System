import { Navbar } from '../components/Navbar.js';
import { ConsultationAPI, getErrorMessage } from '../api.js';

export const ConsultationsPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Consultations (SOAP Notes)</h1>
        <p class="text-muted">Clinical notes and diagnoses from visits.</p>
      </div>

      <div id="consultationList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading consultations... (Ensure Consultation Service 8005 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachConsultationsListeners = async () => {
  const container = document.getElementById('consultationList');
  if (!container) return;

  try {
    const data = await ConsultationAPI.getConsultations();
    const consultations = data.results || data;
    
    if (consultations.length === 0) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No consultations found.</div>`;
      return;
    }

    container.innerHTML = consultations.map(c => `
      <div class="stat-card glass-panel" style="align-items: flex-start;">
        <h3 style="color: var(--primary-blue);">ID: ${c.id.split('-')[0]}</h3>
        <p style="margin-bottom: 0.5rem; font-size: 0.9rem;"><strong>Notes:</strong> ${c.subjective_notes || 'N/A'}</p>
        <p style="color: var(--text-muted); font-size: 0.85rem;">Diagnosis: ${c.diagnosis_codes ? c.diagnosis_codes.join(', ') : 'None'}</p>
      </div>
    `).join('');
  } catch (e) {
    const msg = getErrorMessage(e, 'Failed to load consultations.');
    container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">${msg}</div>`;
  }
};
