import './style.css';
import { AuthPage, attachAuthListeners } from './src/pages/Auth.js';
import { DashboardPage, attachDashboardListeners } from './src/pages/Dashboard.js';
import { ProvidersPage, attachProvidersListeners } from './src/pages/Providers.js';
import { AppointmentsPage, attachAppointmentsListeners } from './src/pages/Appointments.js';
import { SubscriptionsPage, attachSubscriptionsListeners } from './src/pages/Subscriptions.js';
import { MedicalRecordsPage, attachMedicalRecordsListeners } from './src/pages/MedicalRecords.js';
import { ConsultationsPage, attachConsultationsListeners } from './src/pages/Consultations.js';
import { NotificationsPage, attachNotificationsListeners } from './src/pages/Notifications.js';
import { InsurancePage, attachInsuranceListeners } from './src/pages/Insurance.js';
import { AuditPage, attachAuditListeners } from './src/pages/Audit.js';
import { removeToken } from './src/api.js';

// --- ROUTER ---
const routes = {
  '/': { render: DashboardPage, after: attachDashboardListeners },
  '/login': { render: AuthPage, after: attachAuthListeners },
  '/providers': { render: ProvidersPage, after: attachProvidersListeners },
  '/appointments': { render: AppointmentsPage, after: attachAppointmentsListeners },
  '/subscriptions': { render: SubscriptionsPage, after: attachSubscriptionsListeners },
  '/medical-records': { render: MedicalRecordsPage, after: attachMedicalRecordsListeners },
  '/consultations': { render: ConsultationsPage, after: attachConsultationsListeners },
  '/notifications': { render: NotificationsPage, after: attachNotificationsListeners },
  '/insurance': { render: InsurancePage, after: attachInsuranceListeners },
  '/audit': { render: AuditPage, after: attachAuditListeners },
};

const router = async () => {
  const path = window.location.hash.slice(1) || '/';
  const app = document.getElementById('app');
  
  const route = routes[path];
  if (route) {
    app.innerHTML = route.render();
    if (route.after) {
      await route.after();
    }
  } else {
    app.innerHTML = '<div class="container" style="padding-top: 4rem; text-align: center;"><h1>404 Not Found</h1><p><a href="#/">Go back to Dashboard</a></p></div>';
  }

  // Global Logout Button Listener
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn && !logoutBtn.dataset.bound) {
    logoutBtn.dataset.bound = "true";
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      removeToken();
      localStorage.removeItem('user');
      window.location.hash = '#/login';
    });
  }
};

window.addEventListener('hashchange', router);
window.addEventListener('load', router);
