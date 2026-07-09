import { Navbar } from '../components/Navbar.js';
import { NotificationAPI } from '../api.js';

export const NotificationsPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Notifications</h1>
        <p class="text-muted">Your communication logs and alerts.</p>
      </div>

      <div id="notificationList" class="dashboard-grid" style="grid-template-columns: 1fr;">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Loading notifications... (Ensure Notification Service 8007 is running)
        </div>
      </div>
    </div>
  `;
};

export const attachNotificationsListeners = async () => {
  const container = document.getElementById('notificationList');
  if (!container) return;

  try {
    const data = await NotificationAPI.getTemplates();
    const templates = data.results || data;
    
    if (templates.length === 0) {
      container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No notification templates found.</div>`;
      return;
    }

    container.innerHTML = templates.map(n => `
      <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1rem 1.5rem;">
        <h3 style="color: var(--primary-blue); font-size: 1rem; margin-bottom: 0.2rem;">Template: ${n.name}</h3>
        <p style="margin-bottom: 0.5rem; font-size: 0.9rem; font-weight: 500;">Subject: ${n.subject}</p>
        <p style="color: var(--text-muted); font-size: 0.85rem;">Body: ${n.body}</p>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = `<div class="alert alert-error">Failed to load templates. Is Notification Service (8007) running?</div>`;
  }
};
