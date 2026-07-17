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
  const isDoctor = user.role === 'DOCTOR';
  const isAdmin = user.role === 'ADMIN';
  
  return `
    <nav class="navbar glass-panel">
      <div class="container">
        <a href="#/" class="logo">Health<span>Care</span></a>
        <div class="nav-links">
          <span>${user.last_name || user.email} <strong style="color:var(--primary-blue); font-size: 0.8em;">[${user.role}]</strong></span>
          <a href="#/" class="${location.hash === '#/' ? 'active' : ''}">Dashboard</a>
          <a href="#/profile" class="${location.hash === '#/profile' ? 'active' : ''}">Profile</a>
          ${isPatient ? `<a href="#/providers" class="${location.hash === '#/providers' ? 'active' : ''}">Find Doctor</a>` : ''}
          ${(isPatient || isDoctor || isAdmin) ? `<a href="#/appointments" class="${location.hash === '#/appointments' ? 'active' : ''}">Appointments</a>` : ''}
          ${isPatient ? `<a href="#/medical-records" class="${location.hash === '#/medical-records' ? 'active' : ''}">Records</a>` : ''}
          ${(isPatient || isDoctor || isAdmin) ? `<a href="#/consultations" class="${location.hash === '#/consultations' ? 'active' : ''}">Consultations</a>` : ''}
          ${(isPatient || isAdmin) ? `<a href="#/insurance" class="${location.hash === '#/insurance' ? 'active' : ''}">Insurance</a>` : ''}
          ${(isPatient || isAdmin) ? `<a href="#/subscriptions" class="${location.hash === '#/subscriptions' ? 'active' : ''}">Plans</a>` : ''}
          ${isAdmin ? `<a href="#/admin-users" class="${location.hash === '#/admin-users' ? 'active' : ''}">Users</a>` : ''}
          ${isAdmin ? `<a href="#/notifications" class="${location.hash === '#/notifications' ? 'active' : ''}">Templates</a>` : ''}
          ${isAdmin ? `<a href="#/audit" class="${location.hash === '#/audit' ? 'active' : ''}">Audit</a>` : ''}
          <a href="#" id="logoutBtn" style="color: #ef4444; font-weight: 600;">Logout</a>
        </div>
      </div>
    </nav>
  `;
};
