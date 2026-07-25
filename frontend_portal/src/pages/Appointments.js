import { Navbar } from '../components/Navbar.js';
import { AppointmentAPI, ProviderAPI, ConsultationAPI, MedicalRecordAPI, getUser, getErrorMessage } from '../api.js';

export const AppointmentsPage = () => {
  const user = getUser();
  const isDoctor = user && user.role === 'DOCTOR';

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">
            ${isDoctor ? '📥 Quản lý Yêu cầu Lịch hẹn Khám' : '📅 Lịch sử Hẹn khám'}
          </h1>
          <p class="text-muted" style="margin: 0;">
            ${isDoctor 
              ? 'Duyệt các yêu cầu đặt lịch hẹn mới từ bệnh nhân. Đồng ý/Xác nhận để nhận ca khám hoặc Từ chối/Hủy.' 
              : 'Theo dõi danh sách lịch hẹn khám đã đặt và trạng thái xử lý từ bác sĩ.'}
          </p>
        </div>
        ${isDoctor ? `
          <a href="#/doctor-schedule" class="btn btn-primary" style="white-space: nowrap; text-decoration: none; padding: 0.7rem 1.2rem; font-weight: 600;">
            📅 + Đăng Ký Ca Làm Việc
          </a>
        ` : ''}
      </div>

      <div class="glass-panel" style="padding: 2rem;">
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">
          ${isDoctor ? 'Danh sách Yêu cầu Hẹn khám Đang chờ Duyệt' : 'Danh sách Lịch hẹn của Bạn'}
        </h2>
        <div id="appointmentsList" class="dashboard-grid">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
            Đang tải danh sách lịch hẹn...
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Read-Only Detail & Medical Record Modal -->
    <div id="appointmentDetailModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center;">
      <div class="glass-panel" style="background: #1e293b; color: #f8fafc; padding: 2rem; max-width: 700px; width: 92%; max-height: 88vh; overflow-y: auto; border-radius: 12px; position: relative;">
        <button id="closeAptDetailModalBtn" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; font-size: 1.8rem; color: white; cursor: pointer;">&times;</button>
        <h2 style="color: var(--primary-blue); margin-bottom: 1rem;">📋 Kết Quả Bệnh Án & Chi Tiết Ca Khám (Chế độ Xem)</h2>
        <div id="aptDetailModalContent">Đang tải chi tiết...</div>
      </div>
    </div>
  `;
};

// Helper: Format strictly non-empty vital metrics & body info entered by doctor
const renderStrictVitalsAndBodyHTML = (vitalsList, foundRec) => {
  const v = Array.isArray(vitalsList) && vitalsList.length > 0 ? vitalsList[0] : vitalsList;
  const items = [];

  let heightVal = v?.height_cm || v?.height;
  let weightVal = v?.weight_kg || v?.weight;

  if (!heightVal && foundRec?.description) {
    const matchH = foundRec.description.match(/Chiều cao:\s*(\d+(?:\.\d+)?)\s*cm/i);
    if (matchH) heightVal = matchH[1];
  }
  if (!weightVal && foundRec?.description) {
    const matchW = foundRec.description.match(/Cân nặng:\s*(\d+(?:\.\d+)?)\s*kg/i);
    if (matchW) weightVal = matchW[1];
  }

  if (heightVal && heightVal !== '--' && String(heightVal).trim() !== '' && heightVal !== 0 && heightVal !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>📐 Chiều cao:</strong> ${heightVal} cm</div>`);
  }
  if (weightVal && weightVal !== '--' && String(weightVal).trim() !== '' && weightVal !== 0 && weightVal !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>⚖️ Cân nặng:</strong> ${weightVal} kg</div>`);
  }
  const t = v?.temperature_celsius || v?.temperature_c || v?.temperature;
  if (t && t !== '--' && String(t).trim() !== '' && t !== 0 && t !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>🌡️ Nhiệt độ:</strong> ${t} °C</div>`);
  }

  const sys = v?.blood_pressure_systolic;
  const dia = v?.blood_pressure_diastolic;
  const sysValid = sys && sys !== '--' && String(sys).trim() !== '' && sys !== 0 && sys !== '0';
  const diaValid = dia && dia !== '--' && String(dia).trim() !== '' && dia !== 0 && dia !== '0';

  if (sysValid && diaValid) {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>🩺 Huyết áp:</strong> ${sys}/${dia} mmHg</div>`);
  } else if (sysValid) {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>🩺 Huyết áp tâm thu:</strong> ${sys} mmHg</div>`);
  } else if (diaValid) {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>🩺 Huyết áp tâm trương:</strong> ${dia} mmHg</div>`);
  }

  const hr = v?.heart_rate || v?.heartRate;
  if (hr && hr !== '--' && String(hr).trim() !== '' && hr !== 0 && hr !== '0') {
    items.push(`<div style="background: rgba(255,255,255,0.05); padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);"><strong>❤️ Nhịp tim:</strong> ${hr} BPM</div>`);
  }

  if (items.length === 0) return null;
  return `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.6rem; margin-top: 0.4rem;">${items.join('')}</div>`;
};

export const attachAppointmentsListeners = async () => {
  const container = document.getElementById('appointmentsList');
  if (!container) return;

  const user = getUser();
  const isPatient = user && user.role === 'PATIENT';
  const isDoctor = user && user.role === 'DOCTOR';
  const isAdmin = user && user.role === 'ADMIN';

  // Detail Modal Handlers
  const aptDetailModal = document.getElementById('appointmentDetailModal');
  const closeAptDetailModalBtn = document.getElementById('closeAptDetailModalBtn');
  const aptDetailModalContent = document.getElementById('aptDetailModalContent');
  if (closeAptDetailModalBtn) closeAptDetailModalBtn.onclick = () => aptDetailModal.style.display = 'none';

  // Load Appointments List
  const loadAppointments = async () => {
    try {
      const data = await AppointmentAPI.getAppointments();
      const rawAppointments = data.data || data.results || data || [];
      let appointments = Array.isArray(rawAppointments) ? rawAppointments.filter(a => a.status !== 'CANCELLED') : [];
      
      // FOR DOCTOR: Show ONLY appointments that doctor hasn't confirmed or rejected yet (HELD, DRAFT, PAYMENT_PENDING)
      if (isDoctor) {
        appointments = appointments.filter(a => ['HELD', 'DRAFT', 'PAYMENT_PENDING'].includes(a.status));
      }

      if (appointments.length === 0) {
        const emptyMsg = isDoctor 
          ? 'Hiện chưa có yêu cầu hẹn khám mới nào đang chờ bạn duyệt.' 
          : 'Hiện bạn chưa có lịch hẹn khám nào.';
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">${emptyMsg}</div>`;
        return;
      }

      container.innerHTML = appointments.map(a => {
        const slot = a.slot_detail || {};
        const slotDate = slot.date || '';
        const startTimeStr = slot.start_time ? slot.start_time.substring(0, 5) : '';
        const endTimeStr = slot.end_time ? slot.end_time.substring(0, 5) : '';
        const timeDisplay = slotDate ? `${slotDate} (${startTimeStr} - ${endTimeStr})` : 'N/A';

        return `
          <div class="stat-card glass-panel appointment-card-item" data-id="${a.id}" data-patient="${a.patient_id || ''}" style="align-items: flex-start; position: relative; ${isDoctor ? 'cursor: pointer;' : ''}">
            <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.5rem;">
              <strong style="color: var(--primary-blue);">ID Lịch: ${a.id ? a.id.substring(0,8) : 'N/A'}</strong>
              <span class="badge ${a.status === 'CONFIRMED' ? 'badge-success' : a.status === 'COMPLETED' ? 'badge-info' : 'badge-warning'}">${a.status}</span>
            </div>

            <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Giờ hẹn đăng ký:</strong> <span style="color: var(--primary-blue); font-weight: 600;">${timeDisplay}</span></p>
            <p style="margin-bottom: 0.3rem; font-size: 0.9rem;"><strong>Mã Bệnh nhân:</strong> ${a.patient_id || 'N/A'}</p>
            <p style="margin-bottom: 0.3rem; font-size: 0.9rem;" class="text-muted"><strong>Lý do khám:</strong> ${a.reason_for_visit || 'Tư vấn sức khỏe'}</p>

            ${isDoctor ? `
              <div style="display: flex; gap: 0.5rem; width: 100%; margin-top: 1rem;">
                <button class="btn btn-primary btn-sm confirm-apt-btn" style="flex: 1; background: #10b981; border: none; font-weight: 600;" data-id="${a.id}">
                  ✓ Đồng ý / Xác nhận
                </button>
                <button class="btn btn-secondary btn-sm cancel-apt-btn" style="flex: 1; background: #fee2e2; color: #dc2626; border-color: #fca5a5; font-weight: 600;" data-id="${a.id}">
                  ✕ Từ chối / Hủy
                </button>
              </div>
            ` : ''}
          </div>
        `;
      }).join('');

      // Detail Modal (READ-ONLY Mode or Patient Navigation)
      const handleViewDetail = async (aptId, patientId) => {
        if (!aptId) return;

        if (isPatient) {
          window.location.hash = `#/consultations?aptId=${aptId}`;
          return;
        }

        const targetApt = appointments.find(a => String(a.id) === String(aptId)) || {};
        const slot = targetApt.slot_detail || {};
        const slotDate = slot.date ? `${slot.date} (${slot.start_time ? slot.start_time.substring(0,5) : ''} - ${slot.end_time ? slot.end_time.substring(0,5) : ''})` : 'N/A';

        aptDetailModal.style.display = 'flex';
        aptDetailModalContent.innerHTML = '<div style="text-align: center; padding: 2rem;">Đang tải dữ liệu ca khám...</div>';

        let records = [];
        let vitals = [];
        let consultations = [];
        let rxItems = [];

        if (patientId) {
          try {
            const [recRes, vitRes, csRes] = await Promise.all([
              MedicalRecordAPI.getRecords(patientId).catch(() => []),
              MedicalRecordAPI.getVitals(patientId).catch(() => []),
              ConsultationAPI.getConsultations().catch(() => [])
            ]);
            const toArr = (v) => Array.isArray(v) ? v : (v?.results || v?.data || []);
            records = toArr(recRes);
            vitals = toArr(vitRes);
            consultations = toArr(csRes);
          } catch (err) { console.error('Error fetching apt detail data:', err); }
        }

        const foundCs = consultations.find(c => String(c.appointment_id) === String(aptId));
        const foundRec = records.find(r => (r.notes && r.notes.includes(aptId)) || (r.description && r.description.includes(aptId))) || records[0];

        let detailedCs = foundCs;
        if (foundCs && foundCs.id) {
          try {
            const [fullCs, rxData] = await Promise.all([
              ConsultationAPI.getConsultation(foundCs.id).catch(() => foundCs),
              ConsultationAPI.getPrescriptions(foundCs.id).catch(() => ({ items: [] }))
            ]);
            detailedCs = fullCs || foundCs;
            rxItems = rxData ? (rxData.items || (Array.isArray(rxData) ? rxData : [])) : [];
          } catch (rErr) {}
        }

        const cn = detailedCs?.clinical_note || {};
        const subjective = cn.subjective || '';
        const objective = cn.objective || '';
        let assessment = cn.assessment || detailedCs?.diagnosis || foundRec?.title || foundRec?.diagnosis || '';

        if (assessment.startsWith('Chẩn đoán: ')) {
          assessment = assessment.replace('Chẩn đoán: ', '');
        }
        if (!assessment || assessment.trim() === '') {
          assessment = targetApt.reason_for_visit ? `Tư vấn & Đánh giá: ${targetApt.reason_for_visit}` : 'Chẩn đoán y khoa tổng quát (Theo dõi sức khỏe)';
        }

        let plan = cn.plan || foundRec?.description || '';

        if (plan && plan.includes(' | Thể trạng:')) plan = plan.split(' | Thể trạng:')[0];
        if (plan && plan.startsWith('Lời khuyên / Đơn thuốc: ')) plan = plan.replace('Lời khuyên / Đơn thuốc: ', '');

        const vitalsHTML = renderStrictVitalsAndBodyHTML(vitals, foundRec);

        aptDetailModalContent.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 1.2rem; font-size: 0.95rem;">
            <!-- Basic Appointment Info -->
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <strong style="color: var(--primary-blue); font-size: 1.05rem;">Mã Lịch Hẹn: ${targetApt.id || aptId}</strong>
                <span class="badge ${targetApt.status === 'CONFIRMED' ? 'badge-success' : targetApt.status === 'COMPLETED' ? 'badge-info' : 'badge-warning'}">${targetApt.status || 'N/A'}</span>
              </div>
              <p style="margin: 0.3rem 0;"><strong>Giờ khám hẹn:</strong> ${slotDate}</p>
              <p style="margin: 0.3rem 0;"><strong>Mã Bệnh nhân:</strong> ${patientId || targetApt.patient_id || 'N/A'}</p>
              <p style="margin: 0.3rem 0;" class="text-muted"><strong>Lý do khám:</strong> ${targetApt.reason_for_visit || 'Tư vấn sức khỏe'}</p>
            </div>

            <!-- READ-ONLY SOAP NOTE -->
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
              <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.6rem; font-size: 1.05rem;">📋 Ghi Chú Lâm Sàng (SOAP Note - Chế độ Chỉ xem)</h3>
              <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.92rem;">
                <div><strong style="color: #60a5fa;">S (Triệu chứng):</strong> ${subjective || 'Bệnh nhân khai báo lý do khám'}</div>
                <div><strong style="color: #60a5fa;">O (Khám thực thể):</strong> ${objective || 'Kết quả khám lâm sàng bình thường'}</div>
                <div><strong style="color: #60a5fa;">A (Chẩn đoán y khoa):</strong> <span style="color: #ffffff; font-weight: 600;">${assessment || 'Khám y khoa'}</span></div>
                <div><strong style="color: #60a5fa;">P (Lời khuyên & Phác đồ):</strong> ${plan || 'Theo dõi và tuân thủ hướng dẫn điều trị'}</div>
              </div>
            </div>

            <!-- READ-ONLY VITALS -->
            ${vitalsHTML ? `
              <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.6rem; font-size: 1.05rem;">📊 Chỉ Số Sinh Tồn & Thể Trạng Lúc Khám (Chỉ xem)</h3>
                ${vitalsHTML}
              </div>
            ` : ''}

            <!-- READ-ONLY PRESCRIPTION -->
            <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
              <h3 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 0.6rem; font-size: 1.05rem;">💊 Đơn Thuốc Điện Tử (Chỉ xem)</h3>
              ${rxItems.length === 0 ? '<p class="text-muted" style="margin: 0;">Chưa kê đơn thuốc.</p>' : `
                <ul style="padding-left: 1.2rem; margin: 0;">
                  ${rxItems.map(item => `
                    <li style="margin-bottom: 0.4rem; line-height: 1.4;">
                      <strong style="color: #f8fafc;">${item.drug_name}</strong> - Liều: ${item.dosage || '1 viên'} (${item.frequency || '2 lần/ngày'}) - ${item.duration_days || 5} ngày
                    </li>
                  `).join('')}
                </ul>
              `}
            </div>
          </div>
        `;
      };

      // Register detail click handlers
      document.querySelectorAll('.view-apt-detail-btn').forEach(btn => {
        btn.onclick = (e) => {
          e.stopPropagation();
          const aptId = e.currentTarget.dataset.id;
          const patientId = e.currentTarget.dataset.patient;
          handleViewDetail(aptId, patientId);
        };
      });

      document.querySelectorAll('.appointment-card-item').forEach(card => {
        card.onclick = (e) => {
          if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;
          const aptId = card.dataset.id;
          const patientId = card.dataset.patient;
          handleViewDetail(aptId, patientId);
        };
      });

      // Confirm (Accept Request) Handler
      document.querySelectorAll('.confirm-apt-btn').forEach(btn => {
        btn.onclick = async (e) => {
          e.stopPropagation();
          const aptId = e.currentTarget.dataset.id;
          try {
            await AppointmentAPI.confirmAppointment(aptId);
            alert('Đã đồng ý nhận lịch hẹn! Lịch hẹn đã chuyển sang trang Tư vấn & Khám.');
            loadAppointments();
          } catch (err) {
            alert(getErrorMessage(err, 'Lỗi xác nhận lịch hẹn.'));
          }
        };
      });

      // Cancel (Reject Request) Handler
      document.querySelectorAll('.cancel-apt-btn').forEach(btn => {
        btn.onclick = async (e) => {
          e.stopPropagation();
          const aptId = e.currentTarget.dataset.id;
          if (confirm('Từ chối / Hủy bỏ yêu cầu lịch hẹn này?')) {
            try {
              await AppointmentAPI.cancelAppointment(aptId);
              alert('Đã từ chối lịch hẹn.');
              loadAppointments();
            } catch (err) {
              alert(getErrorMessage(err, 'Lỗi hủy lịch hẹn.'));
            }
          }
        };
      });

    } catch (e) {
      container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">Không thể tải danh sách yêu cầu lịch hẹn.</div>`;
    }
  };

  loadAppointments();
};
