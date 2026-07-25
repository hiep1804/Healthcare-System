import { Navbar } from '../components/Navbar.js';
import { MedicalRecordAPI, getUser, getErrorMessage } from '../api.js';

export const MedicalRecordsPage = () => {
  const user = getUser();
  const isDoctor = user && user.role === 'DOCTOR';

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Chỉ số Sinh tồn & Kết quả Xét nghiệm</h1>
        <p class="text-muted">Theo dõi chỉ số sinh tồn (huyết áp, nhịp tim, nhiệt độ...) và các tài liệu kết quả xét nghiệm y tế.</p>
      </div>

      <div class="alert alert-info" style="margin-bottom: 1.5rem;">
        ℹ️ <em>Các chỉ số sinh tồn (Huyết áp, Nhịp tim, Cân nặng...), Bệnh án và Kết quả xét nghiệm được kiểm tra, cập nhật chính thức bởi Bác sĩ chuyên khoa.</em>
      </div>

      <!-- VITALS SECTION -->
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Chỉ số sinh tồn (Vitals)</h2>
          ${isDoctor ? `<button id="showAddVitalsBtn" class="btn btn-secondary btn-sm">+ Ghi nhận chỉ số mới</button>` : ''}
        </div>

        ${isDoctor ? `
          <div id="addVitalsContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <form id="addVitalsForm">
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                <div class="form-group"><label class="form-label">Chiều cao (cm)</label><input type="number" id="vitalHeight" class="form-input" placeholder="170" /></div>
                <div class="form-group"><label class="form-label">Cân nặng (kg)</label><input type="number" id="vitalWeight" class="form-input" placeholder="65" /></div>
                <div class="form-group"><label class="form-label">Nhiệt độ (°C)</label><input type="number" step="0.1" id="vitalTemp" class="form-input" placeholder="36.5" /></div>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                <div class="form-group"><label class="form-label">Huyết áp Tâm thu</label><input type="number" id="vitalSys" class="form-input" placeholder="120" /></div>
                <div class="form-group"><label class="form-label">Huyết áp Tâm trương</label><input type="number" id="vitalDia" class="form-input" placeholder="80" /></div>
                <div class="form-group"><label class="form-label">Nhịp tim (BPM)</label><input type="number" id="vitalHeart" class="form-input" placeholder="75" /></div>
              </div>
              <button type="submit" class="btn btn-primary btn-sm">Lưu chỉ số Vitals</button>
              <button type="button" id="cancelVitalsBtn" class="btn btn-secondary btn-sm">Hủy</button>
            </form>
          </div>
        ` : ''}

        <div id="vitalsList">Đang tải Vitals...</div>
      </div>

      <!-- MEDICAL DOCUMENTS SECTION -->
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Tài liệu Y tế & Kết quả Xét nghiệm</h2>
          ${isDoctor ? `<button id="showUploadDocBtn" class="btn btn-secondary btn-sm">+ Upload tài liệu mới</button>` : ''}
        </div>

        ${isDoctor ? `
          <div id="uploadDocContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <form id="uploadDocForm">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                  <label class="form-label">Loại tài liệu</label>
                  <select id="docTypeInput" class="form-input">
                    <option value="LAB_RESULT">Kết quả Xét nghiệm</option>
                    <option value="XRAY">Hình ảnh X-Quang / Siêu âm</option>
                    <option value="PRESCRIPTION">Đơn thuốc cũ</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Link tài liệu / File URL</label>
                  <input type="text" id="docUrlInput" class="form-input" required placeholder="http://... link file" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Mô tả tài liệu</label>
                <input type="text" id="docDescInput" class="form-input" placeholder="Mô tả ngắn gọn" />
              </div>
              <button type="submit" class="btn btn-primary btn-sm">Lưu Tài liệu</button>
              <button type="button" id="cancelUploadDocBtn" class="btn btn-secondary btn-sm">Hủy</button>
            </form>
          </div>
        ` : ''}

        <div id="recordsList" class="dashboard-grid">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
            Đang tải tài liệu y tế...
          </div>
        </div>
      </div>
    </div>
  `;
};

export const attachMedicalRecordsListeners = async () => {
  const container = document.getElementById('recordsList');
  if (!container) return;
  const user = getUser();
  if (!user) return;

  const isDoctor = user && user.role === 'DOCTOR';

  // Load Vitals
  const vitalsList = document.getElementById('vitalsList');
  const loadVitals = async () => {
    try {
      const data = await MedicalRecordAPI.getVitals(user.id);
      const list = data.results || data || [];
      if (list.length === 0) {
        vitalsList.innerHTML = '<p class="text-muted">Chưa ghi nhận chỉ số sinh tồn nào.</p>';
      } else {
        vitalsList.innerHTML = list.map(v => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong>Chiều cao:</strong> ${v.height_cm || 'N/A'} cm | 
              <strong>Cân nặng:</strong> ${v.weight_kg || 'N/A'} kg | 
              <strong>Huyết áp:</strong> ${v.blood_pressure_systolic || '--'}/${v.blood_pressure_diastolic || '--'} mmHg | 
              <strong>Nhịp tim:</strong> ${v.heart_rate || '--'} BPM | 
              <strong>Nhiệt độ:</strong> ${v.temperature_celsius || '--'} °C
            </div>
            <small class="text-muted">${v.recorded_at ? new Date(v.recorded_at).toLocaleDateString() : ''}</small>
          </div>
        `).join('');
      }
    } catch (e) {
      vitalsList.innerHTML = '<p class="text-muted">Chưa có dữ liệu sinh tồn.</p>';
    }
  };

  loadVitals();

  // Vitals form handlers (Doctor only)
  if (isDoctor) {
    const showVitalsBtn = document.getElementById('showAddVitalsBtn');
    const cancelVitalsBtn = document.getElementById('cancelVitalsBtn');
    const vitalsContainer = document.getElementById('addVitalsContainer');
    const vitalsForm = document.getElementById('addVitalsForm');

    if (showVitalsBtn) showVitalsBtn.onclick = () => vitalsContainer.style.display = 'block';
    if (cancelVitalsBtn) cancelVitalsBtn.onclick = () => vitalsContainer.style.display = 'none';

    if (vitalsForm) {
      vitalsForm.onsubmit = async (e) => {
        e.preventDefault();
        try {
          await MedicalRecordAPI.recordVitals(user.id, {
            height_cm: document.getElementById('vitalHeight').value || null,
            weight_kg: document.getElementById('vitalWeight').value || null,
            temperature_celsius: document.getElementById('vitalTemp').value || null,
            blood_pressure_systolic: document.getElementById('vitalSys').value || null,
            blood_pressure_diastolic: document.getElementById('vitalDia').value || null,
            heart_rate: document.getElementById('vitalHeart').value || null
          });
          alert('Đã lưu chỉ số Vitals!');
          vitalsContainer.style.display = 'none';
          loadVitals();
        } catch (err) { alert(getErrorMessage(err, 'Lỗi lưu chỉ số Vitals')); }
      };
    }
  }

  // Upload Document form handlers (Doctor only)
  if (isDoctor) {
    const showDocBtn = document.getElementById('showUploadDocBtn');
    const cancelDocBtn = document.getElementById('cancelUploadDocBtn');
    const docContainer = document.getElementById('uploadDocContainer');
    const docForm = document.getElementById('uploadDocForm');

    if (showDocBtn) showDocBtn.onclick = () => docContainer.style.display = 'block';
    if (cancelDocBtn) cancelDocBtn.onclick = () => docContainer.style.display = 'none';

    if (docForm) {
      docForm.onsubmit = async (e) => {
        e.preventDefault();
        try {
          await MedicalRecordAPI.uploadDocument(user.id, {
            document_type: document.getElementById('docTypeInput').value,
            file_url: document.getElementById('docUrlInput').value,
            description: document.getElementById('docDescInput').value
          });
          alert('Đã tải lên tài liệu y tế!');
          docContainer.style.display = 'none';
          loadRecords();
        } catch (err) { alert(getErrorMessage(err, 'Lỗi lưu tài liệu')); }
      };
    }
  }

  // Load Timeline Records
  const loadRecords = async () => {
    try {
      const data = await MedicalRecordAPI.getRecords(user.id);
      const records = data.results || data || [];
      
      if (records.length === 0) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Chưa có hồ sơ tài liệu y tế nào.</div>`;
        return;
      }

      container.innerHTML = records.map(r => `
        <div class="stat-card glass-panel" style="align-items: flex-start;">
          <h3 style="color: var(--primary-blue);">Chẩn đoán: ${r.diagnosis || 'Khám tổng quát'}</h3>
          <p style="margin-bottom: 0.5rem; font-size: 0.9rem;"><strong>Phác đồ điều trị:</strong> ${r.treatment_plan || 'N/A'}</p>
          <p style="margin-bottom: 0.5rem; font-size: 0.9rem;"><strong>Ghi chú:</strong> ${r.notes || 'N/A'}</p>
          <small class="text-muted">Ngày ghi nhận: ${r.created_at ? new Date(r.created_at).toLocaleDateString() : 'N/A'}</small>
        </div>
      `).join('');
    } catch (e) {
      if (e.status === 404) {
          container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Vui lòng cập nhật thông tin Bệnh nhân tại mục Profile trước khi xem hồ sơ y tế.</div>`;
      } else {
          container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Không thể tải dữ liệu y tế.</div>`;
      }
    }
  };

  loadRecords();
};
