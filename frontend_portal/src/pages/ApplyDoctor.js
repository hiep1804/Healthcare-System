import { Navbar } from '../components/Navbar.js';
import { ProviderAPI, getUser, getErrorMessage } from '../api.js';

export const ApplyDoctorPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">🩺 Đăng ký trở thành Bác sĩ</h1>
        <p class="text-muted">Nộp hồ sơ thông tin chuyên môn và minh chứng (Chứng chỉ hành nghề - CCHN) để Quản trị viên (Admin) thẩm định & duyệt tài khoản Bác sĩ.</p>
      </div>

      <div id="doctorApplyStatus"></div>

      <div class="glass-panel" id="doctorApplyFormContainer" style="padding: 2rem;">
        <h2 style="font-size: 1.4rem; color: var(--primary-blue); margin-bottom: 1rem;">Đơn Đăng ký & Nộp Minh chứng Chuyên môn</h2>
        
        <form id="doctorApplyForm">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Tên Bác sĩ</label>
              <input type="text" id="applyFirstName" class="form-input" required placeholder="Nguyễn" />
            </div>
            <div class="form-group">
              <label class="form-label">Họ Bác sĩ</label>
              <input type="text" id="applyLastName" class="form-input" required placeholder="Văn A" />
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Giới thiệu bản thân & Kinh nghiệm chuyên môn (Bio)</label>
              <input type="text" id="applyBio" class="form-input" required placeholder="Ví dụ: Bác sĩ CK1 Chuyên khoa Tim mạch 10 năm kinh nghiệm" />
            </div>
            <div class="form-group">
              <label class="form-label">Vùng / Tỉnh thành hoạt động</label>
              <input type="text" id="applyLocation" class="form-input" required placeholder="TP. Hồ Chí Minh" />
            </div>
          </div>

          <hr style="border-color: rgba(255,255,255,0.1); margin: 1.5rem 0;" />

          <h3 style="font-size: 1.2rem; color: var(--primary-blue); margin-bottom: 1rem;">📜 Minh chứng Chuyên môn & CCHN</h3>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Số CCHN / Mã chứng chỉ hành nghề</label>
              <input type="text" id="applyLicenseNum" class="form-input" required placeholder="Ví dụ: CCHN-12345/BYT" />
            </div>
            <div class="form-group">
              <label class="form-label">Ngày cấp chứng chỉ</label>
              <input type="date" id="applyLicenseIssue" class="form-input" required />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Link File / Ảnh chụp Minh chứng CCHN</label>
            <input type="text" id="applyLicenseUrl" class="form-input" required placeholder="http://... link đính kèm file/ảnh chứng chỉ" />
          </div>

          <button type="submit" class="btn btn-primary" style="margin-top: 1rem; width: 100%;">
            Gửi Đơn Đăng ký & Minh chứng cho Admin
          </button>
        </form>
      </div>
    </div>
  `;
};

export const attachApplyDoctorListeners = async () => {
  const user = getUser();
  if (!user) return;

  const statusDiv = document.getElementById('doctorApplyStatus');
  const formContainer = document.getElementById('doctorApplyFormContainer');
  const form = document.getElementById('doctorApplyForm');

  if (!statusDiv || !formContainer) return;

  const loadStatus = async () => {
    try {
      const existing = await ProviderAPI.getMe();
      if (existing && existing.id) {
        let statusBadge = '<span class="badge badge-warning">⏳ Đang chờ Admin xét duyệt hồ sơ & minh chứng</span>';
        if (existing.status === 'VERIFIED') {
          statusBadge = '<span class="badge badge-success">✓ Đã được phê duyệt làm Bác sĩ</span>';
        } else if (existing.status === 'REJECTED') {
          statusBadge = '<span class="badge badge-error">✕ Yêu cầu đăng ký đã bị Từ chối</span>';
        }

        statusDiv.innerHTML = `
          <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
              <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Trạng thái Đơn Đăng ký làm Bác sĩ</h2>
              ${statusBadge}
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px;">
              <p style="margin: 0.3rem 0; font-size: 0.95rem;"><strong>Họ và tên Bác sĩ:</strong> ${existing.first_name || ''} ${existing.last_name || ''}</p>
              <p style="margin: 0.3rem 0; font-size: 0.95rem;"><strong>Bio:</strong> ${existing.bio || 'Chưa có'}</p>
              <p style="margin: 0.3rem 0; font-size: 0.95rem;"><strong>Khu vực hoạt động:</strong> ${existing.location || 'N/A'}</p>
              <p style="margin: 0.3rem 0; font-size: 0.95rem;"><strong>Mã Bác sĩ (ID):</strong> ${existing.id}</p>
            </div>
          </div>
        `;

        if (existing.status === 'VERIFIED') {
          formContainer.style.display = 'none';
          return;
        }
      }
    } catch (e) {}
  };

  await loadStatus();

  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const origText = btn.textContent;
      btn.textContent = 'Đang nộp hồ sơ...';
      btn.disabled = true;

      try {
        const prov = await ProviderAPI.createProfile({
          user_id: user.id,
          first_name: document.getElementById('applyFirstName').value,
          last_name: document.getElementById('applyLastName').value,
          bio: document.getElementById('applyBio').value,
          location: document.getElementById('applyLocation').value
        });

        await ProviderAPI.uploadLicense(prov.id, {
          license_number: document.getElementById('applyLicenseNum').value,
          issue_date: document.getElementById('applyLicenseIssue').value,
          document_url: document.getElementById('applyLicenseUrl').value
        });

        alert('Gửi đơn đăng ký làm Bác sĩ và nộp minh chứng CCHN thành công! Vui lòng chờ Quản trị viên (Admin) phê duyệt.');
        await loadStatus();
      } catch (err) {
        alert(getErrorMessage(err, 'Lỗi nộp đơn đăng ký bác sĩ.'));
      } finally {
        btn.textContent = origText;
        btn.disabled = false;
      }
    };
  }
};
