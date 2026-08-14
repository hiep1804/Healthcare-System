import { Navbar } from '../components/Navbar.js';
import { AppointmentAPI, ProviderAPI, getUser, getErrorMessage } from '../api.js';

export const DoctorSchedulePage = () => {
  const user = getUser();
  const isDoctor = user && user.role === 'DOCTOR';

  if (!isDoctor) {
    return `
      ${Navbar()}
      <div class="container" style="padding-top: 4rem; text-align: center;">
        <h1>403 Forbidden</h1>
        <p>Trang này chỉ dành cho Bác sĩ đăng ký ca làm việc.</p>
        <p><a href="#/">Quay lại Bảng điều khiển</a></p>
      </div>
    `;
  }

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">📅 Đăng Ký Lịch & Ca Làm Việc Bác Sĩ</h1>
        <p class="text-muted">Đăng ký các khoảng thời gian làm việc để hệ thống tự động sinh các slot khám bệnh cho bệnh nhân đặt lịch.</p>
      </div>

      <div class="glass-panel" style="padding: 2.5rem; max-width: 800px; margin: 0 auto;">
        <h2 style="font-size: 1.4rem; color: var(--primary-blue); margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.8rem;">
          ⏰ Đăng Ký Khung Giờ Làm Việc Tùy Chọn
        </h2>

        <form id="doctorScheduleForm">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.2rem;">
            <div class="form-group">
              <label class="form-label" style="font-weight: 600;">📅 Ngày Bắt Đầu Làm Việc</label>
              <input type="date" id="startDateInput" class="form-input" required style="padding: 0.8rem;" />
            </div>
            <div class="form-group">
              <label class="form-label" style="font-weight: 600;">📅 Ngày Kết Thúc Làm Việc</label>
              <input type="date" id="endDateInput" class="form-input" required style="padding: 0.8rem;" />
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
            <div class="form-group">
              <label class="form-label" style="font-weight: 600;">⏰ Giờ Bắt Đầu (Ví dụ: 08:00, 13:30...)</label>
              <input type="time" id="startTimeInput" class="form-input" value="08:00" required style="padding: 0.8rem;" />
            </div>
            <div class="form-group">
              <label class="form-label" style="font-weight: 600;">⏰ Giờ Kết Thúc (Ví dụ: 12:00, 17:30...)</label>
              <input type="time" id="endTimeInput" class="form-input" value="17:00" required style="padding: 0.8rem;" />
            </div>
          </div>

          <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(96, 165, 250, 0.3); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 0.9rem; color: #93c5fd;">
            💡 <strong>Lưu ý:</strong> Số phút đăng ký phải là <code>:00</code> hoặc <code>:30</code> (Ví dụ: 08:00, 08:30). Mỗi slot khám mặc định dài 30 phút.
          </div>

          <button type="submit" id="submitScheduleBtn" class="btn btn-primary" style="width: 100%; padding: 0.9rem; font-size: 1rem; font-weight: 600;">
            🚀 Xác Nhận Đăng Ký Lịch Làm Việc & Sinh Slot Khám
          </button>
        </form>
      </div>
    </div>
  `;
};

export const attachDoctorScheduleListeners = async () => {
  const form = document.getElementById('doctorScheduleForm');
  if (!form) return;

  const user = getUser();
  if (!user || user.role !== 'DOCTOR') return;

  // Set default dates (today to +7 days)
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  const startInput = document.getElementById('startDateInput');
  const endInput = document.getElementById('endDateInput');
  if (startInput && !startInput.value) startInput.value = todayStr;
  if (endInput && !endInput.value) {
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);
    endInput.value = nextWeek.toISOString().split('T')[0];
  }

  form.onsubmit = async (e) => {
    e.preventDefault();

    const startDateVal = document.getElementById('startDateInput').value;
    const endDateVal = document.getElementById('endDateInput').value;
    const startTime = document.getElementById('startTimeInput').value || '';
    const endTime = document.getElementById('endTimeInput').value || '';

    // 1. Kiểm tra số phút phải là 00 hoặc 30
    const startMin = startTime.split(':')[1];
    const endMin = endTime.split(':')[1];

    if (startMin !== '00' && startMin !== '30') {
      alert('Số phút đăng ký không hợp lệ (Số phút phải là :00 hoặc :30, ví dụ 08:00, 08:30)');
      return;
    }
    if (endMin !== '00' && endMin !== '30') {
      alert('Số phút đăng ký không hợp lệ (Số phút phải là :00 hoặc :30, ví dụ 12:00, 17:30)');
      return;
    }

    // Xử lý trường hợp Giờ kết thúc là 12:00 SA (00:00 đêm cuồi ca làm việc)
    let effectiveEndTime = endTime;
    let compareEndTime = endTime;
    if (endTime === '00:00') {
      compareEndTime = '24:00';
      effectiveEndTime = '23:59';
    }

    if (startTime >= compareEndTime) {
      alert(`Giờ bắt đầu (${startTime}) phải nhỏ hơn Giờ kết thúc (${endTime}). (Lưu ý: 12:00 CH là 12:00 Trưa, 12:00 SA là 00:00 Nửa đêm).`);
      return;
    }

    // 2. Kiểm tra thời gian đăng ký phải ở tương lai
    const checkToday = new Date();
    checkToday.setHours(0, 0, 0, 0);

    const startDate = new Date(startDateVal);
    const endDate = new Date(endDateVal);

    if (startDate < checkToday) {
      alert('Ngày bắt đầu làm việc phải từ hôm nay trở đi.');
      return;
    }
    if (endDate < startDate) {
      alert('Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.');
      return;
    }

    const now = new Date();
    const currTodayStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
    if (startDateVal === currTodayStr) {
      const nowTimeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
      if (startTime <= nowTimeStr) {
        alert(`Giờ bắt đầu (${startTime}) đã trôi qua so với giờ hiện tại (${nowTimeStr}). Vui lòng chọn mốc giờ ở tương lai!`);
        return;
      }
    }

    const btn = document.getElementById('submitScheduleBtn');
    const originalText = btn.textContent;
    btn.textContent = '⏳ Đang đăng ký & sinh slot...';
    btn.disabled = true;

    try {
      const myProfile = await ProviderAPI.getMe();
      if (!myProfile) {
        alert('Hồ sơ Bác sĩ chưa được tạo.');
        return;
      }

      for (let day = 0; day <= 6; day++) {
        try {
          await AppointmentAPI.createSchedule(myProfile.id, {
            day_of_week: day,
            start_time: startTime,
            end_time: effectiveEndTime,
            is_active: true
          });
        } catch (sErr) {}
      }

      const res = await AppointmentAPI.generateSlots(myProfile.id, {
        start_date: startDateVal,
        end_date: endDateVal
      });

      // 3. Kiểm tra trùng lặp
      if (res.slots_created === 0) {
        alert('Thời gian đăng ký lịch làm việc bị trùng hoặc đã được đăng ký trước đó!');
        return;
      }

      alert(`Đã đăng ký lịch làm việc thành công! (Tạo ${res.slots_created} slot khám mới)`);
      window.location.hash = '#/appointments';
    } catch (err) {
      alert(getErrorMessage(err, 'Lỗi sinh slot khám.'));
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  };
};
