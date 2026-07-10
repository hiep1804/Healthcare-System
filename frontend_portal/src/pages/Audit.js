import { Navbar } from '../components/Navbar.js';
import { AuditAPI, getUser, getErrorMessage } from '../api.js';

export const AuditPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">System Audit Logs</h1>
        <p class="text-muted">Security and access events (Admin view).</p>
      </div>

      <div id="auditList" class="dashboard-grid" style="grid-template-columns: 1fr;">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading audit events... (Ensure Audit Service 8008 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachAuditListeners = async () => {
  const container = document.getElementById('auditList');
  if (!container) return;
  
  const user = getUser();
  // We can restrict to Admin only here if needed, but let's show to anyone for demo
  if (!user) return;

  try {
    const data = await AuditAPI.getEvents();
    const events = data.results || data;
    
    if (events.length === 0) {
      container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No audit events found.</div>`;
      return;
    }

    container.innerHTML = events.map(e => `
      <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1rem 1.5rem; border-left: 4px solid #f59e0b;">
        <h3 style="color: var(--text-main); font-size: 0.95rem; margin-bottom: 0.2rem;">Action: ${e.action}</h3>
        <p style="margin-bottom: 0.2rem; font-size: 0.85rem; color: var(--text-muted);">Service: ${e.service_name} | User ID: ${e.user_id || 'System'}</p>
        <p style="color: var(--text-muted); font-size: 0.8rem;">Resource: ${e.resource_type} (${e.resource_id}) at ${new Date(e.timestamp).toLocaleString()}</p>
      </div>
    `).join('');
  } catch (e) {
    if (e.status === 403) {
      container.innerHTML = `<div class="alert alert-error">Access Denied. You do not have permission to view audit logs.</div>`;
    } else {
      container.innerHTML = `<div class="alert alert-error">Failed to load events. Is Audit Service (8008) running?</div>`;
    }
  }
};
