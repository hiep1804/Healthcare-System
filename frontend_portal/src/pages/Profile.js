import { Navbar } from '../components/Navbar.js';
import { AuthAPI, PatientAPI, ProviderAPI, getUser, getErrorMessage } from '../api.js';

export const ProfilePage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">👤 Hồ sơ Cá nhân & Tài khoản</h1>
        <p class="text-muted">Quản lý thông tin tài khoản cá nhân, thông tin liên hệ và xem bằng cấp chứng chỉ chuyên môn.</p>
      </div>

      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h2 style="font-size: 1.4rem; color: var(--primary-blue); margin-bottom: 1rem;">Thông tin Cá nhân & Liên hệ</h2>
        <div id="profileError" style="margin-bottom: 1rem;"></div>
        <form id="profileForm" style="display: none;">
          <div id="dynamicFields"></div>
          
          <button type="submit" class="btn btn-primary" style="margin-top: 1rem; font-weight: 600;">
            💾 Lưu Thay đổi Hồ sơ
          </button>
        </form>
        <div id="loadingIndicator" style="text-align: center; color: var(--text-muted);">
          Đang tải dữ liệu hồ sơ...
        </div>
      </div>

      <!-- DOCTOR LICENSE SECTION (READ-ONLY FOR DOCTOR, UPLOADED BY ADMIN) -->
      <div id="doctorLicenseSection" style="display: none;">
        <div class="glass-panel" style="padding: 2rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 0.5rem;">Bằng cấp & Chứng chỉ Hành nghề Bác sĩ</h2>
          <p class="text-muted" style="margin-bottom: 1rem; font-size: 0.9rem;">
            ℹ️ <em>Thông tin chứng chỉ chuyên môn do Quản trị viên (Admin) thẩm định và tải lên hệ thống.</em>
          </p>
          <div id="doctorLicensesList">Đang tải danh sách chứng chỉ...</div>
        </div>
      </div>
    </div>
  `;
};

export const attachProfileListeners = async () => {
  const user = getUser();
  if (!user) return;

  const form = document.getElementById('profileForm');
  const fieldsContainer = document.getElementById('dynamicFields');
  const errorDiv = document.getElementById('profileError');
  const loading = document.getElementById('loadingIndicator');

  if (!form || !fieldsContainer) return;

  const showError = (msg) => {
    errorDiv.innerHTML = `<div class="alert alert-error">${msg}</div>`;
  };
  const showSuccess = (msg) => {
    errorDiv.innerHTML = `<div class="alert alert-success">${msg}</div>`;
  };

  try {
    let profileData = null;
    let authData = await AuthAPI.getMe().catch(() => ({}));

    let fieldsHTML = '';

    if (user.role === 'ADMIN') {
      fieldsHTML = `
        <div class="form-group">
          <label class="form-label">Email tài khoản</label>
          <input type="text" class="form-input" value="${authData.email || ''}" disabled />
        </div>
        <div class="form-group">
          <label class="form-label">Tên đăng nhập</label>
          <input type="text" class="form-input" value="${authData.username || ''}" disabled />
        </div>
        <div class="form-group">
          <label class="form-label">Số điện thoại</label>
          <input type="text" class="form-input" id="phoneInput" value="${authData.phone || ''}" />
        </div>
      `;
    } else if (user.role === 'PATIENT') {
      profileData = await PatientAPI.getMe();
      if (!profileData) {
        showError('Không tìm thấy hồ sơ Bệnh nhân.');
        loading.style.display = 'none';
        return;
      }

      fieldsHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Tên</label>
            <input type="text" class="form-input" id="firstNameInput" value="${profileData.first_name || ''}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Họ & Tên đệm</label>
            <input type="text" class="form-input" id="lastNameInput" value="${profileData.last_name || ''}" required />
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Ngày sinh</label>
            <input type="date" class="form-input" id="dobInput" value="${profileData.date_of_birth || ''}" />
          </div>
          <div class="form-group">
            <label class="form-label">Giới tính</label>
            <select class="form-input" id="genderInput">
              <option value="M" ${profileData.gender === 'M' ? 'selected' : ''}>Nam</option>
              <option value="F" ${profileData.gender === 'F' ? 'selected' : ''}>Nữ</option>
              <option value="O" ${profileData.gender === 'O' ? 'selected' : ''}>Khác</option>
            </select>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Số điện thoại liên hệ</label>
            <input type="text" class="form-input" id="contactNumberInput" value="${profileData.contact_number || profileData.phone || ''}" />
          </div>
          <div class="form-group">
            <label class="form-label">Số điện thoại khẩn cấp</label>
            <input type="text" class="form-input" id="emergencyContactInput" value="${profileData.emergency_contact || ''}" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Địa chỉ thường trú</label>
          <input type="text" class="form-input" id="addressInput" value="${profileData.address || ''}" />
        </div>
      `;
    } else if (user.role === 'DOCTOR') {
      profileData = await ProviderAPI.getMe();
      const docLicSection = document.getElementById('doctorLicenseSection');
      if (docLicSection) docLicSection.style.display = 'block';

      if (profileData) {
        loadDoctorLicenses(profileData.id);
        fieldsHTML = `
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Tên Bác sĩ</label>
              <input type="text" class="form-input" id="firstNameInput" value="${profileData.first_name || ''}" required />
            </div>
            <div class="form-group">
              <label class="form-label">Họ Bác sĩ</label>
              <input type="text" class="form-input" id="lastNameInput" value="${profileData.last_name || ''}" required />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Giới thiệu bản thân & Kinh nghiệm (Bio)</label>
            <textarea class="form-input" id="bioInput" rows="3">${profileData.bio || ''}</textarea>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Tỉnh / Thành phố hoạt động</label>
              <input type="text" class="form-input" id="locationInput" value="${profileData.location || ''}" />
            </div>
            <div class="form-group">
              <label class="form-label">Chuyên khoa</label>
              <input type="text" class="form-input" value="${profileData.specialty_detail ? profileData.specialty_detail.name : 'Đa khoa'}" disabled />
            </div>
          </div>
        `;
      } else {
        fieldsHTML = `<div class="alert alert-info">Chưa có thông tin hồ sơ Bác sĩ.</div>`;
      }
    }

    fieldsContainer.innerHTML = fieldsHTML;
    loading.style.display = 'none';
    form.style.display = 'block';

    // Submit handler
    form.onsubmit = async (e) => {
      e.preventDefault();
      errorDiv.innerHTML = '';

      try {
        if (user.role === 'ADMIN') {
          const phone = document.getElementById('phoneInput').value;
          await AuthAPI.updateMe({ phone });
          showSuccess('Cập nhật thông tin cá nhân thành công!');
        } else if (user.role === 'PATIENT') {
          const payload = {
            first_name: document.getElementById('firstNameInput').value,
            last_name: document.getElementById('lastNameInput').value,
            date_of_birth: document.getElementById('dobInput').value || null,
            gender: document.getElementById('genderInput').value,
            contact_number: document.getElementById('contactNumberInput').value,
            emergency_contact: document.getElementById('emergencyContactInput').value,
            address: document.getElementById('addressInput').value,
          };
          await PatientAPI.updateMe(payload);
          showSuccess('Cập nhật thông tin bệnh nhân thành công!');
        } else if (user.role === 'DOCTOR') {
          if (!profileData) return;
          const payload = {
            first_name: document.getElementById('firstNameInput').value,
            last_name: document.getElementById('lastNameInput').value,
            bio: document.getElementById('bioInput').value,
            location: document.getElementById('locationInput').value,
          };
          await ProviderAPI.updateMe(payload);
          showSuccess('Cập nhật hồ sơ Bác sĩ thành công!');
        }
      } catch (err) {
        showError(getErrorMessage(err, 'Lỗi cập nhật thông tin hồ sơ.'));
      }
    };

  } catch (err) {
    loading.style.display = 'none';
    showError(getErrorMessage(err, 'Lỗi tải thông tin hồ sơ.'));
  }
};

// Helper: Load Doctor Licenses
const loadDoctorLicenses = async (providerId) => {
  const container = document.getElementById('doctorLicensesList');
  if (!container) return;

  try {
    const data = await ProviderAPI.getLicenses(providerId);
    const licenses = data.results || data || [];

    if (licenses.length === 0) {
      container.innerHTML = '<p class="text-muted">Chưa có chứng chỉ hành nghề nào được tải lên.</p>';
      return;
    }

    container.innerHTML = `
      <div style="display: grid; gap: 1rem;">
        ${licenses.map(lic => `
          <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <strong style="color: var(--primary-blue);">Mã CCHN: ${lic.license_number || 'N/A'}</strong>
              <span class="badge ${lic.status === 'VERIFIED' ? 'badge-success' : 'badge-warning'}">
                ${lic.status === 'VERIFIED' ? 'Đã thẩm định' : 'Đang duyệt'}
              </span>
            </div>
            <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Ngày cấp:</strong> ${lic.issue_date || 'N/A'}</p>
            ${lic.license_file_url ? `
              <p style="margin-bottom: 0;">
                <a href="${lic.license_file_url}" target="_blank" style="color: var(--primary-blue);">🔗 Xem File minh chứng CCHN</a>
              </p>
            ` : ''}
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    container.innerHTML = '<p class="text-muted">Chưa có chứng chỉ hành nghề được tải lên.</p>';
  }
};
