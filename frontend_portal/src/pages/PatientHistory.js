import { Navbar } from '../components/Navbar.js';
import { PatientAPI, MedicalRecordAPI, ConsultationAPI, AppointmentAPI, ProviderAPI, AuthAPI, getUser, getErrorMessage } from '../api.js';

export const PatientHistoryPage = () => {
  const user = getUser();
  const isPatient = user && user.role === 'PATIENT';
  const isDoctor = user && user.role === 'DOCTOR';
  const isAdmin = user && user.role === 'ADMIN';

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">
          ${isPatient 
            ? '📋 Lịch sử Khám bệnh Của Tôi (Timeline)' 
            : isDoctor 
            ? '📋 Danh sách Bệnh nhân Bác sĩ Đã khám' 
            : '👥 Quản lý Người dùng & Tài khoản Hệ thống'}
        </h1>
        <p class="text-muted">
          ${isPatient 
            ? 'Danh sách các ca khám bệnh của bạn được cập nhật theo thời gian. Bấm vào từng ca khám để xem chi tiết bệnh án và chỉ số sinh tồn lúc khám.' 
            : isDoctor 
            ? 'Danh sách các bệnh nhân đã từng đăng ký lịch hẹn hoặc thực hiện phiên khám bệnh với bác sĩ. Bác sĩ có thể xem chi tiết hồ sơ y tế & bệnh án.' 
            : 'Xem danh sách tất cả người dùng trong hệ thống (bao gồm Bệnh nhân và Bác sĩ) và xem các thông tin cá nhân cơ bản.'}
        </p>
      </div>

      ${isPatient ? `
        <!-- PATIENT CHRONOLOGICAL TIMELINE VIEW -->
        <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
          <h2 style="font-size: 1.4rem; color: var(--primary-blue); margin-bottom: 1rem;">1. Thông tin Bệnh nhân</h2>
          <div id="patientInfoContainer">Đang tải thông tin...</div>
        </div>

        <div class="glass-panel" style="padding: 2rem;">
          <h2 style="font-size: 1.4rem; color: var(--primary-blue); margin-bottom: 0.5rem;">2. Lịch sử Bệnh theo Thời gian (Timeline Ca Khám)</h2>
          <p class="text-muted" style="margin-bottom: 1.5rem; font-size: 0.9rem;">
            ℹ️ <em>Các ca khám bệnh được hệ thống tự động ghi nhận và cập nhật theo mốc thời gian. Bệnh nhân bấm vào từng ca khám để xem chi tiết bệnh lúc khám.</em>
          </p>
          <div id="patientTimelineContainer">Đang tải lịch sử ca khám...</div>
        </div>

        <!-- PATIENT SESSION DETAIL MODAL DIALOG -->
        <div id="patientSessionDetailModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center;">
          <div class="glass-panel" style="background: #1e293b; color: #f8fafc; padding: 2rem; max-width: 700px; width: 90%; max-height: 85vh; overflow-y: auto; border-radius: 12px; position: relative;">
            <button id="closePatientSessionModalBtn" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.8rem; color: white; cursor: pointer;">&times;</button>
            <h2 id="sessionModalTitle" style="color: var(--primary-blue); margin-bottom: 1rem;">🩺 Chi Tiết Bệnh Án Ca Khám</h2>
            <div id="sessionModalContent">Đang tải chi tiết...</div>
          </div>
        </div>
      ` : `
        <!-- DIRECTORY SEARCH PANEL (DOCTOR OR ADMIN) -->
        <div class="glass-panel" style="padding: 1.5rem; margin-bottom: 2rem;">
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-weight: bold; color: var(--primary-blue);">
              🔍 ${isDoctor ? 'Tìm kiếm Bệnh nhân đã khám' : 'Tìm kiếm Người dùng (Bệnh nhân & Bác sĩ)'}
            </label>
            <input type="text" id="searchDirectoryInput" class="form-input" placeholder="${isDoctor ? 'Nhập tên bệnh nhân hoặc số điện thoại...' : 'Nhập tên, email hoặc số điện thoại...'}" />
          </div>
        </div>

        <div class="glass-panel" style="padding: 2rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">
            ${isDoctor ? 'Danh sách Bệnh nhân Đã khám' : 'Danh sách Tất cả Người dùng Hệ thống'}
          </h2>
          <div id="directoryList" class="dashboard-grid">
            <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
              Đang tải danh sách...
            </div>
          </div>
        </div>

        <!-- DOCTOR MEDICAL HISTORY DETAIL MODAL -->
        <div id="patientDetailModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center;">
          <div class="glass-panel" style="background: #1e293b; color: #f8fafc; padding: 2rem; max-width: 850px; width: 92%; max-height: 90vh; overflow-y: auto; border-radius: 12px; position: relative;">
            <button id="closePatientModalBtn" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.8rem; color: white; cursor: pointer;">&times;</button>
            <h2 id="modalPatientTitle" style="color: var(--primary-blue); margin-bottom: 1rem;">📋 Hồ sơ Y tế & Chi tiết Bệnh án</h2>
            <div id="patientModalContent">Đang tải...</div>
          </div>
        </div>

        <!-- ADMIN BASIC USER INFO MODAL -->
        <div id="adminUserModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center;">
          <div class="glass-panel" style="background: #1e293b; color: #f8fafc; padding: 2rem; max-width: 550px; width: 90%; border-radius: 12px; position: relative;">
            <button id="closeAdminUserModalBtn" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.8rem; color: white; cursor: pointer;">&times;</button>
            <h2 style="color: var(--primary-blue); margin-bottom: 1rem;">👤 Thông tin Cá nhân Cơ bản Người dùng</h2>
            <div id="adminUserModalContent">Đang tải...</div>
          </div>
        </div>
      `}
    </div>
  `;
};

export const attachPatientHistoryListeners = async () => {
  const user = getUser();
  if (!user) return;

  const isPatient = user.role === 'PATIENT';
  const isDoctor = user.role === 'DOCTOR';
  const isAdmin = user.role === 'ADMIN';

  if (isPatient) {
    // 1. PATIENT VIEW: Chronological Timeline List & Detail Session Dialog
    const infoContainer = document.getElementById('patientInfoContainer');
    const timelineContainer = document.getElementById('patientTimelineContainer');
    const sessionModal = document.getElementById('patientSessionDetailModal');
    const closeSessionModalBtn = document.getElementById('closePatientSessionModalBtn');
    const sessionModalContent = document.getElementById('sessionModalContent');

    if (!infoContainer) return;
    if (closeSessionModalBtn) closeSessionModalBtn.onclick = () => sessionModal.style.display = 'none';

    try {
      const patientProfile = await PatientAPI.getMe();
      if (!patientProfile) {
        infoContainer.innerHTML = '<div class="alert alert-error">Chưa cập nhật thông tin hồ sơ bệnh nhân.</div>';
        return;
      }

      infoContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; background: rgba(255,255,255,0.03); padding: 1.2rem; border-radius: 8px;">
          <div><strong>Họ và tên:</strong> ${patientProfile.first_name || ''} ${patientProfile.last_name || ''}</div>
          <div><strong>Ngày sinh:</strong> ${patientProfile.date_of_birth || 'N/A'}</div>
          <div><strong>Giới tính:</strong> ${patientProfile.gender === 'M' ? 'Nam' : patientProfile.gender === 'F' ? 'Nữ' : 'Khác'}</div>
          <div><strong>Số điện thoại:</strong> ${patientProfile.contact_number || patientProfile.phone || 'N/A'}</div>
          <div><strong>Địa chỉ:</strong> ${patientProfile.address || 'N/A'}</div>
          <div><strong>Liên hệ khẩn cấp:</strong> ${patientProfile.emergency_contact || 'N/A'}</div>
        </div>
      `;

      // Load Consultations, Medical Records & Appointments into Timeline
      const pId = patientProfile.id;
      const uId = patientProfile.user_id;

      const [csRes, recRes1, recRes2, aptRes, vitalsRes1, vitalsRes2] = await Promise.all([
        ConsultationAPI.getConsultations().catch(() => []),
        pId ? MedicalRecordAPI.getRecords(pId).catch(() => []) : Promise.resolve([]),
        uId ? MedicalRecordAPI.getRecords(uId).catch(() => []) : Promise.resolve([]),
        AppointmentAPI.getAppointments().catch(() => []),
        pId ? MedicalRecordAPI.getVitals(pId).catch(() => []) : Promise.resolve([]),
        uId ? MedicalRecordAPI.getVitals(uId).catch(() => []) : Promise.resolve([])
      ]);

      // Helper: extract array from any response shape
      const toArr = (v) => Array.isArray(v) ? v : (v?.results || v?.data || []);

      const rawCs = toArr(csRes);
      const rawRecs1 = toArr(recRes1);
      const rawRecs2 = toArr(recRes2);
      const rawApts = toArr(aptRes);
      const rawVitals1 = toArr(vitalsRes1);
      const rawVitals2 = toArr(vitalsRes2);

      console.log('[PatientHistory] rawCs:', rawCs.length, 'rawRecs:', rawRecs1.length + rawRecs2.length, 'rawApts:', rawApts.length, 'rawVitals:', rawVitals1.length + rawVitals2.length);

      // Combine records & vitals (deduplicate by ID)
      const recordsMap = new Map();
      [...rawRecs1, ...rawRecs2].forEach(r => { if (r && r.id) recordsMap.set(r.id, r); });
      const records = Array.from(recordsMap.values());

      const vitalsMap = new Map();
      [...rawVitals1, ...rawVitals2].forEach(v => { if (v && v.id) vitalsMap.set(v.id, v); });
      const vitals = Array.from(vitalsMap.values());

      const patientApptIds = new Set(rawApts.map(a => String(a.id)));

      // Combine into timeline entries
      const timelineEntries = [];
      const processedIds = new Set();

      // 1. Medical Records (chẩn đoán bác sĩ đã điền khi hoàn tất khám)
      records.forEach(r => {
        if (r && r.id && !processedIds.has(r.id)) {
          processedIds.add(r.id);
          timelineEntries.push({
            id: r.id,
            type: 'RECORD',
            date: new Date(r.created_at || Date.now()),
            dateStr: r.created_at ? new Date(r.created_at).toLocaleString() : 'N/A',
            title: r.title || `Bệnh Án Y Khoa: ${r.diagnosis || 'Khám y khoa'}`,
            summary: r.description || r.treatment_plan || r.notes || 'Chưa có phác đồ',
            advice: r.description || r.treatment_plan || r.notes,
            raw: r
          });
        }
      });

      // 3. Completed Appointments (including b4aa9e63)
      rawApts.forEach(a => {
        if (a && a.id && a.status === 'COMPLETED' && !processedIds.has(`apt-${a.id}`)) {
          processedIds.add(`apt-${a.id}`);
          const slot = a.slot_detail || {};
          const slotDate = slot.date ? `${slot.date} ${slot.start_time ? slot.start_time.substring(0,5) : ''}` : '';
          
          // Match Medical Record or Consultation for this appointment
          const foundRec = records.find(rec => (rec.notes && rec.notes.includes(a.id)) || (rec.title && rec.title.trim() !== ''));
          const foundCs = rawCs.find(cs => String(cs.appointment_id) === String(a.id));

          let aptDiag = '';
          let aptAdvice = '';
          if (foundRec) {
            aptDiag = foundRec.title || foundRec.diagnosis;
            aptAdvice = foundRec.description || foundRec.treatment_plan;
          } else if (foundCs) {
            const cn = foundCs.clinical_note || {};
            aptDiag = cn.assessment || cn.subjective || foundCs.clinical_notes || foundCs.diagnosis;
            aptAdvice = cn.plan || foundCs.prescription?.notes;
          }

          const finalDiag = aptDiag || (a.reason_for_visit ? `Khám theo hẹn: ${a.reason_for_visit}` : 'Ca khám bệnh theo hẹn đã hoàn thành');

          timelineEntries.push({
            id: a.id,
            type: 'APPOINTMENT',
            date: new Date(slot.date ? `${slot.date}T${slot.start_time || '00:00:00'}` : (a.created_at || Date.now())),
            dateStr: slotDate || (a.created_at ? new Date(a.created_at).toLocaleString() : 'N/A'),
            title: `Lịch Hẹn Khám Hoàn Tất: ${finalDiag}`,
            summary: finalDiag,
            advice: aptAdvice || 'Thực hiện theo chỉ dẫn và lời khuyên của bác sĩ.',
            raw: a
          });
        }
      });

      // Sort descending by date
      timelineEntries.sort((a, b) => b.date - a.date);

      if (timelineEntries.length === 0) {
        timelineContainer.innerHTML = '<p class="text-muted" style="text-align: center; padding: 2rem;">Chưa có lịch sử ca khám nào được ghi nhận trên hệ thống.</p>';
        return;
      }

      timelineContainer.innerHTML = `
        <div style="position: relative; padding-left: 2rem; border-left: 3px solid var(--primary-blue);">
          ${timelineEntries.map((item, idx) => `
            <div style="position: relative; margin-bottom: 2rem;">
              <div style="position: absolute; left: -2.65rem; top: 0; width: 1.2rem; height: 1.2rem; background: var(--primary-blue); border-radius: 50%; border: 3px solid #1e293b;"></div>
              
              <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 1.2rem; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                  <strong style="color: var(--primary-blue); font-size: 1.1rem;">${item.title}</strong>
                  <span class="badge badge-info">${item.dateStr}</span>
                </div>
                <p style="margin-bottom: 0.8rem; font-size: 0.95rem;"><strong>Chẩn đoán / Nội dung khám:</strong> ${item.summary}</p>
                
                <button class="btn btn-primary btn-sm view-patient-session-btn" data-index="${idx}" style="background: var(--primary-blue);">
                  👁️ Xem Chi Tiết Bệnh Lúc Khám
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      `;

      document.querySelectorAll('.view-patient-session-btn').forEach(btn => {
        btn.onclick = (e) => {
          const idx = e.currentTarget.dataset.index;
          const entry = timelineEntries[idx];
          if (!entry) return;

          sessionModal.style.display = 'flex';
          const r = entry.raw || {};

          const diagnosisDisplay = entry.summary || 'Ghi nhận ca khám y khoa';
          const adviceDisplay = entry.advice || 'Thực hiện theo chỉ dẫn của bác sĩ.';

          let vitalsHTML = '<p class="text-muted" style="margin: 0.2rem 0; font-size: 0.9rem;">Chưa có dữ liệu sinh tồn lúc khám.</p>';
          if (vitals.length > 0) {
            const v = vitals[0];
            const vItems = [];

            const h = v.height_cm || v.height;
            if (h !== null && h !== undefined && String(h).trim() !== '' && h !== '--' && h !== 0 && h !== '0') {
              vItems.push(`<strong>Chiều cao:</strong> ${h} cm`);
            }
            const w = v.weight_kg || v.weight;
            if (w !== null && w !== undefined && String(w).trim() !== '' && w !== '--' && w !== 0 && w !== '0') {
              vItems.push(`<strong>Cân nặng:</strong> ${w} kg`);
            }
            const t = v.temperature_celsius || v.temperature_c || v.temperature;
            if (t !== null && t !== undefined && String(t).trim() !== '' && t !== '--' && t !== 0 && t !== '0') {
              vItems.push(`<strong>Nhiệt độ:</strong> ${t} °C`);
            }
            const sys = v.blood_pressure_systolic;
            const dia = v.blood_pressure_diastolic;
            const sysValid = sys !== null && sys !== undefined && String(sys).trim() !== '' && sys !== '--' && sys !== 0 && sys !== '0';
            const diaValid = dia !== null && dia !== undefined && String(dia).trim() !== '' && dia !== '--' && dia !== 0 && dia !== '0';

            if (sysValid && diaValid) {
              vItems.push(`<strong>Huyết áp:</strong> ${sys}/${dia} mmHg`);
            } else if (sysValid) {
              vItems.push(`<strong>Huyết áp tâm thu:</strong> ${sys} mmHg`);
            } else if (diaValid) {
              vItems.push(`<strong>Huyết áp tâm trương:</strong> ${dia} mmHg`);
            }
            const hr = v.heart_rate || v.heartRate;
            if (hr !== null && hr !== undefined && String(hr).trim() !== '' && hr !== '--' && hr !== 0 && hr !== '0') {
              vItems.push(`<strong>Nhịp tim:</strong> ${hr} BPM`);
            }

            if (vItems.length > 0) {
              vitalsHTML = `
                <div style="background: rgba(255,255,255,0.05); padding: 0.8rem; border-radius: 6px; font-size: 0.9rem; margin-top: 0.4rem; display: flex; flex-wrap: wrap; gap: 1rem;">
                  ${vItems.map(item => `<div>${item}</div>`).join('')}
                </div>
              `;
            } else {
              vitalsHTML = '<p class="text-muted" style="margin: 0.2rem 0; font-size: 0.9rem;">Bác sĩ không nhập chỉ số sinh tồn trong ca khám này.</p>';
            }
          }

          sessionModalContent.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 1rem; font-size: 0.95rem;">
              <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <p style="margin: 0.3rem 0;"><strong>Thời gian khám:</strong> <span style="color: var(--primary-blue); font-weight: 600;">${entry.dateStr}</span></p>
                <p style="margin: 0.3rem 0;"><strong>Mã ca khám / Lịch hẹn:</strong> ${entry.id}</p>
              </div>

              <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.5rem; font-size: 1.05rem;">🩺 Chẩn đoán & Kết luận Y khoa Bác sĩ đã điền</h3>
                <p style="margin: 0; font-size: 1rem; line-height: 1.5; color: #f8fafc;">${diagnosisDisplay}</p>
              </div>

              <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.5rem; font-size: 1.05rem;">📊 Chỉ số Sinh tồn (Vitals Lúc Khám)</h3>
                ${vitalsHTML}
              </div>

              <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.5rem; font-size: 1.05rem;">💊 Phác đồ / Lời khuyên Bác sĩ & Đơn thuốc</h3>
                <p style="margin: 0; color: #f8fafc;">${adviceDisplay}</p>
              </div>
            </div>
          `;
        };
      });

    } catch (err) {
      if (timelineContainer) timelineContainer.innerHTML = `<div class="alert alert-error">${getErrorMessage(err, 'Lỗi tải lịch sử bệnh.')}</div>`;
    }

  } else if (isDoctor) {
    // 2. DOCTOR VIEW: Only Patients Examined by This Doctor
    const directoryList = document.getElementById('directoryList');
    const searchInput = document.getElementById('searchDirectoryInput');
    const modal = document.getElementById('patientDetailModal');
    const closeModalBtn = document.getElementById('closePatientModalBtn');
    const modalContent = document.getElementById('patientModalContent');

    if (!directoryList) return;
    if (closeModalBtn) closeModalBtn.onclick = () => modal.style.display = 'none';

    let examinedPatients = [];

    const loadDoctorPatients = async () => {
      try {
        let doctorProviderId = null;
        try {
          const doctorProv = await ProviderAPI.getMe();
          if (doctorProv) doctorProviderId = doctorProv.id;
        } catch (e) {}

        const [csRes, apptRes, allPatientsRes] = await Promise.all([
          ConsultationAPI.getConsultations().catch(() => ({ results: [] })),
          AppointmentAPI.getAppointments().catch(() => ({ data: [] })),
          PatientAPI.getPatients().catch(() => ({ data: [] }))
        ]);

        const rawCs = csRes.results || csRes || [];
        const rawAppts = apptRes.data || apptRes.results || apptRes || [];
        const allPatients = allPatientsRes.data || allPatientsRes.results || allPatientsRes || [];

        const examinedPatientIds = new Set();

        rawCs.forEach(c => {
          if (!doctorProviderId || String(c.provider_id) === String(doctorProviderId)) {
            if (c.patient_id) examinedPatientIds.add(String(c.patient_id));
          }
        });

        rawAppts.forEach(a => {
          if (!doctorProviderId || String(a.provider_id) === String(doctorProviderId)) {
            if (a.patient_id) examinedPatientIds.add(String(a.patient_id));
          }
        });

        examinedPatients = allPatients.filter(p => examinedPatientIds.has(String(p.id)) || examinedPatientIds.has(String(p.user_id)));

        renderDoctorPatientCards(examinedPatients);
      } catch (err) {
        directoryList.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Không thể tải danh sách bệnh nhân đã khám.</div>`;
      }
    };

    const renderDoctorPatientCards = (list) => {
      if (!Array.isArray(list) || list.length === 0) {
        directoryList.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Bác sĩ chưa có phiên khám hoặc lịch hẹn nào với bệnh nhân.</div>`;
        return;
      }

      directoryList.innerHTML = list.map(p => `
        <div class="stat-card glass-panel" style="align-items: flex-start; position: relative;">
          <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.5rem;">
            <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin: 0;">Bệnh nhân: ${p.first_name || ''} ${p.last_name || ''}</h3>
            <span class="badge badge-info">${p.gender === 'M' ? 'Nam' : p.gender === 'F' ? 'Nữ' : 'Khác'}</span>
          </div>
          <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Ngày sinh:</strong> ${p.date_of_birth || 'N/A'}</p>
          <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Số điện thoại:</strong> ${p.contact_number || p.phone || 'N/A'}</p>
          <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Địa chỉ:</strong> ${p.address || 'N/A'}</p>
          <p style="margin-bottom: 1rem; font-size: 0.85rem;" class="text-muted">Liên hệ khẩn cấp: ${p.emergency_contact || 'N/A'}</p>

          <button class="btn btn-primary btn-sm view-doctor-patient-btn" style="width: 100%; margin-top: auto;" data-id="${p.id}" data-user-id="${p.user_id}" data-name="${p.first_name || ''} ${p.last_name || ''}">
            👁️ Xem Lịch sử Bệnh & Hồ sơ Y tế
          </button>
        </div>
      `).join('');

      document.querySelectorAll('.view-doctor-patient-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const pId = e.currentTarget.dataset.id;
          const uId = e.currentTarget.dataset.userId;
          const pName = e.currentTarget.dataset.name;

          modal.style.display = 'flex';
          modalContent.innerHTML = '<p class="text-muted" style="padding: 2rem; text-align: center;">Đang tải hồ sơ bệnh án & chi tiết y tế...</p>';
          document.getElementById('modalPatientTitle').textContent = `📋 Hồ sơ Y tế & Bệnh án: Bệnh nhân ${pName}`;

          try {
            const pProfile = await PatientAPI.getProfile(pId).catch(() => ({ id: pId, first_name: pName, user_id: uId }));
            
            modalContent.innerHTML = `
              <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">1. Thông tin Hành chính</h3>
                  <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; font-size: 0.9rem;">
                    <div><strong>Họ và tên:</strong> ${pProfile.first_name || ''} ${pProfile.last_name || ''}</div>
                    <div><strong>Ngày sinh:</strong> ${pProfile.date_of_birth || 'N/A'}</div>
                    <div><strong>Giới tính:</strong> ${pProfile.gender === 'M' ? 'Nam' : pProfile.gender === 'F' ? 'Nữ' : 'Khác'}</div>
                    <div><strong>Số điện thoại:</strong> ${pProfile.contact_number || pProfile.phone || 'N/A'}</div>
                    <div><strong>Địa chỉ:</strong> ${pProfile.address || 'N/A'}</div>
                    <div><strong>Liên hệ khẩn cấp:</strong> ${pProfile.emergency_contact || 'N/A'}</div>
                  </div>
                </div>

                <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">2. Chỉ số Sinh tồn gần đây (Vitals)</h3>
                  <div id="modalVitals">Đang tải...</div>
                </div>

                <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">3. Tiền sử Y tế & Chuyên môn</h3>
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                      <strong style="color: var(--primary-blue);">⚠️ Dị ứng (Allergies):</strong>
                      <div id="modalAllergies" style="margin-top: 0.4rem;">Đang tải...</div>
                    </div>
                    <div>
                      <strong style="color: var(--primary-blue);">🩺 Bệnh nền (Conditions):</strong>
                      <div id="modalConditions" style="margin-top: 0.4rem;">Đang tải...</div>
                    </div>
                  </div>
                  <div style="margin-top: 1rem;">
                    <strong style="color: var(--primary-blue);">💊 Thuốc đang sử dụng (Current Medications):</strong>
                    <div id="modalMedications" style="margin-top: 0.4rem;">Đang tải...</div>
                  </div>
                </div>

                <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">4. Lịch sử Các phiên Khám bệnh</h3>
                  <div id="modalConsultations">Đang tải...</div>
                </div>

                <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                  <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-top: 0; margin-bottom: 0.8rem;">5. File Tài liệu & Kết quả Xét nghiệm</h3>
                  <div id="modalDocuments">Đang tải...</div>
                </div>
              </div>
            `;

            populateModalMedicalHistory(pId, uId);
          } catch (mErr) {
            modalContent.innerHTML = `<div class="alert alert-error">Không thể tải hồ sơ chi tiết bệnh nhân.</div>`;
          }
        };
      });
    };

    if (searchInput) {
      searchInput.oninput = (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (!query) {
          renderDoctorPatientCards(examinedPatients);
        } else {
          const filtered = examinedPatients.filter(p => {
            const name = `${p.first_name || ''} ${p.last_name || ''}`.toLowerCase();
            const phone = (p.contact_number || p.phone || '').toLowerCase();
            return name.includes(query) || phone.includes(query);
          });
          renderDoctorPatientCards(filtered);
        }
      };
    }

    loadDoctorPatients();

  } else if (isAdmin) {
    // 3. ADMIN VIEW: All System Users (Patients & Doctors) with BASIC PERSONAL INFO ONLY
    const directoryList = document.getElementById('directoryList');
    const searchInput = document.getElementById('searchDirectoryInput');
    const adminModal = document.getElementById('adminUserModal');
    const closeAdminModalBtn = document.getElementById('closeAdminUserModalBtn');
    const adminModalContent = document.getElementById('adminUserModalContent');

    if (!directoryList) return;
    if (closeAdminModalBtn) closeAdminModalBtn.onclick = () => adminModal.style.display = 'none';

    let allUsers = [];

    const loadAdminUsersDirectory = async () => {
      try {
        const res = await AuthAPI.getUsers();
        allUsers = res.results || res.data || res || [];
        renderAdminUserCards(allUsers);
      } catch (err) {
        directoryList.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Không thể tải danh sách người dùng hệ thống.</div>`;
      }
    };

    const renderAdminUserCards = (list) => {
      if (!Array.isArray(list) || list.length === 0) {
        directoryList.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">Chưa có tài khoản người dùng nào.</div>`;
        return;
      }

      directoryList.innerHTML = list.map(u => {
        const roles = u.roles || (u.role ? [u.role] : ['PATIENT']);
        const primaryRole = roles[0] || 'PATIENT';
        const roleLabel = primaryRole === 'PATIENT' ? 'Bệnh nhân' : primaryRole === 'DOCTOR' ? 'Bác sĩ' : 'Quản trị viên';
        const badgeClass = primaryRole === 'ADMIN' ? 'badge-error' : primaryRole === 'DOCTOR' ? 'badge-success' : 'badge-info';

        return `
          <div class="stat-card glass-panel" style="align-items: flex-start; position: relative;">
            <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.5rem;">
              <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin: 0;">${u.last_name || u.first_name ? `${u.first_name || ''} ${u.last_name || ''}` : u.email}</h3>
              <span class="badge ${badgeClass}">${roleLabel}</span>
            </div>
            <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Email:</strong> ${u.email || 'N/A'}</p>
            <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>SĐT:</strong> ${u.phone || u.contact_number || 'N/A'}</p>
            <p style="margin-bottom: 1rem; font-size: 0.85rem;" class="text-muted">Trạng thái tài khoản: <span style="color: #10b981; font-weight: 600;">HOẠT ĐỘNG</span></p>

            <button class="btn btn-secondary btn-sm view-admin-user-btn" style="width: 100%; margin-top: auto;" data-id="${u.id}" data-email="${u.email}" data-role="${roleLabel}" data-name="${u.first_name || ''} ${u.last_name || ''}">
              👁️ Xem Thông tin Cá nhân Cơ bản
            </button>
          </div>
        `;
      }).join('');

      document.querySelectorAll('.view-admin-user-btn').forEach(btn => {
        btn.onclick = (e) => {
          const uEmail = e.currentTarget.dataset.email;
          const uRole = e.currentTarget.dataset.role;
          const uName = e.currentTarget.dataset.name;

          adminModal.style.display = 'flex';
          adminModalContent.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); font-size: 0.95rem;">
              <p style="margin: 0.5rem 0;"><strong>Họ và tên:</strong> ${uName || 'Chưa cập nhật'}</p>
              <p style="margin: 0.5rem 0;"><strong>Email tài khoản:</strong> ${uEmail}</p>
              <p style="margin: 0.5rem 0;"><strong>Vai trò hệ thống:</strong> <span class="badge badge-info">${uRole}</span></p>
              <p style="margin: 0.5rem 0;"><strong>Trạng thái tài khoản:</strong> <span style="color: #10b981; font-weight: 600;">Đang hoạt động (Active)</span></p>
              <hr style="border-color: rgba(255,255,255,0.1); margin: 1rem 0;" />
              <p class="text-muted" style="margin: 0; font-size: 0.85rem;">
                ℹ️ <em>Quản trị viên (Admin) chỉ quản lý tài khoản người dùng và xem thông tin cá nhân cơ bản (Bảo mật quyền riêng tư bệnh án).</em>
              </p>
            </div>
          `;
        };
      });
    };

    if (searchInput) {
      searchInput.oninput = (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (!query) {
          renderAdminUserCards(allUsers);
        } else {
          const filtered = allUsers.filter(u => {
            const name = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase();
            const email = (u.email || '').toLowerCase();
            const phone = (u.phone || '').toLowerCase();
            return name.includes(query) || email.includes(query) || phone.includes(query);
          });
          renderAdminUserCards(filtered);
        }
      };
    }

    loadAdminUsersDirectory();
  }
};

// Helper: Populate Vitals, History, Consultations & Documents in Doctor Modal
const populateModalMedicalHistory = async (patientId, userId, targetElements = {}) => {
  const vList = targetElements.vitalsList || document.getElementById('modalVitals');
  const aList = targetElements.allergiesList || document.getElementById('modalAllergies');
  const cList = targetElements.conditionsList || document.getElementById('modalConditions');
  const mList = targetElements.medicationsList || document.getElementById('modalMedications');
  const csList = targetElements.consultationsList || document.getElementById('modalConsultations');
  const dList = targetElements.documentsList || document.getElementById('modalDocuments');

  if (vList) {
    try {
      const vData = await MedicalRecordAPI.getVitals(userId || patientId);
      const list = vData.results || vData || [];
      if (list.length === 0) {
        vList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.9rem;">Chưa ghi nhận chỉ số sinh tồn nào.</p>';
      } else {
        vList.innerHTML = list.map(v => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.6rem 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; font-size: 0.88rem; display: flex; justify-content: space-between;">
            <div>
              <strong>Chiều cao:</strong> ${v.height_cm || 'N/A'} cm | 
              <strong>Cân nặng:</strong> ${v.weight_kg || 'N/A'} kg | 
              <strong>Huyết áp:</strong> ${v.blood_pressure_systolic || '--'}/${v.blood_pressure_diastolic || '--'} mmHg | 
              <strong>Nhịp tim:</strong> ${v.heart_rate || '--'} BPM
            </div>
            <small class="text-muted">${v.recorded_at ? new Date(v.recorded_at).toLocaleDateString() : ''}</small>
          </div>
        `).join('');
      }
    } catch (e) {
      vList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.9rem;">Chưa có chỉ số sinh tồn.</p>';
    }
  }

  if (aList) {
    try {
      const aData = await PatientAPI.getAllergies(patientId);
      const list = aData.results || aData || [];
      if (list.length === 0) {
        aList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Không ghi nhận dị ứng.</p>';
      } else {
        aList.innerHTML = list.map(a => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem; font-size: 0.85rem;">
            <strong>${a.allergen}</strong> - <span class="badge badge-warning">${a.severity}</span>
          </div>
        `).join('');
      }
    } catch (e) {
      aList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Chưa có dữ liệu dị ứng.</p>';
    }
  }

  if (cList) {
    try {
      const cData = await PatientAPI.getConditions(patientId);
      const list = cData.results || cData || [];
      if (list.length === 0) {
        cList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Không ghi nhận bệnh nền.</p>';
      } else {
        cList.innerHTML = list.map(c => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem; font-size: 0.85rem;">
            <strong>${c.condition_name}</strong> (${c.diagnosis_date || 'N/A'})
          </div>
        `).join('');
      }
    } catch (e) {
      cList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Chưa có dữ liệu bệnh nền.</p>';
    }
  }

  if (mList) {
    try {
      const mData = await PatientAPI.getMedications(patientId);
      const list = mData.results || mData || [];
      if (list.length === 0) {
        mList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Không ghi nhận thuốc đang dùng.</p>';
      } else {
        mList.innerHTML = list.map(m => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem; font-size: 0.85rem;">
            <strong>${m.medication_name}</strong> - Liều: ${m.dosage || 'N/A'}
          </div>
        `).join('');
      }
    } catch (e) {
      mList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.85rem;">Chưa có dữ liệu thuốc.</p>';
    }
  }

  if (csList) {
    try {
      const csData = await ConsultationAPI.getConsultations();
      const rawList = csData.results || csData || [];
      const list = rawList.filter(cs => String(cs.patient_id) === String(patientId) || String(cs.patient_id) === String(userId));
      
      if (list.length === 0) {
        csList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.9rem;">Chưa có lịch sử phiên khám bệnh nào.</p>';
      } else {
        csList.innerHTML = list.map(cs => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 6px; margin-bottom: 0.5rem; font-size: 0.88rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
              <strong style="color: var(--primary-blue);">Phiên khám ID: ${cs.id ? cs.id.substring(0,8) : 'N/A'}</strong>
              <span class="badge badge-info">${cs.status || 'COMPLETED'}</span>
            </div>
            <p style="margin: 0.2rem 0;"><strong>Chẩn đoán:</strong> ${cs.clinical_notes || cs.diagnosis || 'Khám sức khỏe tổng quát'}</p>
            <small class="text-muted">Ngày khám: ${cs.created_at ? new Date(cs.created_at).toLocaleString() : ''}</small>
          </div>
        `).join('');
      }
    } catch (e) {
      csList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.9rem;">Chưa có dữ liệu phiên khám.</p>';
    }
  }

  if (dList) {
    try {
      const dData = await MedicalRecordAPI.getRecords(userId || patientId);
      const list = dData.results || dData || [];
      if (list.length === 0) {
        dList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.9rem;">Chưa có file tài liệu hoặc kết quả xét nghiệm nào.</p>';
      } else {
        dList.innerHTML = list.map(d => `
          <div style="background: rgba(255,255,255,0.03); padding: 0.6rem 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; font-size: 0.88rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong>${d.record_type || 'Tài liệu y tế'}</strong>: ${d.description || 'N/A'}
            </div>
            ${d.document_url ? `<a href="${d.document_url}" target="_blank" style="color: var(--primary-blue);">Xem file</a>` : ''}
          </div>
        `).join('');
      }
    } catch (e) {
      dList.innerHTML = '<p class="text-muted" style="margin: 0; font-size: 0.9rem;">Chưa có tài liệu đính kèm.</p>';
    }
  }
};
