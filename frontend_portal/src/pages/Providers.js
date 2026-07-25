import { Navbar } from '../components/Navbar.js';
import { ProviderAPI, AppointmentAPI, PatientAPI, getUser, getErrorMessage } from '../api.js';

export const ProvidersPage = () => {
  const user = getUser();
  const isDoctor = user && user.role === 'DOCTOR';
  const isAdmin = user && user.role === 'ADMIN';

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Danh mục Bác sĩ & Chuyên gia Y tế</h1>
        <p class="text-muted">Tìm kiếm bác sĩ, đặt lịch hẹn khám trực tuyến và quản lý hồ sơ chuyên môn bác sĩ.</p>
      </div>

      <!-- SEARCH BAR -->
      <div class="glass-panel" style="padding: 1.5rem; margin-bottom: 2rem;">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label" style="font-weight: bold; color: var(--primary-blue);">Tìm kiếm Bác sĩ theo Tên</label>
          <input type="text" id="searchDoctorInput" class="form-input" placeholder="Nhập tên bác sĩ (Ví dụ: Nguyễn, Trần, Smith...)" />
        </div>
      </div>

      ${isDoctor ? `
        <!-- DOCTOR SERVICES MANAGEMENT SECTION -->
        <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Dịch vụ khám & Bảng giá của tôi</h2>
            <button id="showAddServiceBtn" class="btn btn-secondary btn-sm">+ Thêm dịch vụ khám mới</button>
          </div>

          <div id="addServiceFormContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <form id="addServiceForm">
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                  <label class="form-label">Tên dịch vụ</label>
                  <input type="text" id="serviceNameInput" class="form-input" required placeholder="Ví dụ: Tư vấn Online 30 phút" />
                </div>
                <div class="form-group">
                  <label class="form-label">Giá dịch vụ (VND)</label>
                  <input type="number" id="servicePriceInput" class="form-input" required placeholder="300000" />
                </div>
                <div class="form-group">
                  <label class="form-label">Thời lượng (Phút)</label>
                  <input type="number" id="serviceDurationInput" class="form-input" value="30" required />
                </div>
              </div>
              <button type="submit" class="btn btn-primary btn-sm">Tạo dịch vụ</button>
              <button type="button" id="cancelAddServiceBtn" class="btn btn-secondary btn-sm">Hủy</button>
            </form>
          </div>

          <div id="myServicesList">Đang tải danh sách dịch vụ...</div>
        </div>
      ` : ''}

      ${isAdmin ? `
        <!-- ADMIN PENDING DOCTOR APPLICATIONS SECTION -->
        <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">📋 Yêu cầu Đăng ký làm Bác sĩ (Chờ Admin duyệt)</h2>
          <div id="pendingApplicationsList">Đang tải yêu cầu đăng ký...</div>
        </div>
      ` : ''}

      <!-- SEARCH / LIST SECTION -->
      <div id="providerList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Đang tải danh sách bác sĩ...
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div id="bookingModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center;">
      <div class="glass-panel" style="background: white; padding: 2rem; max-width: 500px; width: 90%; border-radius: 12px; position: relative; color: var(--text-main);">
        <button id="closeModalBtn" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
        <h2 style="color: var(--primary-blue); margin-bottom: 1rem;">Đặt Lịch Hẹn Khám</h2>
        <div id="modalContent">
          <p>Vui lòng chọn khung giờ khám khả dụng:</p>
          <div id="slotsContainer" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 1rem; max-height: 200px; overflow-y: auto;">
            Đang tải các khung giờ khám...
          </div>
          <div id="bookingError" class="alert alert-error" style="display: none; margin-top: 1rem;"></div>
          <button id="confirmBookBtn" class="btn btn-primary" style="width: 100%; margin-top: 1.5rem;" disabled>Xác Nhận Đặt Lịch</button>
        </div>
      </div>
    </div>

    <!-- Admin License Upload Modal -->
    <div id="addLicenseModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center;">
      <div class="glass-panel" style="background: white; padding: 2rem; max-width: 500px; width: 90%; border-radius: 12px; position: relative; color: var(--text-main);">
        <button id="closeLicenseModalBtn" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
        <h2 style="color: var(--primary-blue); margin-bottom: 1rem;">Thêm Chứng chỉ Hành nghề Bác sĩ (Admin)</h2>
        <form id="adminLicenseForm">
          <div class="form-group">
            <label class="form-label">Số CCHN / Mã chứng chỉ</label>
            <input type="text" id="adminLicenseNum" class="form-input" required placeholder="Ví dụ: CCHN-12345/BYT" />
          </div>
          <div class="form-group">
            <label class="form-label">Ngày cấp</label>
            <input type="date" id="adminLicenseIssue" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Link file / Hình ảnh minh chứng</label>
            <input type="text" id="adminLicenseUrl" class="form-input" placeholder="http://... link tài liệu chứng chỉ" />
          </div>
          <div id="licenseSubmitError" class="alert alert-error" style="display: none; margin-top: 1rem;"></div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Lưu & Cấp chứng chỉ</button>
        </form>
      </div>
    </div>
  `;
};

export const attachProvidersListeners = async () => {
  const providerList = document.getElementById('providerList');
  const searchInput = document.getElementById('searchDoctorInput');
  if (!providerList) return;

  const user = getUser();
  const isDoctor = user && user.role === 'DOCTOR';
  const isAdmin = user && user.role === 'ADMIN';
  let allProviders = [];

  // Doctor Services logic
  if (isDoctor) {
    try {
      const myProfile = await ProviderAPI.getMe();
      if (myProfile) {
        const renderMyServices = async () => {
          const container = document.getElementById('myServicesList');
          try {
            const data = await ProviderAPI.getServices(myProfile.id);
            const services = data.results || data || [];
            if (services.length === 0) {
              container.innerHTML = '<p class="text-muted">Chưa tạo dịch vụ nào.</p>';
            } else {
              container.innerHTML = services.map(s => `
                <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                  <div>
                    <strong>${s.service_name}</strong> - ${Number(s.price).toLocaleString()} VND (${s.duration_minutes} phút)
                  </div>
                </div>
              `).join('');
            }
          } catch (e) {
            container.innerHTML = '<p class="text-muted">Không thể tải dịch vụ.</p>';
          }
        };
        renderMyServices();

        document.getElementById('showAddServiceBtn').onclick = () => {
          document.getElementById('addServiceFormContainer').style.display = 'block';
        };
        document.getElementById('cancelAddServiceBtn').onclick = () => {
          document.getElementById('addServiceFormContainer').style.display = 'none';
        };
        document.getElementById('addServiceForm').onsubmit = async (e) => {
          e.preventDefault();
          try {
            await ProviderAPI.createService(myProfile.id, {
              service_name: document.getElementById('serviceNameInput').value,
              price: document.getElementById('servicePriceInput').value,
              duration_minutes: document.getElementById('serviceDurationInput').value
            });
            document.getElementById('addServiceFormContainer').style.display = 'none';
            renderMyServices();
          } catch (err) {
            alert(getErrorMessage(err, 'Lỗi tạo dịch vụ'));
          }
        };
      }
    } catch (e) {}
  }

  // Render Provider Cards helper
  const renderProviderCards = (providers) => {
    if (providers.length === 0) {
      providerList.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Không tìm thấy bác sĩ phù hợp với từ khóa tìm kiếm.</div>`;
      return;
    }

    providerList.innerHTML = providers.map(p => `
      <div class="stat-card glass-panel" style="align-items: flex-start;">
        <div style="display: flex; justify-content: space-between; width: 100%;">
          <h3 style="color: var(--primary-blue); font-size: 1.1rem;">Bác sĩ: ${p.first_name} ${p.last_name}</h3>
          ${p.status === 'VERIFIED' ? '<span class="badge badge-success">Đã xác thực</span>' : '<span class="badge badge-warning">Chờ xác thực</span>'}
        </div>
        <p style="margin-bottom: 0.5rem;"><strong>Chuyên khoa:</strong> ${p.specialty_name || p.specialty || 'Nội tổng quát'}</p>
        <p style="margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--text-muted);">Phòng khám: ${p.clinic_name || 'N/A'}</p>
        <p style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-muted);">${p.bio || ''}</p>
        
        <div style="display: flex; gap: 0.5rem; width: 100%;">
          ${!isDoctor && !isAdmin ? `
            <button class="btn btn-primary book-btn" style="flex: 1;" data-id="${p.id}">Đặt lịch khám</button>
          ` : ''}
          ${isAdmin ? `
            <div style="display: flex; gap: 0.5rem; width: 100%;">
              <button class="btn btn-secondary add-license-btn btn-sm" style="flex: 1;" data-id="${p.id}">+ Thêm CCHN</button>
              <button class="btn btn-primary verify-btn btn-sm" style="flex: 1;" data-id="${p.id}">Xác thực Bác sĩ</button>
            </div>
          ` : ''}
        </div>
      </div>
    `).join('');

    // Attach listeners
    if (isAdmin) {
      const pendingList = document.getElementById('pendingApplicationsList');
      const loadPendingApplications = async () => {
        if (!pendingList) return;
        try {
          const res = await ProviderAPI.getProviders('status=PENDING_VERIFICATION');
          const list = res.data || res.results || res || [];

          if (!Array.isArray(list) || list.length === 0) {
            pendingList.innerHTML = '<p class="text-muted" style="margin: 0;">Hiện không có đơn đăng ký làm Bác sĩ nào đang chờ duyệt.</p>';
            return;
          }

          const cardsHTML = await Promise.all(list.map(async p => {
            let licensesHTML = '<p class="text-muted" style="font-size: 0.85rem; margin: 0.2rem 0;">Chưa nộp minh chứng CCHN</p>';
            try {
              const lRes = await ProviderAPI.getLicenses(p.id);
              const licenses = lRes.data || lRes.results || lRes || [];
              if (Array.isArray(licenses) && licenses.length > 0) {
                licensesHTML = licenses.map(l => `
                  <div style="background: rgba(255,255,255,0.05); padding: 0.5rem 0.8rem; border-radius: 6px; margin-top: 0.4rem; font-size: 0.85rem;">
                    <strong>Số CCHN:</strong> ${l.license_number || 'N/A'} - <strong>Ngày cấp:</strong> ${l.issue_date || 'N/A'}<br/>
                    ${l.document_url ? `<strong>File minh chứng:</strong> <a href="${l.document_url}" target="_blank" style="color: var(--primary-blue); text-decoration: underline;">Xem file/ảnh minh chứng</a>` : ''}
                  </div>
                `).join('');
              }
            } catch (e) {}

            return `
              <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                  <div>
                    <h3 style="margin: 0; color: var(--primary-blue); font-size: 1.1rem;">Bác sĩ: ${p.first_name || ''} ${p.last_name || ''}</h3>
                    <p style="margin: 0.2rem 0; font-size: 0.85rem;" class="text-muted">User ID: ${p.user_id}</p>
                  </div>
                  <span class="badge badge-warning">PENDING_VERIFICATION</span>
                </div>
                <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Bio:</strong> ${p.bio || 'Chưa cập nhật'}</p>
                <p style="margin-bottom: 0.5rem; font-size: 0.9rem;"><strong>Khu vực:</strong> ${p.location || 'N/A'}</p>
                
                <div style="margin-bottom: 1rem;">
                  <strong style="font-size: 0.9rem;">Minh chứng chuyên môn nộp kèm:</strong>
                  ${licensesHTML}
                </div>

                <div style="display: flex; gap: 0.5rem;">
                  <button class="btn btn-primary btn-sm approve-doctor-btn" data-id="${p.id}" data-user-id="${p.user_id}" style="background: #10b981;">✓ Đồng ý / Phê duyệt Bác sĩ</button>
                  <button class="btn btn-secondary btn-sm reject-doctor-btn" data-id="${p.id}" style="background: #fee2e2; color: #dc2626; border-color: #fca5a5;">✕ Hủy bỏ / Từ chối</button>
                </div>
              </div>
            `;
          }));

          pendingList.innerHTML = cardsHTML.join('');

          document.querySelectorAll('.approve-doctor-btn').forEach(btn => {
            btn.onclick = async (e) => {
              const providerId = e.currentTarget.dataset.id;
              const userId = e.currentTarget.dataset.userId;
              if (confirm('Phê duyệt ứng viên này làm Bác sĩ chính thức?')) {
                try {
                  await ProviderAPI.verifyProvider(providerId, 'VERIFIED', 'Verified by Admin');
                  try {
                    await AuthAPI.assignRole(userId, 'DOCTOR');
                  } catch (rErr) {}
                  alert('Đã phê duyệt Bác sĩ thành công!');
                  loadPendingApplications();
                  loadProviders();
                } catch (err) {
                  alert(getErrorMessage(err, 'Lỗi phê duyệt bác sĩ.'));
                }
              }
            };
          });

          document.querySelectorAll('.reject-doctor-btn').forEach(btn => {
            btn.onclick = async (e) => {
              const providerId = e.currentTarget.dataset.id;
              if (confirm('Hủy bỏ / Từ chối đơn đăng ký làm Bác sĩ này?')) {
                try {
                  await ProviderAPI.verifyProvider(providerId, 'REJECTED', 'Rejected by Admin');
                  alert('Đã từ chối đơn đăng ký.');
                  loadPendingApplications();
                } catch (err) {
                  alert(getErrorMessage(err, 'Lỗi từ chối đơn đăng ký.'));
                }
              }
            };
          });

        } catch (err) {
          pendingList.innerHTML = '<p class="text-muted">Không thể tải đơn đăng ký.</p>';
        }
      };
      loadPendingApplications();

      const licenseModal = document.getElementById('addLicenseModal');
      const closeLicenseModalBtn = document.getElementById('closeLicenseModalBtn');
      const adminLicenseForm = document.getElementById('adminLicenseForm');
      const licenseSubmitError = document.getElementById('licenseSubmitError');
      let selectedProviderForLicense = null;

      if (closeLicenseModalBtn) closeLicenseModalBtn.onclick = () => licenseModal.style.display = 'none';

      document.querySelectorAll('.add-license-btn').forEach(btn => {
        btn.onclick = (e) => {
          selectedProviderForLicense = e.target.getAttribute('data-id');
          if (licenseSubmitError) licenseSubmitError.style.display = 'none';
          if (adminLicenseForm) adminLicenseForm.reset();
          if (licenseModal) licenseModal.style.display = 'flex';
        };
      });

      if (adminLicenseForm) {
        adminLicenseForm.onsubmit = async (e) => {
          e.preventDefault();
          if (!selectedProviderForLicense) return;
          if (licenseSubmitError) licenseSubmitError.style.display = 'none';

          try {
            await ProviderAPI.uploadLicense(selectedProviderForLicense, {
              license_number: document.getElementById('adminLicenseNum').value,
              issue_date: document.getElementById('adminLicenseIssue').value,
              document_url: document.getElementById('adminLicenseUrl').value
            });
            alert('Đã thêm chứng chỉ cho Bác sĩ thành công!');
            if (licenseModal) licenseModal.style.display = 'none';
          } catch (err) {
            if (licenseSubmitError) {
              licenseSubmitError.textContent = getErrorMessage(err, 'Lỗi tải lên chứng chỉ.');
              licenseSubmitError.style.display = 'block';
            }
          }
        };
      }

      document.querySelectorAll('.verify-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const pid = e.target.getAttribute('data-id');
          if (confirm('Verify doctor credentials?')) {
            try {
              await ProviderAPI.verifyProvider(pid, 'VERIFIED', 'Verified by Admin');
              alert('Doctor verified successfully!');
              loadProviders();
            } catch (err) {
              alert(getErrorMessage(err, 'Verification failed.'));
            }
          }
        };
      });
    }

    document.querySelectorAll('.book-btn').forEach(btn => {
      btn.onclick = async (e) => {
        const providerId = e.target.getAttribute('data-id');
        currentProvider = providerId;
        selectedSlot = null;
        confirmBookBtn.disabled = true;
        bookingError.style.display = 'none';
        modal.style.display = 'flex';
        slotsContainer.innerHTML = 'Loading slots...';

        try {
          const slotsData = await AppointmentAPI.getProviderSlots(providerId);
          const rawSlots = slotsData.data || slotsData || [];
          const now = new Date();
          const year = now.getFullYear();
          const month = String(now.getMonth() + 1).padStart(2, '0');
          const day = String(now.getDate()).padStart(2, '0');
          const todayStr = `${year}-${month}-${day}`;

          const hours = String(now.getHours()).padStart(2, '0');
          const minutes = String(now.getMinutes()).padStart(2, '0');
          const seconds = String(now.getSeconds()).padStart(2, '0');
          const currentTimeStr = `${hours}:${minutes}:${seconds}`;

          const slots = (Array.isArray(rawSlots) ? rawSlots : []).filter(s => {
            if (!s.date) return false;
            if (s.date > todayStr) return true;
            if (s.date === todayStr) {
              const startTime = (s.start_time || '').length === 5 ? `${s.start_time}:00` : (s.start_time || '');
              return startTime > currentTimeStr;
            }
            return false;
          });

          if (slots.length === 0) {
            slotsContainer.innerHTML = '<div style="grid-column: 1/-1; color: var(--text-muted); padding: 1rem; text-align: center;">Bác sĩ chưa có lịch hợp lệ</div>';
            return;
          }

          slotsContainer.innerHTML = slots.map(s => `
            <button class="btn slot-btn" style="background: var(--bg-light); color: var(--text-main); border: 1px solid #ccc; padding: 0.5rem;" data-slot-id="${s.id}">
              ${s.date ? s.date + ' ' : ''}${s.start_time ? s.start_time.substring(0,5) : 'Slot'} - ${s.end_time ? s.end_time.substring(0,5) : ''}
            </button>
          `).join('');

          document.querySelectorAll('.slot-btn').forEach(sBtn => {
            sBtn.onclick = (ev) => {
              document.querySelectorAll('.slot-btn').forEach(b => b.style.borderColor = '#ccc');
              ev.currentTarget.style.borderColor = 'var(--primary-blue)';
              selectedSlot = ev.currentTarget.getAttribute('data-slot-id');
              confirmBookBtn.disabled = false;
            };
          });

        } catch (err) {
          const msg = getErrorMessage(err, 'Failed to load slots.');
          slotsContainer.innerHTML = `<div style="color: red; grid-column: 1/-1; padding: 0.5rem;">Lỗi tải khung giờ: ${msg}</div>`;
        }
      };
    });
  };

  // Load Providers
  let currentProvider = null;
  let selectedSlot = null;
  const modal = document.getElementById('bookingModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const slotsContainer = document.getElementById('slotsContainer');
  const confirmBookBtn = document.getElementById('confirmBookBtn');
  const bookingError = document.getElementById('bookingError');

  if (closeModalBtn) closeModalBtn.onclick = () => modal.style.display = 'none';

  const loadProviders = async () => {
    try {
      const data = await ProviderAPI.getProviders();
      allProviders = data.results || data || [];
      renderProviderCards(allProviders);
    } catch (e) {
      providerList.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Failed to load providers. Is Provider Service (8003) running?</div>`;
    }
  };

  // Real-time Name Search filter
  if (searchInput) {
    searchInput.oninput = (e) => {
      const query = e.target.value.trim().toLowerCase();
      if (!query) {
        renderProviderCards(allProviders);
      } else {
        const filtered = allProviders.filter(p => {
          const fullName = `${p.first_name || ''} ${p.last_name || ''}`.toLowerCase();
          return fullName.includes(query);
        });
        renderProviderCards(filtered);
      }
    };
  }

  loadProviders();

  confirmBookBtn.onclick = async () => {
    if (!selectedSlot || !currentProvider) return;
    confirmBookBtn.textContent = 'Booking...';
    confirmBookBtn.disabled = true;
    bookingError.style.display = 'none';

    try {
      let patientId = user ? user.id : null;
      try {
        const pProfile = await PatientAPI.getMe();
        if (pProfile && pProfile.id) patientId = pProfile.id;
      } catch (err) {}

      // Get provider's service ID or fallback to valid UUID
      let serviceId = '1b8d60c2-550a-4fb4-b816-0155b40d6cfa';
      try {
        const sData = await ProviderAPI.getServices(currentProvider);
        const sList = sData.results || sData || [];
        if (sList.length > 0 && sList[0].id) {
          serviceId = sList[0].id;
        }
      } catch (err) {}

      const holdPayload = {
        patient_id: patientId,
        provider_id: currentProvider,
        slot_id: selectedSlot,
        service_id: serviceId,
        amount: 300000,
        currency: 'VND'
      };
      
      const holdRes = await AppointmentAPI.holdSlot(holdPayload);
      await AppointmentAPI.createAppointment({ appointment_id: holdRes.appointment_id || holdRes.id });

      modal.style.display = 'none';
      alert('Đặt lịch hẹn khám thành công!');
      window.location.hash = '#/appointments';
    } catch (e) {
      bookingError.textContent = getErrorMessage(e, 'Failed to book appointment.');
      bookingError.style.display = 'block';
      confirmBookBtn.textContent = 'Confirm Booking';
      confirmBookBtn.disabled = false;
    }
  };
};
