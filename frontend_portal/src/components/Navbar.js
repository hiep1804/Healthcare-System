import { getUser } from '../api.js';

/* ── SVG Icon helpers ── */
const icons = {
  dashboard: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  profile: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
  providers: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`,
  appointments: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  consultations: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  records: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
  subscription: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>`,
  insurance: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  users: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  notifications: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`,
  audit: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
  history: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  schedule: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/></svg>`,
  apply: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>`,
  logout: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
  chevron: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>`,
  login: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>`,
};

const isActive = (hash) => location.hash === hash ? 'active' : '';

/* ── Build a nav link HTML ── */
const navLink = (href, icon, label, activeHash) => {
  return `<a href="${href}" class="nav-dropdown-item ${isActive(activeHash || href)}">${icon}<span>${label}</span></a>`;
};

/* ── Build a dropdown group ── */
const dropdown = (id, label, icon, items) => {
  const hasActiveChild = items.some(i => location.hash === i.href);
  return `
    <div class="nav-dropdown" id="${id}">
      <button class="nav-dropdown-trigger ${hasActiveChild ? 'active' : ''}" data-dropdown="${id}">
        ${icon}<span>${label}</span>${icons.chevron}
      </button>
      <div class="nav-dropdown-menu">
        ${items.map(i => navLink(i.href, i.icon, i.label)).join('')}
      </div>
    </div>
  `;
};

export const Navbar = () => {
  const user = getUser();

  if (!user) {
    return `
      <nav class="navbar glass-panel" id="mainNavbar">
        <div class="container">
          <a href="#/" class="logo">
            <span class="logo-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </span>
            Health<span>Care</span>
          </a>
          <div class="nav-actions">
            <a href="#/login" class="nav-btn nav-btn-login">${icons.login}<span>Đăng nhập</span></a>
          </div>
        </div>
      </nav>
    `;
  }

  const isPatient = user.role === 'PATIENT';
  const isDoctor = user.role === 'DOCTOR';
  const isAdmin = user.role === 'ADMIN';

  const roleLabel = isPatient ? 'Bệnh nhân' : isDoctor ? 'Bác sĩ' : 'Quản trị viên';
  const roleColor = isPatient ? '#10b981' : isDoctor ? '#3b82f6' : '#f59e0b';
  const userInitial = (user.last_name || user.email || 'U')[0].toUpperCase();

  /* ── Build menu items based on role ── */

  // Direct top-level links
  const topLinks = [
    { href: '#/', icon: icons.dashboard, label: 'Bảng điều khiển' },
  ];

  // "Khám bệnh" dropdown group
  const khamBenhItems = [];
  if (isPatient) {
    khamBenhItems.push({ href: '#/providers', icon: icons.providers, label: 'Tìm Bác sĩ' });
    khamBenhItems.push({ href: '#/appointments', icon: icons.appointments, label: 'Lịch hẹn khám' });
    khamBenhItems.push({ href: '#/consultations', icon: icons.consultations, label: 'Tư vấn & Khám' });
    khamBenhItems.push({ href: '#/medical-records', icon: icons.records, label: 'Vitals & Kết quả' });
  }
  if (isDoctor) {
    khamBenhItems.push({ href: '#/appointments', icon: icons.appointments, label: 'Quản lý Lịch hẹn' });
    khamBenhItems.push({ href: '#/consultations', icon: icons.consultations, label: 'Tư vấn & Khám' });
    khamBenhItems.push({ href: '#/patient-history', icon: icons.history, label: 'Lịch sử bệnh nhân' });
    khamBenhItems.push({ href: '#/doctor-schedule', icon: icons.schedule, label: 'Ca làm việc' });
  }
  if (isAdmin) {
    khamBenhItems.push({ href: '#/providers', icon: icons.providers, label: 'Duyệt Bác sĩ' });
  }

  // "Dịch vụ" dropdown group (for patient/admin)
  const dichVuItems = [];
  if (isPatient) {
    dichVuItems.push({ href: '#/subscriptions', icon: icons.subscription, label: 'Gói dịch vụ của tôi' });
    dichVuItems.push({ href: '#/apply-doctor', icon: icons.apply, label: 'Đăng ký Bác sĩ' });
  }
  if (isAdmin) {
    dichVuItems.push({ href: '#/subscriptions', icon: icons.subscription, label: 'Quản lý Gói dịch vụ' });
    dichVuItems.push({ href: '#/insurance', icon: icons.insurance, label: 'Bảo hiểm y tế' });
  }

  // "Hệ thống" dropdown group (admin only)
  const heThongItems = [];
  if (isAdmin) {
    heThongItems.push({ href: '#/admin-users', icon: icons.users, label: 'Tài khoản User' });
    heThongItems.push({ href: '#/notifications', icon: icons.notifications, label: 'Mẫu thông báo' });
    heThongItems.push({ href: '#/audit', icon: icons.audit, label: 'Nhật ký hệ thống' });
  }

  return `
    <nav class="navbar glass-panel" id="mainNavbar">
      <div class="container">
        <a href="#/" class="logo">
          <span class="logo-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </span>
          Health<span>Care</span>
        </a>

        <div class="nav-menu" id="navMenu">
          ${topLinks.map(l => `<a href="${l.href}" class="nav-top-link ${isActive(l.href)}">${l.icon}<span>${l.label}</span></a>`).join('')}

          ${khamBenhItems.length > 0 ? dropdown('ddKhamBenh', isDoctor ? 'Khám bệnh' : isAdmin ? 'Y tế' : 'Khám bệnh', icons.consultations, khamBenhItems) : ''}

          ${dichVuItems.length > 0 ? dropdown('ddDichVu', 'Dịch vụ', icons.subscription, dichVuItems) : ''}

          ${heThongItems.length > 0 ? dropdown('ddHeThong', 'Hệ thống', icons.audit, heThongItems) : ''}
        </div>

        <div class="nav-actions">
          <div class="nav-dropdown" id="ddUser">
            <button class="nav-user-trigger" data-dropdown="ddUser">
              <div class="nav-avatar" style="--role-color: ${roleColor}">${userInitial}</div>
              <div class="nav-user-info">
                <span class="nav-user-name">${user.last_name || user.email}</span>
                <span class="nav-user-role" style="color: ${roleColor}">${roleLabel}</span>
              </div>
              ${icons.chevron}
            </button>
            <div class="nav-dropdown-menu nav-dropdown-menu-right">
              ${navLink('#/profile', icons.profile, 'Hồ sơ cá nhân')}
              <div class="nav-dropdown-divider"></div>
              <a href="#" id="logoutBtn" class="nav-dropdown-item nav-logout-item">${icons.logout}<span>Đăng xuất</span></a>
            </div>
          </div>
        </div>
      </div>
    </nav>
  `;
};

/* ── Attach dropdown event listeners ── */
export const attachNavbarListeners = () => {
  // Close all dropdowns
  const closeAll = () => {
    document.querySelectorAll('.nav-dropdown').forEach(d => d.classList.remove('open'));
  };

  // Toggle dropdown on trigger click
  document.querySelectorAll('[data-dropdown]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const parent = trigger.closest('.nav-dropdown');
      const isOpen = parent.classList.contains('open');
      closeAll();
      if (!isOpen) parent.classList.add('open');
    });
  });

  // Close dropdowns when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-dropdown')) {
      closeAll();
    }
  });

  // Close dropdowns when a link is clicked (navigation)
  document.querySelectorAll('.nav-dropdown-item').forEach(item => {
    item.addEventListener('click', () => closeAll());
  });
};
