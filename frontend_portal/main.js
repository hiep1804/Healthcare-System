import './style.css';
import { AuthPage, attachAuthListeners } from './src/pages/Auth.js';
import { RegisterPage, attachRegisterListeners } from './src/pages/Register.js';
import { DashboardPage, attachDashboardListeners } from './src/pages/Dashboard.js';
import { ProvidersPage, attachProvidersListeners } from './src/pages/Providers.js';
import { AppointmentsPage, attachAppointmentsListeners } from './src/pages/Appointments.js';
import { SubscriptionsPage, attachSubscriptionsListeners } from './src/pages/Subscriptions.js';
import { MedicalRecordsPage, attachMedicalRecordsListeners } from './src/pages/MedicalRecords.js';
import { ConsultationsPage, attachConsultationsListeners } from './src/pages/Consultations.js';
import { NotificationsPage, attachNotificationsListeners } from './src/pages/Notifications.js';
import { InsurancePage, attachInsuranceListeners } from './src/pages/Insurance.js';
import { AuditPage, attachAuditListeners } from './src/pages/Audit.js';
import { AdminUsersPage, attachAdminUsersListeners } from './src/pages/AdminUsers.js';
import { ProfilePage, attachProfileListeners } from './src/pages/Profile.js';
import { removeToken } from './src/api.js';

// --- ROUTER ---
const routes = {
  '/': { render: DashboardPage, after: attachDashboardListeners },
  '/login': { render: AuthPage, after: attachAuthListeners },
  '/register': { render: RegisterPage, after: attachRegisterListeners },
  '/providers': { render: ProvidersPage, after: attachProvidersListeners },
  '/appointments': { render: AppointmentsPage, after: attachAppointmentsListeners },
  '/subscriptions': { render: SubscriptionsPage, after: attachSubscriptionsListeners },
  '/medical-records': { render: MedicalRecordsPage, after: attachMedicalRecordsListeners },
  '/consultations': { render: ConsultationsPage, after: attachConsultationsListeners },
  '/notifications': { render: NotificationsPage, after: attachNotificationsListeners },
  '/insurance': { render: InsurancePage, after: attachInsuranceListeners },
  '/audit': { render: AuditPage, after: attachAuditListeners },
  '/admin-users': { render: AdminUsersPage, after: attachAdminUsersListeners },
  '/profile': { render: ProfilePage, after: attachProfileListeners },
};

const router = async () => {
  const path = window.location.hash.slice(1) || '/';
  const app = document.getElementById('app');
  
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const role = user ? user.role : null;

  // Define allowed routes per role based on the Navbar logic
  const allowedRoutes = {
    'PATIENT': ['/', '/profile', '/providers', '/appointments', '/medical-records', '/consultations', '/insurance', '/subscriptions'],
    'DOCTOR': ['/', '/profile', '/appointments', '/consultations'],
    'ADMIN': ['/', '/profile', '/appointments', '/consultations', '/insurance', '/subscriptions', '/notifications', '/audit', '/admin-users']
  };

  const route = routes[path];
  if (route) {
    if (path !== '/login' && path !== '/register' && !user) {
      window.location.hash = '#/login';
      return;
    }

    if (path !== '/login' && path !== '/register' && role && allowedRoutes[role] && !allowedRoutes[role].includes(path)) {
      app.innerHTML = '<div class="container" style="padding-top: 4rem; text-align: center;"><h1>403 Forbidden</h1><p>You do not have permission to view this page.</p><p><a href="#/">Go back to Dashboard</a></p></div>';
      return;
    }

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
