import { getUser } from '../api.js';

export const Navbar = () => {
  const user = getUser();
  
  if (!user) {
    return `
      <nav class="navbar glass-panel">
        <div class="container">
          <a href="#/" class="logo">Health<span>Care</span></a>
          <div class="nav-links">
            <a href="#/login">Login</a>
          </div>
        </div>
      </nav>
    `;
  }

  const isPatient = user.role === 'PATIENT';
  
  return `
    <nav class="navbar glass-panel">
      <div class="container">
        <a href="#/" class="logo">Health<span>Care</span></a>
        <div class="nav-links">
          <span>${user.email}</span>
          <a href="#/" class="${location.hash === '#/' ? 'active' : ''}">Dashboard</a>
          ${isPatient ? `<a href="#/providers" class="${location.hash === '#/providers' ? 'active' : ''}">Find Doctor</a>` : ''}
          <a href="#/appointments" class="${location.hash === '#/appointments' ? 'active' : ''}">Appointments</a>
          ${isPatient ? `<a href="#/medical-records" class="${location.hash === '#/medical-records' ? 'active' : ''}">Records</a>` : ''}
          <a href="#/consultations" class="${location.hash === '#/consultations' ? 'active' : ''}">Consultations</a>
          <a href="#/insurance" class="${location.hash === '#/insurance' ? 'active' : ''}">Insurance</a>
          <a href="#/notifications" class="${location.hash === '#/notifications' ? 'active' : ''}">Alerts</a>
          <a href="#/subscriptions" class="${location.hash === '#/subscriptions' ? 'active' : ''}">Plans</a>
          <a href="#/audit" class="${location.hash === '#/audit' ? 'active' : ''}">Audit</a>
          <a href="#" id="logoutBtn" style="color: #ef4444; font-weight: 600;">Logout</a>
        </div>
      </div>
    </nav>
  `;
};
