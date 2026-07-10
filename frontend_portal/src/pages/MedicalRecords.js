import { Navbar } from '../components/Navbar.js';
import { MedicalRecordAPI, getUser, getErrorMessage } from '../api.js';

export const MedicalRecordsPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Medical Records</h1>
        <p class="text-muted">Your clinical health data and vitals.</p>
      </div>

      <div id="recordsList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading records... (Ensure Medical Record Service 8006 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachMedicalRecordsListeners = async () => {
  const container = document.getElementById('recordsList');
  if (!container) return;
  const user = getUser();
  if (!user) return;

  try {
    const data = await MedicalRecordAPI.getRecords(user.id);
    const records = data.results || data;
    
    if (records.length === 0) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No medical records found for your account.</div>`;
      return;
    }

    container.innerHTML = records.map(r => `
      <div class="stat-card glass-panel" style="align-items: flex-start;">
        <h3 style="color: var(--primary-blue);">Record Type: ${r.record_type}</h3>
        <p style="margin-bottom: 0.5rem; font-size: 0.9rem;"><strong>Date:</strong> ${new Date(r.created_at).toLocaleDateString()}</p>
        <p style="margin-bottom: 1rem; color: var(--text-main);">${r.details || 'No details provided.'}</p>
      </div>
    `).join('');
  } catch (e) {
    if (e.status === 404) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Patient profile must be created first to have medical records.</div>`;
    } else {
        container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Failed to load records. Is Medical Record Service (8006) running?</div>`;
    }
  }
};
