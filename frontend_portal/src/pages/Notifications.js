import { Navbar } from '../components/Navbar.js';
import { NotificationAPI, getUser, getErrorMessage } from '../api.js';

export const NotificationsPage = () => {
  const user = getUser();
  const isAdmin = user && user.role === 'ADMIN';

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Notification Center</h1>
        <p class="text-muted">Quản lý mẫu thông báo, phát lệnh gửi tin nhắn/email và theo dõi nhật ký công việc (Jobs).</p>
      </div>

      ${isAdmin ? `
        <!-- CREATE TEMPLATE SECTION -->
        <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Tạo Mẫu Thông báo (Notification Template)</h2>
            <button id="showAddTplBtn" class="btn btn-secondary btn-sm">+ Tạo Template mới</button>
          </div>

          <div id="addTplContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <form id="addTplForm">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group"><label class="form-label">Mã Template (Code)</label><input type="text" id="tplName" class="form-input" required placeholder="e.g. APPOINTMENT_CONFIRMED" /></div>
                <div class="form-group"><label class="form-label">Kênh gửi (Channel)</label><select id="tplType" class="form-input"><option value="EMAIL">EMAIL</option><option value="SMS">SMS</option><option value="PUSH">PUSH</option></select></div>
              </div>
              <div class="form-group"><label class="form-label">Tiêu đề (Subject Template)</label><input type="text" id="tplSubject" class="form-input" required placeholder="Lịch hẹn khám bệnh của bạn" /></div>
              <div class="form-group"><label class="form-label">Nội dung (Body Template)</label><textarea id="tplBody" class="form-input" rows="3" required placeholder="Chào {{patient_name}}, lịch hẹn của bạn đã được xác nhận."></textarea></div>
              <button type="submit" class="btn btn-primary btn-sm">Lưu Template</button>
              <button type="button" id="cancelTplBtn" class="btn btn-secondary btn-sm">Hủy</button>
            </form>
          </div>
        </div>

        <!-- SEND NOTIFICATION FORM SECTION -->
        <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">🚀 Phát Lệnh Gửi Thông báo cho Bệnh nhân</h2>
            <button id="showSendNotifBtn" class="btn btn-primary btn-sm">✉️ Gửi Thông báo ngay</button>
          </div>

          <div id="sendNotifContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px;">
            <form id="sendNotifForm">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                  <label class="form-label">Email người nhận (Recipient Email)</label>
                  <input type="email" id="sendRecipientAddr" class="form-input" required placeholder="patient@gmail.com" />
                </div>
                <div class="form-group">
                  <label class="form-label">Kênh gửi (Channel)</label>
                  <select id="sendChannel" class="form-input">
                    <option value="EMAIL">EMAIL</option>
                    <option value="SMS">SMS</option>
                    <option value="PUSH">PUSH</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Tiêu đề thông báo (Subject)</label>
                <input type="text" id="sendSubject" class="form-input" placeholder="Thông báo từ hệ thống Y tế Healthcare" />
              </div>

              <div class="form-group">
                <label class="form-label">Nội dung thông báo (Content)</label>
                <textarea id="sendContent" class="form-input" rows="3" required placeholder="Nhập nội dung tin nhắn/email muốn gửi cho bệnh nhân..."></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">Mẫu thông báo sử dụng (Template Code - Tùy chọn)</label>
                <input type="text" id="sendTplCode" class="form-input" placeholder="Ví dụ: GENERAL_EMAIL hoặc APPOINTMENT_CONFIRMED" />
              </div>

              <button type="submit" class="btn btn-primary btn-sm">Phát Lệnh Gửi Thông báo</button>
              <button type="button" id="cancelSendNotifBtn" class="btn btn-secondary btn-sm">Hủy</button>
            </form>
          </div>
        </div>
      ` : ''}

      <!-- TEMPLATES LIST -->
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">Danh sách Mẫu Thông báo</h2>
        <div id="notificationList" class="dashboard-grid" style="grid-template-columns: 1fr;">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
            Loading templates...
          </div>
        </div>
      </div>

      <!-- NOTIFICATION JOBS SECTION -->
      <div class="glass-panel" style="padding: 2rem;">
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">Nhật ký Công việc Gửi Thông báo (Jobs Log)</h2>
        <div id="notificationJobsList">Đang tải jobs...</div>
      </div>
    </div>
  `;
};

export const attachNotificationsListeners = async () => {
  const container = document.getElementById('notificationList');
  if (!container) return;

  const user = getUser();
  const isAdmin = user && user.role === 'ADMIN';

  // Admin Template Form
  if (isAdmin) {
    const showBtn = document.getElementById('showAddTplBtn');
    const cancelBtn = document.getElementById('cancelTplBtn');
    const tplContainer = document.getElementById('addTplContainer');
    const tplForm = document.getElementById('addTplForm');

    if (showBtn) showBtn.onclick = () => tplContainer.style.display = 'block';
    if (cancelBtn) cancelBtn.onclick = () => tplContainer.style.display = 'none';

    if (tplForm) {
      tplForm.onsubmit = async (e) => {
        e.preventDefault();
        try {
          const rawName = document.getElementById('tplName').value;
          const codeVal = rawName.trim().toUpperCase().replace(/[^A-Z0-9]/g, '_');
          await NotificationAPI.createTemplate({
            code: codeVal,
            channel: document.getElementById('tplType').value,
            subject_template: document.getElementById('tplSubject').value,
            body_template: document.getElementById('tplBody').value
          });
          alert('Đã tạo template thông báo thành công!');
          tplContainer.style.display = 'none';
          loadTemplates();
        } catch (err) { alert(getErrorMessage(err, 'Lỗi tạo template')); }
      };
    }

    // Admin Send Notification Form
    const showSendBtn = document.getElementById('showSendNotifBtn');
    const cancelSendBtn = document.getElementById('cancelSendNotifBtn');
    const sendContainer = document.getElementById('sendNotifContainer');
    const sendForm = document.getElementById('sendNotifForm');

    if (showSendBtn) showSendBtn.onclick = () => {
      sendContainer.style.display = 'block';
      if (user && user.email) {
        document.getElementById('sendRecipientAddr').value = user.email;
      }
    };
    if (cancelSendBtn) cancelSendBtn.onclick = () => sendContainer.style.display = 'none';

    if (sendForm) {
      sendForm.onsubmit = async (e) => {
        e.preventDefault();
        try {
          const recipientEmail = document.getElementById('sendRecipientAddr').value;
          const subject = document.getElementById('sendSubject').value || 'Thông báo từ hệ thống Y tế';
          const content = document.getElementById('sendContent').value;
          const channel = document.getElementById('sendChannel').value;
          const tplCode = document.getElementById('sendTplCode').value || 'GENERAL_EMAIL';

          await NotificationAPI.sendNotification({
            recipient_address: recipientEmail,
            subject: subject,
            content: content,
            channel: channel,
            template_code: tplCode,
            variables: {
              subject: subject,
              content: content,
              message: content,
              patient_name: recipientEmail.split('@')[0]
            }
          });
          alert('Đã phát lệnh gửi thông báo tới ' + recipientEmail + ' thành công!');
          sendContainer.style.display = 'none';
          sendForm.reset();
          loadJobs();
        } catch (err) { alert(getErrorMessage(err, 'Lỗi gửi thông báo')); }
      };
    }
  }

  // Load Templates
  const loadTemplates = async () => {
    try {
      const data = await NotificationAPI.getTemplates();
      const templates = data.results || data || [];
      
      if (templates.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">Chưa có mẫu thông báo nào. Bấm nút "+ Tạo Template mới" ở trên để khởi tạo.</div>`;
        return;
      }

      container.innerHTML = templates.map(n => `
        <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1rem 1.5rem;">
          <div style="display: flex; justify-content: space-between; width: 100%;">
            <h3 style="color: var(--primary-blue); font-size: 1rem; margin-bottom: 0.2rem;">Mã Code: ${n.code || n.name || 'N/A'}</h3>
            <span class="badge badge-info">${n.channel || n.type || 'EMAIL'}</span>
          </div>
          <p style="margin-bottom: 0.3rem; font-size: 0.9rem; font-weight: 500;">Subject: ${n.subject_template || n.subject || ''}</p>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.8rem;">Body: ${n.body_template || n.body || ''}</p>
          ${isAdmin ? `<button class="btn btn-secondary btn-sm quick-send-btn" data-code="${n.code}" data-channel="${n.channel}">📤 Gửi thử bằng mẫu này</button>` : ''}
        </div>
      `).join('');

      document.querySelectorAll('.quick-send-btn').forEach(btn => {
        btn.onclick = (e) => {
          const sendContainer = document.getElementById('sendNotifContainer');
          if (sendContainer) {
            sendContainer.style.display = 'block';
            document.getElementById('sendTplCode').value = e.target.dataset.code;
            document.getElementById('sendChannel').value = e.target.dataset.channel;
            if (user) {
              document.getElementById('sendRecipientId').value = user.id;
              document.getElementById('sendRecipientAddr').value = user.email || 'patient@example.com';
            }
            sendContainer.scrollIntoView({ behavior: 'smooth' });
          }
        };
      });

    } catch (e) {
      const msg = getErrorMessage(e, 'Failed to load templates.');
      container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">${msg}</div>`;
    }
  };

  // Load Jobs
  const jobsContainer = document.getElementById('notificationJobsList');
  const loadJobs = async () => {
    try {
      const data = await NotificationAPI.getJobs();
      const jobs = data.results || data || [];

      if (jobs.length === 0) {
        jobsContainer.innerHTML = '<p class="text-muted">Chưa có công việc gửi thông báo nào.</p>';
        return;
      }

      jobsContainer.innerHTML = jobs.map(j => `
        <div style="background: rgba(255,255,255,0.03); padding: 0.8rem 1.2rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong>Gửi tới:</strong> ${j.recipient_address || j.recipient_email || 'User'} | 
            Kênh: <strong>${j.channel || 'EMAIL'}</strong> | 
            Trạng thái: <span class="badge ${j.status === 'SENT' ? 'badge-success' : 'badge-warning'}">${j.status}</span>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem;" class="text-muted">Thời gian: ${j.sent_at || j.created_at ? new Date(j.sent_at || j.created_at).toLocaleString() : 'N/A'}</p>
          </div>
          ${j.status === 'FAILED' ? `<button class="btn btn-secondary btn-sm retry-job-btn" data-id="${j.id}">Thử lại</button>` : ''}
        </div>
      `).join('');

      document.querySelectorAll('.retry-job-btn').forEach(btn => {
        btn.onclick = async (e) => {
          try {
            await NotificationAPI.retryJob(e.target.dataset.id);
            alert('Đã phát lệnh gửi lại!');
            loadJobs();
          } catch (err) { alert(getErrorMessage(err, 'Thất bại khi gửi lại.')); }
        };
      });

    } catch (e) {
      jobsContainer.innerHTML = '<p class="text-muted">Chưa có lịch sử công việc gửi thông báo.</p>';
    }
  };

  loadTemplates();
  loadJobs();
};
