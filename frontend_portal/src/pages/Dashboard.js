import { Navbar } from '../components/Navbar.js';
import { getUser, PatientAPI, getErrorMessage } from '../api.js';

export const DashboardPage = () => {
  const user = getUser();
  if (!user) return '';

  const isPatient = user.role === 'PATIENT';
  const isDoctor = user.role === 'DOCTOR' || user.role === 'PROVIDER';
  const isAdmin = user.role === 'ADMIN';

  const roleTitle = isPatient ? 'Bệnh nhân' : isDoctor ? 'Bác sĩ' : 'Quản trị viên';

  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Bảng Điều Khiển Hệ Thống Y Tế</h1>
        <p class="text-muted">Xin chào <strong>${user.last_name || user.email}</strong> [${roleTitle}], chúc bạn một ngày làm việc và chăm sóc sức khỏe hiệu quả!</p>
      </div>

      <div class="dashboard-grid">
        ${isPatient ? `
          <div class="stat-card glass-panel" id="patientProfileWidget">
            <h3 style="color: var(--primary-blue);">Hồ sơ Bệnh nhân</h3>
            <div class="value" style="font-size: 1rem; font-weight: normal; margin-top: 10px;" id="profileStatus">Đang tải thông tin...</div>
            <a href="#/profile" class="btn btn-primary btn-sm" style="margin-top: 1rem; width: fit-content; text-decoration: none;">Xem Hồ sơ</a>
          </div>
          <div class="stat-card glass-panel">
            <h3 style="color: var(--primary-blue);">Lịch sử hẹn khám</h3>
            <div class="value">!</div>
            <a href="#/appointments" class="btn btn-primary btn-sm" style="margin-top: 1rem; width: fit-content; text-decoration: none;">Xem Lịch sử Hẹn khám</a>
          </div>
          <div class="stat-card glass-panel">
            <h3 style="color: var(--primary-blue);">Vitals & Kết quả Y tế</h3>
            <div class="value">📊</div>
            <a href="#/medical-records" style="margin-top: 1rem; color: var(--secondary-teal); text-decoration: none; font-weight: 500; display: inline-block;">Xem Chỉ số Vitals &rarr;</a>
          </div>
        ` : ''}

        ${isDoctor ? `
          <div class="stat-card glass-panel">
            <h3 style="color: var(--primary-blue);">Lịch làm việc hôm nay</h3>
            <div class="value">0</div>
            <a href="#/appointments" class="btn btn-primary btn-sm" style="margin-top: 1rem; width: fit-content; text-decoration: none;">Xem Lịch khám</a>
          </div>
          <div class="stat-card glass-panel">
            <h3 style="color: var(--primary-blue);">Phiên khám chờ tư vấn</h3>
            <div class="value">0</div>
            <a href="#/consultations" style="margin-top: 1rem; color: var(--secondary-teal); text-decoration: none; font-weight: 500; display: inline-block;">Đến Phiên khám &rarr;</a>
          </div>
        ` : ''}

        ${isAdmin ? `
          <div class="stat-card glass-panel">
            <h3 style="color: var(--primary-blue);">Yêu cầu Duyệt Bác sĩ</h3>
            <div class="value">!</div>
            <a href="#/providers" class="btn btn-primary btn-sm" style="margin-top: 1rem; width: fit-content; text-decoration: none;">Xem Danh sách Duyệt</a>
          </div>
          <div class="stat-card glass-panel">
            <h3 style="color: var(--primary-blue);">Quản lý Tài khoản</h3>
            <div class="value">User</div>
            <a href="#/admin-users" style="margin-top: 1rem; color: var(--secondary-teal); text-decoration: none; font-weight: 500; display: inline-block;">Xem Người dùng &rarr;</a>
          </div>
        ` : ''}
      </div>
    </div>
  `;
};

export const attachDashboardListeners = async () => {
  const user = getUser();
  if (!user || user.role !== 'PATIENT') return;

  const profileStatus = document.getElementById('profileStatus');

  if (profileStatus) {
    try {
      const profile = await PatientAPI.getMe();
      if (profile && profile.first_name) {
        profileStatus.innerHTML = `Bệnh nhân: <b>${profile.first_name} ${profile.last_name}</b><br>Ngày sinh: ${profile.date_of_birth || 'N/A'}<br>SĐT: ${profile.contact_number || profile.phone || 'N/A'}`;
      } else {
        profileStatus.textContent = "Chưa cập nhật đầy đủ thông tin cá nhân.";
      }
    } catch (e) {
      profileStatus.textContent = "Chưa thiết lập hồ sơ bệnh nhân.";
    }
  }
};
