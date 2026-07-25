import { getUser } from '../api.js';

export const Navbar = () => {
  const user = getUser();
  
  if (!user) {
    return `
      <nav class="navbar glass-panel">
        <div class="container">
          <a href="#/" class="logo">Health<span>Care</span></a>
          <div class="nav-links">
            <a href="#/login">Đăng nhập</a>
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
          <span>${user.last_name || user.email} <strong style="color:var(--primary-blue); font-size: 0.8em;">[${user.role === 'PATIENT' ? 'Bệnh nhân' : user.role === 'DOCTOR' ? 'Bác sĩ' : 'Quản trị viên'}]</strong></span>
          <a href="#/" class="${location.hash === '#/' ? 'active' : ''}">Bảng điều khiển</a>
          <a href="#/profile" class="${location.hash === '#/profile' ? 'active' : ''}">Hồ sơ cá nhân</a>
          ${(isDoctor || isAdmin) ? `<a href="#/patient-history" class="${location.hash === '#/patient-history' ? 'active' : ''}">Lịch sử bệnh nhân</a>` : ''}
          ${isDoctor ? `<a href="#/doctor-schedule" class="${location.hash === '#/doctor-schedule' ? 'active' : ''}">Đăng ký Ca làm việc</a>` : ''}
          ${isPatient ? `<a href="#/apply-doctor" class="${location.hash === '#/apply-doctor' ? 'active' : ''}">Đăng ký Bác sĩ</a>` : ''}
          ${isPatient ? `<a href="#/providers" class="${location.hash === '#/providers' ? 'active' : ''}">Tìm Bác sĩ</a>` : ''}
          ${isAdmin ? `<a href="#/providers" class="${location.hash === '#/providers' ? 'active' : ''}">Duyệt Bác sĩ</a>` : ''}
          ${isDoctor ? `<a href="#/appointments" class="${location.hash === '#/appointments' ? 'active' : ''}">Quản lý Yêu cầu Lịch hẹn</a>` : ''}
          ${isPatient ? `<a href="#/appointments" class="${location.hash === '#/appointments' ? 'active' : ''}">Lịch sử hẹn khám</a>` : ''}
          ${isPatient ? `<a href="#/medical-records" class="${location.hash === '#/medical-records' ? 'active' : ''}">Vitals & Kết quả</a>` : ''}
          ${(isPatient || isDoctor) ? `<a href="#/consultations" class="${location.hash === '#/consultations' ? 'active' : ''}">Tư vấn & Khám</a>` : ''}
          ${isPatient ? `<a href="#/subscriptions" class="${location.hash === '#/subscriptions' ? 'active' : ''}">Gói dịch vụ của tôi</a>` : ''}
          ${isAdmin ? `<a href="#/subscriptions" class="${location.hash === '#/subscriptions' ? 'active' : ''}">Quản lý Gói dịch vụ</a>` : ''}
          ${isAdmin ? `<a href="#/insurance" class="${location.hash === '#/insurance' ? 'active' : ''}">Bảo hiểm y tế</a>` : ''}
          ${isAdmin ? `<a href="#/admin-users" class="${location.hash === '#/admin-users' ? 'active' : ''}">Tài khoản User</a>` : ''}
          ${isAdmin ? `<a href="#/notifications" class="${location.hash === '#/notifications' ? 'active' : ''}">Mẫu thông báo</a>` : ''}
          ${isAdmin ? `<a href="#/audit" class="${location.hash === '#/audit' ? 'active' : ''}">Nhật ký hệ thống</a>` : ''}
          <a href="#" id="logoutBtn" style="color: #ef4444; font-weight: 600;">Đăng xuất</a>
        </div>
      </div>
    </nav>
  `;
};
