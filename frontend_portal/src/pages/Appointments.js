import { Navbar } from '../components/Navbar.js';
import { AppointmentAPI } from '../api.js';

export const AppointmentsPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Appointments</h1>
        <p class="text-muted">Manage your upcoming and past appointments.</p>
      </div>

      <div id="appointmentsList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading appointments... (Ensure Appointment Service 8004 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachAppointmentsListeners = async () => {
  const container = document.getElementById('appointmentsList');
  if (!container) return;

  try {
    const data = await AppointmentAPI.getAppointments();
    const appointments = data.results || data;
    
    if (appointments.length === 0) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No appointments found.</div>`;
      return;
    }

    container.innerHTML = appointments.map(a => `
      <div class="stat-card glass-panel" style="align-items: flex-start; border-left: 4px solid ${a.status === 'CONFIRMED' ? 'var(--secondary-teal)' : 'var(--text-muted)'}">
        <h3 style="color: var(--text-main);">${new Date(a.appointment_datetime).toLocaleString()}</h3>
        <p style="margin-bottom: 0.5rem;"><strong>Status:</strong> ${a.status}</p>
        <p style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-muted);">Notes: ${a.reason_for_visit || 'N/A'}</p>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Failed to load appointments. Is Appointment Service (8004) running?</div>`;
  }
};
