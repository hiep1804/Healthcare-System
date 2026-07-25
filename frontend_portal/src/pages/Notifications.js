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
        <p class="text-muted">Manage notification templates, view delivery jobs, and monitor outbound communication.</p>
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
                <div class="form-group"><label class="form-label">Tên Template</label><input type="text" id="tplName" class="form-input" required placeholder="Xác nhận lịch hẹn" /></div>
                <div class="form-group"><label class="form-label">Loại (Type)</label><select id="tplType" class="form-input"><option value="EMAIL">Email</option><option value="SMS">SMS</option></select></div>
              </div>
              <div class="form-group"><label class="form-label">Tiêu đề (Subject Template)</label><input type="text" id="tplSubject" class="form-input" required placeholder="Lịch hẹn khám bệnh của bạn" /></div>
              <div class="form-group"><label class="form-label">Nội dung (Body Template)</label><textarea id="tplBody" class="form-input" rows="3" required placeholder="Chào {{patient_name}}, lịch hẹn của bạn với BS {{doctor_name}} đã được xác nhận."></textarea></div>
              <button type="submit" class="btn btn-primary btn-sm">Lưu Template</button>
              <button type="button" id="cancelTplBtn" class="btn btn-secondary btn-sm">Hủy</button>
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
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">Nhật ký Công việc Gửi Thông báo (Jobs)</h2>
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
          await NotificationAPI.createTemplate({
            name: document.getElementById('tplName').value,
            type: document.getElementById('tplType').value,
            subject_template: document.getElementById('tplSubject').value,
            body_template: document.getElementById('tplBody').value
          });
          alert('Đã tạo template thông báo!');
          tplContainer.style.display = 'none';
          loadTemplates();
        } catch (err) { alert(getErrorMessage(err, 'Lỗi tạo template')); }
      };
    }
  }

  // Load Templates
  const loadTemplates = async () => {
    try {
      const data = await NotificationAPI.getTemplates();
      const templates = data.results || data || [];
      
      if (templates.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No notification templates found.</div>`;
        return;
      }

      container.innerHTML = templates.map(n => `
        <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1rem 1.5rem;">
          <div style="display: flex; justify-content: space-between; width: 100%;">
            <h3 style="color: var(--primary-blue); font-size: 1rem; margin-bottom: 0.2rem;">${n.name}</h3>
            <span class="badge badge-info">${n.type || 'EMAIL'}</span>
          </div>
          <p style="margin-bottom: 0.5rem; font-size: 0.9rem; font-weight: 500;">Subject: ${n.subject_template || n.subject || ''}</p>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0;">Body: ${n.body_template || n.body || ''}</p>
        </div>
      `).join('');
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
        <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 6px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong>Gửi đến:</strong> ${j.recipient_email || j.recipient_phone || 'User'} | 
            Status: <span class="badge ${j.status === 'SENT' ? 'badge-success' : 'badge-warning'}">${j.status}</span>
          </div>
          ${j.status === 'FAILED' ? `<button class="btn btn-secondary btn-sm retry-job-btn" data-id="${j.id}">Gửi lại</button>` : ''}
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
