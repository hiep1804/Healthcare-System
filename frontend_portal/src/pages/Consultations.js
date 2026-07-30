import { Navbar } from '../components/Navbar.js';
import { ConsultationAPI, AppointmentAPI, PatientAPI, MedicalRecordAPI, CDSAPI, getUser, getErrorMessage } from '../api.js';

const checkIsDoctor = (u) => {
  if (!u) return false;
  const role = u.role || u.roles;
  if (Array.isArray(role)) return role.some(r => String(r).toUpperCase() === 'DOCTOR');
  if (typeof role === 'string') return role.toUpperCase() === 'DOCTOR';
  return false;
};

export const ConsultationsPage = () => {
  const user = getUser();
  const isDoctor = checkIsDoctor(user);

  const doctorHTML = `
    <!-- DOCTOR PER-APPOINTMENT CONSULTATION SUITE -->
    <div class="glass-panel" style="padding: 1.5rem; margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">1. Danh sách Ca khám Bác sĩ</h2>
        <div style="display: flex; gap: 0.5rem;">
          <button id="filterAllAptsBtn" class="btn btn-secondary btn-sm" style="background: var(--primary-blue); color: white;">Tất cả</button>
          <button id="filterConfirmedAptsBtn" class="btn btn-secondary btn-sm">Cần khám</button>
          <button id="filterCompletedAptsBtn" class="btn btn-secondary btn-sm">Đã hoàn thành</button>
        </div>
      </div>
      <div id="appointmentSelectorList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 1.5rem;">
          Đang tải danh sách ca khám...
        </div>
      </div>
    </div>

    <!-- ACTIVE EXAMINATION WORKSPACE -->
    <div id="activeExamWorkspace" class="glass-panel" style="padding: 2rem; display: none; margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <div>
          <h2 id="examPatientNameTitle" style="color: var(--primary-blue); font-size: 1.4rem; margin: 0;">Ca Khám Bệnh Nhân: ...</h2>
          <p id="examAptMeta" class="text-muted" style="margin: 0.3rem 0 0 0; font-size: 0.9rem;">Mã lịch hẹn: ... | Giờ hẹn: ...</p>
        </div>
        <div style="display: flex; gap: 0.8rem; align-items: center;">
          <button id="toggleAiCdsBtn" class="btn btn-primary btn-sm" style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); border: none; font-weight: 600;">
            🤖 Trợ Lý AI CDS
          </button>
          <span id="examStatusBadge" class="badge badge-info">ĐANG KHÁM</span>
        </div>
      </div>

      <div id="workspaceContentArea">
        <!-- Dynamic workspace content loaded via JS (Active Input Form OR Read-Only View) -->
      </div>
    </div>
  `;

  const patientHTML = `
    <!-- PATIENT CONSULTATIONS LIST -->
    <div class="glass-panel" style="padding: 2rem;">
      <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">Lịch sử Các Phiên Khám & Tư Vấn của Bạn</h2>
      <div id="patientConsultationList" class="dashboard-grid">
        <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
          Đang tải danh sách...
        </div>
      </div>
    </div>

    <!-- Patient Detail Modal -->
    <div id="patientConsultModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center;">
      <div class="glass-panel" style="background: #1e293b; color: #f8fafc; padding: 2rem; max-width: 700px; width: 92%; max-height: 88vh; overflow-y: auto; border-radius: 12px; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.8rem; margin-bottom: 1rem;">
          <h2 style="color: var(--primary-blue); margin: 0; font-size: 1.3rem;">📋 Hồ Sơ Chi Tiết Phiên Khám Lâm Sàng</h2>
          <button id="closePatientConsultModalBtn" style="background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer;">&times;</button>
        </div>
        <div id="patientConsultModalContent">
          <!-- Content filled dynamically -->
        </div>
      </div>
    </div>
  `;

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">
          ${isDoctor ? '🩺 Không Gian Tư Vấn & Khám Bệnh Chuyên Biệt' : '📋 Lịch sử Phiên Tư Vấn & Khám Bệnh'}
        </h1>
        <p class="text-muted">
          ${isDoctor 
            ? 'Thực hiện quy trình khám lâm sàng SOAP, ghi nhận chỉ số sinh tồn, chẩn đoán y khoa và kê đơn thuốc điện tử cho từng ca khám.' 
            : 'Xem chi tiết toàn bộ thông số kết quả chẩn đoán, ghi chú lâm sàng SOAP, chỉ số sinh tồn và đơn thuốc từ bác sĩ.'}
        </p>
      </div>

      ${isDoctor ? doctorHTML : patientHTML}
    </div>
  `;
};

// Helper: Format patient vitals strictly
const renderPatientVitalsHTML = (vitalsList) => {
  const v = Array.isArray(vitalsList) && vitalsList.length > 0 ? vitalsList[0] : vitalsList;
  if (!v) return null;

  const items = [];
  const h = v.height_cm || v.height;
  if (h && h !== '--' && String(h).trim() !== '' && h !== 0 && h !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>📐 Chiều cao:</strong> ${h} cm</div>`);
  }
  const w = v.weight_kg || v.weight;
  if (w && w !== '--' && String(w).trim() !== '' && w !== 0 && w !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>⚖️ Cân nặng:</strong> ${w} kg</div>`);
  }
  const t = v.temperature_celsius || v.temperature_c || v.temperature;
  if (t && t !== '--' && String(t).trim() !== '' && t !== 0 && t !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>🌡️ Nhiệt độ:</strong> ${t} °C</div>`);
  }
  const sys = v.blood_pressure_systolic;
  const dia = v.blood_pressure_diastolic;
  const sysValid = sys && sys !== '--' && String(sys).trim() !== '' && sys !== 0 && sys !== '0';
  const diaValid = dia && dia !== '--' && String(dia).trim() !== '' && dia !== 0 && dia !== '0';
  if (sysValid && diaValid) {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>🩺 Huyết áp:</strong> ${sys}/${dia} mmHg</div>`);
  }
  const hr = v.heart_rate || v.heartRate;
  if (hr && hr !== '--' && String(hr).trim() !== '' && hr !== 0 && hr !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>❤️ Nhịp tim:</strong> ${hr} BPM</div>`);
  }

  if (items.length === 0) return null;
  return `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.6rem; font-size: 0.9rem;">${items.join('')}</div>`;
};

export const attachConsultationsListeners = async () => {
  const user = getUser();
  if (!user) return;

  const isDoctor = checkIsDoctor(user);

  if (isDoctor) {
    // ALWAYS INITIALIZE AI CDS CHATBOT FIRST
    initAiCdsChatbot(null, null, null);

    // DOCTOR WORKSPACE LISTENER
    const aptListContainer = document.getElementById('appointmentSelectorList');
    const examWorkspace = document.getElementById('activeExamWorkspace');
    const patientTitle = document.getElementById('examPatientNameTitle');
    const aptMeta = document.getElementById('examAptMeta');
    const statusBadge = document.getElementById('examStatusBadge');
    const workspaceContentArea = document.getElementById('workspaceContentArea');

    const filterAllBtn = document.getElementById('filterAllAptsBtn');
    const filterConfirmedBtn = document.getElementById('filterConfirmedAptsBtn');
    const filterCompletedBtn = document.getElementById('filterCompletedAptsBtn');

    if (!aptListContainer) return;

    let doctorAppointments = [];
    let activeAppointment = null;
    let activeConsultation = null;
    let activeRxItems = [];

    const loadDoctorAppointments = async (filterStatus = null) => {
      try {
        const res = await AppointmentAPI.getAppointments();
        const raw = res.data || res.results || res || [];
        
        // Show ONLY CONFIRMED and COMPLETED appointments in Consultations suite
        doctorAppointments = raw.filter(a => a.status === 'CONFIRMED' || a.status === 'COMPLETED');

        if (filterStatus) {
          renderAppointmentSelector(doctorAppointments.filter(a => a.status === filterStatus));
        } else {
          renderAppointmentSelector(doctorAppointments);
        }
      } catch (e) {
        aptListContainer.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Không thể tải danh sách ca khám.</div>`;
      }
    };

    const renderAppointmentSelector = (list) => {
      if (!Array.isArray(list) || list.length === 0) {
        aptListContainer.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 1.5rem;">Chưa có ca khám nào.</div>`;
        return;
      }

      const now = new Date();

      aptListContainer.innerHTML = list.map(a => {
        const slot = a.slot_detail || {};
        const startTimeStr = slot.start_time ? slot.start_time.substring(0,5) : '';
        const endTimeStr = slot.end_time ? slot.end_time.substring(0,5) : '';
        const timeDisplay = slot.date ? `${slot.date} (${startTimeStr} - ${endTimeStr})` : 'N/A';
        const isCompleted = a.status === 'COMPLETED';

        let canStart = true;
        let isExpired = false;

        if (!isCompleted && slot.date && slot.start_time) {
          const startDt = new Date(`${slot.date}T${slot.start_time}`);
          const endDt = slot.end_time ? new Date(`${slot.date}T${slot.end_time}`) : new Date(startDt.getTime() + 30 * 60000);

          if (now < startDt) {
            canStart = false; // Chưa đến thời gian bắt đầu
          } else if (now > endDt) {
            isExpired = true; // Quá thời gian bắt đầu
            // Auto cancel in background
            AppointmentAPI.cancelAppointment(a.id).catch(() => {});
          }
        }

        let badgeHTML = '';
        let buttonHTML = '';

        if (isCompleted) {
          badgeHTML = `<span class="badge badge-success">ĐÃ KHÁM HOÀN TẤT</span>`;
          buttonHTML = `<button class="btn btn-secondary btn-sm select-apt-exam-btn" style="width: 100%; margin-top: auto; background: #3b82f6; color: white;" data-id="${a.id}">👁️ Xem Lại Bệnh Án</button>`;
        } else if (isExpired) {
          badgeHTML = `<span class="badge badge-error" style="background: #ef4444;">ĐÃ HỦY (QUÁ HẠN)</span>`;
          buttonHTML = `<button disabled class="btn btn-secondary btn-sm" style="width: 100%; margin-top: auto; opacity: 0.5; cursor: not-allowed; background: #64748b; color: #cbd5e1;">⚠️ Đã quá thời gian khám (Tự động hủy)</button>`;
        } else if (!canStart) {
          badgeHTML = `<span class="badge badge-warning">CHỜ ĐẾN GIỜ KHÁM</span>`;
          buttonHTML = `<button disabled class="btn btn-secondary btn-sm" style="width: 100%; margin-top: auto; opacity: 0.6; cursor: not-allowed; background: #f59e0b; color: white;">⏳ Chưa đến thời gian khám</button>`;
        } else {
          badgeHTML = `<span class="badge badge-info">SẴN SÀNG KHÁM</span>`;
          buttonHTML = `<button class="btn btn-primary btn-sm select-apt-exam-btn" style="width: 100%; margin-top: auto; background: #10b981; border: none; font-weight: 600;" data-id="${a.id}">🩺 Khám Ca Này</button>`;
        }

        return `
          <div class="stat-card glass-panel" style="align-items: flex-start; position: relative;">
            <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.4rem;">
              <strong style="color: var(--primary-blue); font-size: 0.95rem;">Lịch hẹn: ${a.id ? a.id.substring(0,8) : 'N/A'}</strong>
              ${badgeHTML}
            </div>
            <p style="margin-bottom: 0.2rem; font-size: 0.88rem;"><strong>Giờ hẹn:</strong> ${timeDisplay}</p>
            <p style="margin-bottom: 0.6rem; font-size: 0.85rem;" class="text-muted"><strong>Lý do:</strong> ${a.reason_for_visit || 'Tư vấn chung'}</p>
            ${buttonHTML}
          </div>
        `;
      }).join('');

      document.querySelectorAll('.select-apt-exam-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const aptId = e.currentTarget.dataset.id;
          activeAppointment = doctorAppointments.find(a => String(a.id) === String(aptId));
          if (!activeAppointment) return;

          // Bind AI CDS Chatbot session to this active patient IMMEDIATELY
          initAiCdsChatbot(
            null,
            activeAppointment.patient_id,
            activeAppointment.provider_id
          );

          examWorkspace.style.display = 'block';
          examWorkspace.scrollIntoView({ behavior: 'smooth' });

          const slot = activeAppointment.slot_detail || {};
          const timeDisplay = slot.date ? `${slot.date} (${slot.start_time ? slot.start_time.substring(0,5) : ''})` : 'N/A';
          const isCompleted = activeAppointment.status === 'COMPLETED';

          patientTitle.textContent = `Ca Khám Bệnh Nhân: ${activeAppointment.patient_id ? activeAppointment.patient_id.substring(0,8) : 'N/A'}`;
          aptMeta.textContent = `Mã lịch hẹn: ${activeAppointment.id} | Giờ hẹn: ${timeDisplay} | Lý do: ${activeAppointment.reason_for_visit || 'Tư vấn sức khỏe'}`;
          statusBadge.textContent = isCompleted ? 'ĐÃ KHÁM HOÀN TẤT (CHẾ ĐỘ XEM)' : 'ĐANG KHÁM LÂM SÀNG';
          statusBadge.className = isCompleted ? 'badge badge-success' : 'badge badge-info';

          // Initialize or load Consultation for this Appointment
          try {
            const csRes = await ConsultationAPI.createConsultation({
              appointment_id: activeAppointment.id,
              patient_id: activeAppointment.patient_id,
              provider_id: activeAppointment.provider_id
            });
            activeConsultation = csRes;
          } catch (cErr) {
            try {
              const listRes = await ConsultationAPI.getConsultations();
              const list = listRes.results || listRes.data || listRes || [];
              activeConsultation = list.find(c => String(c.appointment_id) === String(activeAppointment.id)) || { id: null };
            } catch (lErr) {}
          }

          let existingRx = [];
          if (activeConsultation && activeConsultation.id) {
            try {
              const [fullCs, rxRes] = await Promise.all([
                ConsultationAPI.getConsultation(activeConsultation.id).catch(() => activeConsultation),
                ConsultationAPI.getPrescriptions(activeConsultation.id).catch(() => ({ items: [] }))
              ]);
              if (fullCs) activeConsultation = fullCs;
              existingRx = rxRes ? (rxRes.items || (Array.isArray(rxRes) ? rxRes : [])) : [];
            } catch (rErr) {}
          }

          let existingVitals = [];
          if (activeAppointment.patient_id) {
            try {
              const vitRes = await MedicalRecordAPI.getVitals(activeAppointment.patient_id);
              const toArr = (v) => Array.isArray(v) ? v : ((v && v.results) || (v && v.data) || []);
              existingVitals = toArr(vitRes);
            } catch (vErr) {}
          }

          const cn = (activeConsultation && activeConsultation.clinical_note) ? activeConsultation.clinical_note : {};
          const subjective = cn.subjective || '';
          const objective = cn.objective || '';
          let assessment = cn.assessment || (activeConsultation && activeConsultation.diagnosis) || (activeConsultation && activeConsultation.clinical_notes) || '';

          if (assessment.startsWith('Chẩn đoán: ')) {
            assessment = assessment.replace('Chẩn đoán: ', '');
          }
          if (!assessment || assessment.trim() === '') {
            assessment = (activeAppointment && activeAppointment.reason_for_visit) ? `Tư vấn & Đánh giá: ${activeAppointment.reason_for_visit}` : 'Chẩn đoán y khoa tổng quát (Theo dõi sức khỏe)';
          }
          const plan = cn.plan || '';

          // REQUIREMENT: IF COMPLETED -> RENDER READ-ONLY WORKSPACE (NO EDITING, REMOVE COMPLETE BUTTON)
          if (isCompleted) {
            const vitalsHTML = renderPatientVitalsHTML(existingVitals);

            workspaceContentArea.innerHTML = `
              <div style="display: flex; flex-direction: column; gap: 1.2rem;">
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 1rem; border-radius: 8px; color: #60a5fa;">
                  <strong>ℹ️ Chế độ Xem lại Bệnh án:</strong> Ca khám này đã hoàn tất. Tất cả chỉ số y khoa và đơn thuốc hiển thị ở dạng chỉ xem và không thể chỉnh sửa.
                </div>

                <!-- READ-ONLY SOAP NOTE -->
                <div style="background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.8rem; font-size: 1.1rem;">📋 Ghi Chú Lâm Sàng (SOAP Note)</h3>
                  <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.95rem;">
                    <div><strong style="color: #60a5fa;">S (Triệu chứng cơ năng):</strong> ${subjective || 'Bệnh nhân khai báo lý do khám'}</div>
                    <div><strong style="color: #60a5fa;">O (Thăm khám thực thể):</strong> ${objective || 'Kết quả khám lâm sàng bình thường'}</div>
                    <div><strong style="color: #60a5fa;">A (Chẩn đoán y khoa):</strong> <span style="color: #f8fafc; font-weight: 600;">${assessment || 'Khám y khoa'}</span></div>
                    <div><strong style="color: #60a5fa;">P (Phác đồ & Lời khuyên):</strong> ${plan || 'Theo dõi và tuân thủ hướng dẫn điều trị'}</div>
                  </div>
                </div>

                <!-- READ-ONLY VITALS -->
                ${vitalsHTML ? `
                  <div style="background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                    <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.8rem; font-size: 1.1rem;">📊 Chỉ Số Sinh Tồn & Thể Trạng Lúc Khám</h3>
                    ${vitalsHTML}
                  </div>
                ` : ''}

                <!-- READ-ONLY PRESCRIPTION -->
                <div style="background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.8rem; font-size: 1.1rem;">💊 Đơn Thuốc Điện Tử Bác Sĩ Kê</h3>
                  ${existingRx.length === 0 ? '<p class="text-muted" style="margin: 0;">Chưa kê đơn thuốc.</p>' : `
                    <ul style="padding-left: 1.2rem; margin: 0;">
                      ${existingRx.map(item => `
                        <li style="margin-bottom: 0.4rem; line-height: 1.4;">
                          <strong style="color: #f8fafc;">${item.drug_name}</strong> - Liều: ${item.dosage || '1 viên'} (${item.frequency || '2 lần/ngày'}) - ${item.duration_days || 5} ngày
                        </li>
                      `).join('')}
                    </ul>
                  `}
                </div>
              </div>
            `;
            return;
          }

          // ACTIVE EDITABLE WORKSPACE FOR CONFIRMED APPOINTMENTS
          workspaceContentArea.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
              <!-- LEFT PANEL: SOAP NOTES & VITALS -->
              <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                <!-- SOAP Note -->
                <div style="background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">1. Ghi chú Lâm sàng (SOAP Note)</h3>
                  <form id="workspaceSoapForm">
                    <div class="form-group" style="margin-bottom: 0.6rem;">
                      <label class="form-label" style="font-size: 0.85rem;">S (Subjective - Triệu chứng cơ năng):</label>
                      <input type="text" id="wsSoapS" class="form-input" placeholder="Lý do khám, bệnh nhân đau đầu, ho sốt..." value="${subjective}" />
                    </div>
                    <div class="form-group" style="margin-bottom: 0.6rem;">
                      <label class="form-label" style="font-size: 0.85rem;">O (Objective - Thăm khám thực thể):</label>
                      <input type="text" id="wsSoapO" class="form-input" placeholder="Họng đỏ, nghe phổi trong, tim đều..." value="${objective}" />
                    </div>
                    <div class="form-group" style="margin-bottom: 0.6rem;">
                      <label class="form-label" style="font-size: 0.85rem;">A (Assessment - Đánh giá & Chẩn đoán):</label>
                      <input type="text" id="wsSoapA" class="form-input" placeholder="Viêm họng cấp / Sốt siêu vi..." value="${assessment}" />
                    </div>
                    <div class="form-group" style="margin-bottom: 0.8rem;">
                      <label class="form-label" style="font-size: 0.85rem;">P (Plan - Phác đồ & Lời khuyên):</label>
                      <input type="text" id="wsSoapP" class="form-input" placeholder="Nghỉ ngơi, uống đủ nước, uống thuốc đúng liều..." value="${plan}" />
                    </div>
                    <button type="submit" class="btn btn-secondary btn-sm" style="width: 100%;">💾 Lưu Ghi chú SOAP</button>
                  </form>
                </div>

                <!-- Vitals Recorder -->
                <div style="background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">2. Ghi nhận Chỉ số Sinh tồn (Vitals)</h3>
                  <form id="workspaceVitalsForm">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; margin-bottom: 0.6rem;">
                      <div><label class="form-label" style="font-size: 0.8rem;">Cao (cm)</label><input type="number" id="wsVitalHeight" class="form-input" placeholder="170" /></div>
                      <div><label class="form-label" style="font-size: 0.8rem;">Nặng (kg)</label><input type="number" id="wsVitalWeight" class="form-input" placeholder="65" /></div>
                      <div><label class="form-label" style="font-size: 0.8rem;">Nhiệt độ (°C)</label><input type="number" step="0.1" id="wsVitalTemp" class="form-input" placeholder="36.5" /></div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; margin-bottom: 0.8rem;">
                      <div><label class="form-label" style="font-size: 0.8rem;">Huyết áp Thu</label><input type="number" id="wsVitalSys" class="form-input" placeholder="120" /></div>
                      <div><label class="form-label" style="font-size: 0.8rem;">Huyết áp Trương</label><input type="number" id="wsVitalDia" class="form-input" placeholder="80" /></div>
                      <div><label class="form-label" style="font-size: 0.8rem;">Nhịp tim (BPM)</label><input type="number" id="wsVitalHeart" class="form-input" placeholder="75" /></div>
                    </div>
                    <button type="submit" class="btn btn-secondary btn-sm" style="width: 100%;">📊 Lưu Chỉ số Sinh tồn</button>
                  </form>
                </div>
              </div>

              <!-- RIGHT PANEL: PRESCRIPTIONS & COMPLETION -->
              <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                <!-- Prescription Builder -->
                <div style="background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">3. Kê Đơn thuốc Điện tử</h3>
                  <form id="workspaceRxForm">
                    <div class="form-group" style="margin-bottom: 0.6rem;">
                      <label class="form-label" style="font-size: 0.85rem;">Tên thuốc:</label>
                      <input type="text" id="wsRxName" class="form-input" required placeholder="Paracetamol 500mg, Amoxicillin..." />
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; margin-bottom: 0.8rem;">
                      <div><label class="form-label" style="font-size: 0.8rem;">Liều dùng</label><input type="text" id="wsRxDosage" class="form-input" placeholder="1 viên" /></div>
                      <div><label class="form-label" style="font-size: 0.8rem;">Tần suất</label><input type="text" id="wsRxFreq" class="form-input" placeholder="2 lần/ngày" /></div>
                      <div><label class="form-label" style="font-size: 0.8rem;">Số ngày</label><input type="number" id="wsRxDays" class="form-input" value="5" /></div>
                    </div>
                    <button type="submit" class="btn btn-secondary btn-sm" style="width: 100%; margin-bottom: 1rem;">💊 Thêm Thuốc Vào Đơn</button>
                  </form>

                  <h4 style="font-size: 0.95rem; color: var(--primary-blue); margin-bottom: 0.5rem;">Danh sách thuốc đã thêm:</h4>
                  <div id="wsRxList" style="max-height: 150px; overflow-y: auto; background: rgba(0,0,0,0.2); padding: 0.6rem; border-radius: 6px;">
                    <p class="text-muted" style="margin: 0; font-size: 0.85rem;">Chưa thêm thuốc nào.</p>
                  </div>
                </div>

                <!-- Complete Exam Button -->
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; padding: 1.2rem; border-radius: 10px; margin-top: auto;">
                  <h3 style="color: #10b981; font-size: 1.1rem; margin-top: 0; margin-bottom: 0.5rem;">4. Hoàn tất Phiên Khám</h3>
                  <p class="text-muted" style="font-size: 0.85rem; margin-bottom: 1rem;">Xác nhận hoàn tất ca khám, hệ thống sẽ tự động cập nhật trạng thái Lịch hẹn và lưu toàn bộ bệnh án cho bệnh nhân.</p>
                  <button id="wsCompleteExamBtn" class="btn btn-primary" style="width: 100%; background: #10b981; border: none; font-weight: 600; padding: 0.8rem;">
                    ✅ Xác nhận Hoàn tất Ca Khám & Lưu Bệnh Án
                  </button>
                </div>
              </div>
            </div>
          `;

          // Re-bind active workspace forms
          activeRxItems = existingRx;
          renderRxItemsList();
          bindWorkspaceFormEvents();

          // Initialize AI CDS Chatbot session for this examination
          if (activeConsultation && activeConsultation.id) {
            initAiCdsChatbot(activeConsultation.id, activeAppointment.patient_id, activeAppointment.provider_id);
          }
        };
      });
    };

    const renderRxItemsList = () => {
      const rxListContainer = document.getElementById('wsRxList');
      if (!rxListContainer) return;
      if (activeRxItems.length === 0) {
        rxListContainer.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Chưa thêm thuốc nào.</p>';
      } else {
        rxListContainer.innerHTML = activeRxItems.map((item, index) => `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; font-size: 0.85rem; background: rgba(255,255,255,0.05); padding: 0.4rem 0.6rem; border-radius: 4px;">
            <div><strong>${item.drug_name}</strong> - ${item.dosage} (${item.frequency})</div>
            <button type="button" class="remove-rx-btn" data-index="${index}" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1rem;">&times;</button>
          </div>
        `).join('');

        document.querySelectorAll('.remove-rx-btn').forEach(btn => {
          btn.onclick = (e) => {
            const idx = e.currentTarget.dataset.index;
            activeRxItems.splice(idx, 1);
            renderRxItemsList();
          };
        });
      }
    };

    const bindWorkspaceFormEvents = () => {
      const soapForm = document.getElementById('workspaceSoapForm');
      const vitalsForm = document.getElementById('workspaceVitalsForm');
      const rxForm = document.getElementById('workspaceRxForm');
      const completeBtn = document.getElementById('wsCompleteExamBtn');

      if (soapForm) {
        soapForm.onsubmit = async (e) => {
          e.preventDefault();
          if (!activeConsultation || !activeConsultation.id) { alert('Chưa chọn ca khám!'); return; }
          try {
            await ConsultationAPI.addNote(activeConsultation.id, {
              subjective: document.getElementById('wsSoapS').value,
              objective: document.getElementById('wsSoapO').value,
              assessment: document.getElementById('wsSoapA').value,
              plan: document.getElementById('wsSoapP').value
            });
            alert('Đã lưu Ghi chú SOAP!');
          } catch (err) { alert(getErrorMessage(err, 'Lỗi lưu SOAP Note.')); }
        };
      }

      if (vitalsForm) {
        vitalsForm.onsubmit = async (e) => {
          e.preventDefault();
          if (!activeAppointment || !activeAppointment.patient_id) { alert('Chưa chọn bệnh nhân!'); return; }
          try {
            await MedicalRecordAPI.recordVitals(activeAppointment.patient_id, {
              height_cm: document.getElementById('wsVitalHeight').value || null,
              weight_kg: document.getElementById('wsVitalWeight').value || null,
              temperature_c: document.getElementById('wsVitalTemp').value || null,
              temperature_celsius: document.getElementById('wsVitalTemp').value || null,
              blood_pressure_systolic: document.getElementById('wsVitalSys').value || null,
              blood_pressure_diastolic: document.getElementById('wsVitalDia').value || null,
              heart_rate: document.getElementById('wsVitalHeart').value || null
            });
            alert('Đã lưu Chỉ số sinh tồn!');
            if (activeAppointment && activeAppointment.patient_id) {
              initAiCdsChatbot(
                activeConsultation ? activeConsultation.id : null,
                activeAppointment.patient_id,
                activeAppointment.provider_id
              );
            }
          } catch (err) { alert(getErrorMessage(err, 'Lỗi lưu chỉ số sinh tồn.')); }
        };
      }

      if (rxForm) {
        rxForm.onsubmit = async (e) => {
          e.preventDefault();
          if (!activeConsultation || !activeConsultation.id) { alert('Chưa chọn ca khám!'); return; }

          const name = document.getElementById('wsRxName').value;
          const dosage = document.getElementById('wsRxDosage').value;
          const freq = document.getElementById('wsRxFreq').value;
          const daysEl = document.getElementById('wsRxDays');
          const daysVal = daysEl ? daysEl.value : null;
          const durationDays = parseInt(daysVal, 10) || 5;

          activeRxItems.push({
            drug_name: name,
            dosage: dosage || '1 viên',
            frequency: freq || '2 lần/ngày',
            duration_days: durationDays,
            quantity: durationDays * 2
          });
          renderRxItemsList();

          const cleanedItems = activeRxItems.map(item => ({
            drug_name: item.drug_name || 'Thuốc điều trị',
            dosage: item.dosage || '1 viên',
            frequency: item.frequency || '2 lần/ngày',
            duration_days: parseInt(item.duration_days, 10) || 5,
            quantity: parseInt(item.quantity, 10) || 10
          }));

          try {
            await ConsultationAPI.createPrescription(activeConsultation.id, {
              notes: 'Đơn thuốc điện tử',
              items: cleanedItems
            });
            document.getElementById('wsRxName').value = '';
            alert('Đã kê thêm thuốc vào đơn!');
          } catch (err) { alert(getErrorMessage(err, 'Lỗi lưu đơn thuốc.')); }
        };
      }

      if (completeBtn) {
        completeBtn.onclick = async () => {
          if (!activeAppointment) return;

          try {
            if (activeConsultation && activeConsultation.id) {
              try { await ConsultationAPI.completeConsultation(activeConsultation.id); } catch (cErr) {}
            }

            try {
              await AppointmentAPI.confirmAppointment(activeAppointment.id);
            } catch (cfErr) {}

            await AppointmentAPI.completeAppointment(activeAppointment.id);

            alert('Đã hoàn tất ca khám và lưu bệnh án thành công!');
            examWorkspace.style.display = 'none';
            loadDoctorAppointments();
          } catch (err) {
            alert(getErrorMessage(err, 'Lỗi hoàn tất ca khám.'));
          }
        };
      }
    };

    if (filterAllBtn) filterAllBtn.onclick = () => loadDoctorAppointments();
    if (filterConfirmedBtn) filterConfirmedBtn.onclick = () => loadDoctorAppointments('CONFIRMED');
    if (filterCompletedBtn) filterCompletedBtn.onclick = () => loadDoctorAppointments('COMPLETED');

    loadDoctorAppointments();
    initAiCdsChatbot(null, null, null);

  } else {
    // PATIENT VIEW CONSULTATIONS
    const patientListContainer = document.getElementById('patientConsultationList');
    const modal = document.getElementById('patientConsultModal');
    const closeModalBtn = document.getElementById('closePatientConsultModalBtn');
    const modalContent = document.getElementById('patientConsultModalContent');

    if (!patientListContainer) return;
    if (closeModalBtn) closeModalBtn.onclick = () => modal.style.display = 'none';

    try {
      const csRes = await ConsultationAPI.getConsultations();
      const list = csRes.results || csRes.data || csRes || [];

      if (!Array.isArray(list) || list.length === 0) {
        patientListContainer.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Bạn chưa có phiên khám nào.</div>`;
        return;
      }

      patientListContainer.innerHTML = list.map(c => `
        <div class="stat-card glass-panel" style="align-items: flex-start; position: relative;">
          <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.5rem;">
            <strong style="color: var(--primary-blue);">Ca khám ID: ${c.id ? c.id.substring(0,8) : 'N/A'}</strong>
            <span class="badge badge-success">${c.status || 'COMPLETED'}</span>
          </div>
          <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Mã lịch hẹn:</strong> ${c.appointment_id || 'N/A'}</p>
          <p style="margin-bottom: 0.6rem; font-size: 0.9rem;"><strong>Tóm tắt:</strong> ${(c.clinical_note && (c.clinical_note.assessment || c.clinical_note.subjective)) || c.clinical_notes || c.diagnosis || 'Khám y khoa'}</p>
          <button class="btn btn-primary btn-sm view-patient-consult-btn" style="width: 100%; margin-top: auto;" data-id="${c.id}" data-patient="${c.patient_id || ''}" data-aptid="${c.appointment_id || ''}">
            👁️ Xem Chi Tiết Toàn Bộ Kết Quả Ca Khám
          </button>
        </div>
      `).join('');

      document.querySelectorAll('.view-patient-consult-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const cid = e.currentTarget.dataset.id;
          const patientId = e.currentTarget.dataset.patient;

          modal.style.display = 'flex';
          modalContent.innerHTML = '<div style="text-align: center; padding: 2rem;">Đang tải chi tiết phiên khám...</div>';

          try {
            const [detail, rxData, vitRes] = await Promise.all([
              ConsultationAPI.getConsultation(cid).catch(() => ({ id: cid })),
              ConsultationAPI.getPrescriptions(cid).catch(() => ({ items: [] })),
              patientId ? MedicalRecordAPI.getVitals(patientId).catch(() => []) : Promise.resolve([])
            ]);

            const rxItems = rxData ? (rxData.items || (Array.isArray(rxData) ? rxData : [])) : [];
            const cn = detail.clinical_note || {};
            const subjective = cn.subjective || '';
            const objective = cn.objective || '';
            let assessment = cn.assessment || cn.diagnosis || detail.clinical_notes || detail.diagnosis || '';
            
            if (assessment.startsWith('Chẩn đoán: ')) {
              assessment = assessment.replace('Chẩn đoán: ', '');
            }
            if (!assessment || assessment.trim() === '') {
              assessment = 'Chẩn đoán y khoa tổng quát (Theo dõi sức khỏe)';
            }
            const plan = cn.plan || '';

            const toArr = (v) => Array.isArray(v) ? v : ((v && v.results) || (v && v.data) || []);
            const vitals = toArr(vitRes);
            const vitalsHTML = renderPatientVitalsHTML(vitals);

            modalContent.innerHTML = `
              <div style="display: flex; flex-direction: column; gap: 1.2rem; font-size: 0.95rem;">
                <!-- Header Info -->
                <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <strong style="color: var(--primary-blue); font-size: 1.05rem;">Mã Ca Khám: ${detail.id || cid}</strong>
                    <span class="badge badge-success">${detail.status || 'COMPLETED'}</span>
                  </div>
                  <p style="margin: 0.3rem 0;"><strong>Bác sĩ tư vấn:</strong> ID ${detail.provider_id ? String(detail.provider_id).substring(0,8) : 'N/A'}</p>
                  <p style="margin: 0.3rem 0;" class="text-muted"><strong>Mã lịch hẹn:</strong> ${detail.appointment_id || 'N/A'}</p>
                </div>

                <!-- 1. SOAP Clinical Note -->
                <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.6rem; font-size: 1.05rem;">📋 Ghi Chú Lâm Sàng Bác Sĩ (SOAP Note)</h3>
                  <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.92rem;">
                    <div><strong style="color: #60a5fa;">S (Triệu chứng cơ năng):</strong> ${subjective || 'Bệnh nhân khai báo lý do khám'}</div>
                    <div><strong style="color: #60a5fa;">O (Thăm khám thực thể):</strong> ${objective || 'Kết quả khám lâm sàng bình thường'}</div>
                    <div><strong style="color: #60a5fa;">A (Chẩn đoán y khoa):</strong> <span style="color: #f8fafc; font-weight: 600;">${assessment || 'Khám y khoa'}</span></div>
                    <div><strong style="color: #60a5fa;">P (Lời khuyên & Phác đồ):</strong> ${plan || 'Theo dõi và tuân thủ hướng dẫn điều trị'}</div>
                  </div>
                </div>

                <!-- 2. Vitals & Body Metrics -->
                ${vitalsHTML ? `
                  <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.6rem; font-size: 1.05rem;">📊 Chỉ Số Sinh Tồn & Thể Trạng Lúc Khám</h3>
                    ${vitalsHTML}
                  </div>
                ` : ''}

                <!-- 3. Electronic Prescription -->
                <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.6rem; font-size: 1.05rem;">💊 Đơn Thuốc Điện Tử Bác Sĩ Kê</h3>
                  ${rxItems.length === 0 ? '<p class="text-muted" style="margin: 0;">Chưa kê đơn thuốc.</p>' : `
                    <ul style="padding-left: 1.2rem; margin: 0;">
                      ${rxItems.map(item => `
                        <li style="margin-bottom: 0.4rem; line-height: 1.4;">
                          <strong style="color: #f8fafc;">${item.drug_name}</strong> - Liều: ${item.dosage || '1 viên'} (${item.frequency || '2 lần/ngày'})
                        </li>
                      `).join('')}
                    </ul>
                  `}
                </div>
              </div>
            `;
          } catch (mErr) {
            modalContent.innerHTML = `<div class="alert alert-error">Không thể tải kết quả phiên khám.</div>`;
          }
        };
      });

      // Auto open matching patient consultation detail modal if aptId is present in URL hash
      if (window.location.hash.includes('aptId=')) {
        const match = window.location.hash.match(/aptId=([a-f0-9-]+)/i);
        if (match && match[1]) {
          const targetAptId = match[1];
          setTimeout(() => {
            const targetBtn = document.querySelector(`.view-patient-consult-btn[data-aptid="${targetAptId}"]`) || document.querySelector(`.view-patient-consult-btn`);
            if (targetBtn) targetBtn.click();
          }, 200);
        }
      }

    } catch (err) {
      patientListContainer.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Không thể tải danh sách phiên khám.</div>`;
    }
  }

  // Bind Global Floating FAB Button for Doctor
  const globalFab = document.getElementById('globalAiCdsFab');
  if (globalFab) {
    globalFab.onclick = () => {
      const drawer = document.getElementById('aiCdsDrawer');
      if (drawer) {
        drawer.style.display = drawer.style.display === 'none' ? 'flex' : 'none';
      }
    };
  }
};

// ============================================================
// AI CDS CHATBOT CONTROLLER (Module-scoped)
// ============================================================
let currentCdsConversation = null;
let currentConsultationId = null;
let currentPatientId = null;
let currentProviderId = null;
let isSendingAiMsg = false;

const ensureConversation = async () => {
  const messagesList = document.getElementById('aiCdsMessagesList');
  if (!currentCdsConversation) {
    if (messagesList) {
      messagesList.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 1.5rem; font-size: 0.85rem;">🤖 Khởi tạo Trợ lý AI CDS...</div>';
    }
    currentCdsConversation = await CDSAPI.createConversation({
      consultation_id: currentConsultationId || null,
      patient_id: currentPatientId || null,
      provider_id: currentProviderId || null,
      force_new: true
    });
    renderAiCdsMessages(currentCdsConversation);
  }
  return currentCdsConversation;
};

const handleSend = async () => {
  if (isSendingAiMsg) return;

  const inputEl = document.getElementById('aiCdsInput');
  const msgListEl = document.getElementById('aiCdsMessagesList');
  if (!inputEl || !msgListEl) return;

  const text = inputEl.value.trim();
  if (!text) {
    alert('Vui lòng nhập nội dung câu hỏi trước khi gửi!');
    return;
  }

  isSendingAiMsg = true;

  // 1. Append Doctor message IMMEDIATELY for instant UI feedback
  const docMsgHTML = `
    <div class="ai-cds-row doctor">
      <div class="ai-cds-msg doctor">${text}</div>
    </div>
  `;
  msgListEl.insertAdjacentHTML('beforeend', docMsgHTML);

  // 2. Append Loading Indicator IMMEDIATELY
  const loadingId = `loading-${Date.now()}`;
  const loadingHTML = `
    <div id="${loadingId}" class="ai-cds-row assistant">
      <div style="width: 28px; height: 28px; border-radius: 50%; background: #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0;">🤖</div>
      <div class="ai-cds-msg assistant" style="font-style: italic; color: #94a3b8;">
        ⏳ AI đang phân tích dữ liệu y khoa...
      </div>
    </div>
  `;
  msgListEl.insertAdjacentHTML('beforeend', loadingHTML);
  msgListEl.scrollTop = msgListEl.scrollHeight;
  inputEl.value = '';

  try {
    await ensureConversation();
    const res = await CDSAPI.sendMessage(currentCdsConversation.id, text);
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) loadingEl.remove();

    // Refresh full conversation data
    const updatedConv = await CDSAPI.getConversation(currentCdsConversation.id);
    currentCdsConversation = updatedConv;
    renderAiCdsMessages(updatedConv);
  } catch (err) {
    console.error('[AI CDS Error]', err);
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) loadingEl.remove();
    const errorMsg = getErrorMessage(err, 'Lỗi kết nối AI Service.');
    const errHTML = `
      <div class="ai-cds-row assistant">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #ef4444; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0;">⚠️</div>
        <div class="ai-cds-msg assistant" style="color: #f87171;">${errorMsg}</div>
      </div>
    `;
    msgListEl.insertAdjacentHTML('beforeend', errHTML);
    msgListEl.scrollTop = msgListEl.scrollHeight;
  } finally {
    isSendingAiMsg = false;
  }
};

window.handleSendAiCds = handleSend;

const initAiCdsChatbot = async (consultationId, patientId, providerId) => {
  currentConsultationId = consultationId;
  currentPatientId = patientId;
  currentProviderId = providerId;
  currentCdsConversation = null;

  let drawer = document.getElementById('aiCdsDrawer');
  if (!drawer) {
    drawer = document.createElement('div');
    drawer.id = 'aiCdsDrawer';
    drawer.className = 'ai-cds-drawer';
    drawer.innerHTML = `
      <div class="ai-cds-header">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
          <div class="ai-avatar-badge">
            🤖
            <span class="ai-online-dot"></span>
          </div>
          <div>
            <strong style="color: #f8fafc; font-size: 0.9rem; display: block; line-height: 1.2;">Trợ Lý AI CDS</strong>
            <span style="color: #10b981; font-size: 0.72rem; font-weight: 500;">● Đang hoạt động</span>
          </div>
        </div>
        <button id="closeAiCdsDrawerBtn" title="Thu gọn / Đóng" style="background: rgba(255,255,255,0.08); border: none; color: #cbd5e1; width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; cursor: pointer;">−</button>
      </div>

      <div id="aiCdsMessagesList" class="ai-cds-messages-list">
        <div style="text-align: center; color: #94a3b8; padding: 1.5rem; font-size: 0.8rem;">
          💬 Nhập câu hỏi bên dưới để chat với AI...
        </div>
      </div>

      <div class="ai-cds-footer">
        <input type="text" id="aiCdsInput" class="ai-cds-input-pill" placeholder="Hỏi AI y khoa..." onkeydown="if(event.key==='Enter'){event.preventDefault(); if(window.handleSendAiCds) window.handleSendAiCds();}" />
        <button type="button" id="sendAiCdsMsgBtn" class="ai-cds-send-btn" title="Gửi" onclick="if(window.handleSendAiCds) window.handleSendAiCds();">✈️</button>
      </div>`;
    document.body.appendChild(drawer);
  }

  let minFab = document.getElementById('aiCdsMinFab');
  if (!minFab) {
    minFab = document.createElement('button');
    minFab.id = 'aiCdsMinFab';
    minFab.title = 'Mở Trợ Lý AI CDS';
    minFab.innerHTML = '🤖';
    minFab.style.cssText = 'display: none; position: fixed; bottom: 1.5rem; right: 1.5rem; width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #0084ff, #a855f7); color: white; border: none; box-shadow: 0 10px 25px rgba(0, 132, 255, 0.6); cursor: pointer; font-size: 1.7rem; z-index: 999999; align-items: center; justify-content: center; transition: transform 0.2s;';
    document.body.appendChild(minFab);

    minFab.onmouseover = () => minFab.style.transform = 'scale(1.1)';
    minFab.onmouseout = () => minFab.style.transform = 'scale(1)';
  }

  const toggleBtn = document.getElementById('toggleAiCdsBtn');
  const globalFab = document.getElementById('globalAiCdsFab');
  const closeBtn = document.getElementById('closeAiCdsDrawerBtn');
  const messagesList = document.getElementById('aiCdsMessagesList');

  if (!drawer || !messagesList) return;

  // Clear previous chat messages from screen & reset input
  messagesList.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 1.5rem; font-size: 0.8rem;">💬 Nhập câu hỏi bên dưới để chat với AI...</div>';

  // Handle Minimize (Hide drawer, show small floating 🤖 FAB)
  if (closeBtn) {
    closeBtn.onclick = () => {
      drawer.style.setProperty('display', 'none', 'important');
      if (minFab) minFab.style.setProperty('display', 'flex', 'important');
    };
  }

  // Handle Expand (Hide small FAB, show main drawer)
  if (minFab) {
    minFab.onclick = () => {
      minFab.style.setProperty('display', 'none', 'important');
      drawer.style.setProperty('display', 'flex', 'important');
    };
  }

  const toggleDrawer = async () => {
    const isHidden = window.getComputedStyle(drawer).display === 'none';
    if (isHidden) {
      drawer.style.setProperty('display', 'flex', 'important');
      if (minFab) minFab.style.setProperty('display', 'none', 'important');
      try {
        await ensureConversation();
      } catch (e) {
        messagesList.innerHTML = '<div class="alert alert-error" style="font-size: 0.85rem;">Không thể kết nối Trợ lý AI.</div>';
      }
      messagesList.scrollTop = messagesList.scrollHeight;
    } else {
      drawer.style.setProperty('display', 'none', 'important');
      if (minFab) minFab.style.setProperty('display', 'flex', 'important');
    }
  };

  if (toggleBtn) toggleBtn.onclick = toggleDrawer;
  if (globalFab) globalFab.onclick = toggleDrawer;

  // Expose globally for inline onclick/onkeydown attributes
  window.handleSendAiCds = handleSend;

  // Direct element assignment
  const btnSendEl = document.getElementById('sendAiCdsMsgBtn');
  const inputMsgEl = document.getElementById('aiCdsInput');
  if (btnSendEl) btnSendEl.onclick = handleSend;
  if (inputMsgEl) {
    inputMsgEl.onkeydown = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSend();
      }
    };
  }

  // Global Event Delegation fallback to guarantee clicks/enters are NEVER missed
  if (!window._aiCdsEventsBound) {
    window._aiCdsEventsBound = true;
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('#sendAiCdsMsgBtn');
      if (btn) {
        e.preventDefault();
        handleSend();
      }
    });
    document.addEventListener('keydown', (e) => {
      if (e.target && e.target.id === 'aiCdsInput' && e.key === 'Enter') {
        e.preventDefault();
        handleSend();
      }
    });
  }
};

const renderAiCdsMessages = (conv) => {
  const messagesList = document.getElementById('aiCdsMessagesList');
  if (!messagesList || !conv) return;

  const msgs = conv.messages || [];
  const recs = conv.recommendations || [];

  if (msgs.length === 0) {
    messagesList.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 1.5rem; font-size: 0.85rem;">💬 Hãy đặt câu hỏi để bắt đầu tư vấn với AI.</div>';
    return;
  }

  messagesList.innerHTML = msgs.map(msg => {
    const isDoctor = msg.role === 'doctor';
    
    // Find recommendations attached to this message
    const msgRecs = recs.filter(r => r.message === msg.id || String(r.message) === String(msg.id));

    let recsHTML = '';
    if (msgRecs.length > 0) {
      recsHTML = msgRecs.map(r => {
        const isActed = r.doctor_action !== 'PENDING';
        const actionLabel = r.doctor_action === 'ACCEPTED' ? '✅ Đã chấp nhận' : r.doctor_action === 'IGNORED' ? '❌ Đã bỏ qua' : r.doctor_action;

        return `
          <div class="ai-cds-rec-card ${r.severity}">
            <div style="display: flex; justify-content: space-between; align-items: center; font-weight: 600; margin-bottom: 0.3rem; color: #f8fafc;">
              <span style="font-size: 0.85rem;">🎯 ${r.category_display || r.category}</span>
              <span class="badge ${r.severity === 'HIGH' || r.severity === 'CRITICAL' ? 'badge-error' : 'badge-warning'}" style="font-size: 0.7rem; padding: 0.15rem 0.5rem;">${r.severity_display || r.severity}</span>
            </div>
            <div style="color: #e2e8f0; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.88rem;">${r.summary}</div>
            ${r.explanation ? `<div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.5rem; line-height: 1.4;">${r.explanation}</div>` : ''}

            ${isActed ? `
              <div style="font-size: 0.75rem; color: #60a5fa; font-weight: 600; background: rgba(59,130,246,0.1); padding: 0.3rem 0.6rem; border-radius: 6px; display: inline-block;">${actionLabel}</div>
            ` : `
              <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                <button class="btn btn-sm act-rec-btn" data-id="${r.id}" data-action="ACCEPTED" style="padding: 0.3rem 0.8rem; font-size: 0.75rem; background: #10b981; color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer;">✓ Chấp nhận</button>
                <button class="btn btn-sm act-rec-btn" data-id="${r.id}" data-action="IGNORED" style="padding: 0.3rem 0.8rem; font-size: 0.75rem; background: #475569; color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer;">✕ Bỏ qua</button>
              </div>
            `}
          </div>
        `;
      }).join('');
    }

    const avatarHTML = isDoctor 
      ? `<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #0084ff, #00c6ff); display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; color: white; font-weight: 600;">👨‍⚕️</div>`
      : `<div style="width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #a855f7, #3b82f6); display: flex; align-items: center; justify-content: center; font-size: 0.85rem; flex-shrink: 0; color: white; font-weight: 600;">🤖</div>`;

    return `
      <div class="ai-cds-row ${isDoctor ? 'doctor' : 'assistant'}">
        ${avatarHTML}
        <div style="display: flex; flex-direction: column; max-width: 82%;">
          <div class="ai-cds-msg ${isDoctor ? 'doctor' : 'assistant'}">
            ${msg.content}
          </div>
          ${recsHTML}
        </div>
      </div>
    `;
  }).join('');

  // Bind Recommendation Action Listeners (Accept / Ignore)
  document.querySelectorAll('.act-rec-btn').forEach(btn => {
    btn.onclick = async (e) => {
      const recId = e.currentTarget.dataset.id;
      const action = e.currentTarget.dataset.action;

      try {
        await CDSAPI.actOnRecommendation(recId, action);
        if (currentCdsConversation) {
          const updatedConv = await CDSAPI.getConversation(currentCdsConversation.id);
          currentCdsConversation = updatedConv;
          renderAiCdsMessages(updatedConv);
        }
      } catch (err) {
        alert(getErrorMessage(err, 'Lỗi cập nhật phản hồi khuyến nghị.'));
      }
    };
  });

  messagesList.scrollTop = messagesList.scrollHeight;
};
