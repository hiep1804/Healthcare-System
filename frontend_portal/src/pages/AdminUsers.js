import { Navbar } from '../components/Navbar.js';
import { AuthAPI, ProviderAPI, getErrorMessage } from '../api.js';

export const AdminUsersPage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-top: 2rem; padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="color: var(--primary-blue); margin-bottom: 0.5rem;">Quản lý Người dùng & Tài khoản Hệ thống</h1>
        <p class="text-muted">Quản lý danh sách người dùng, mở/khóa tài khoản, phân quyền và khởi tạo tài khoản Bác sĩ.</p>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        <!-- CREATE DOCTOR FORM -->
        <div class="glass-panel" style="padding: 2rem;">
          <h3 style="margin-bottom: 1.5rem; color: var(--primary-blue);">Tạo Tài khoản Bác sĩ Mới (Admin)</h3>
          <div id="createDoctorError" class="alert alert-error" style="display: none;"></div>
          <div id="createDoctorSuccess" class="alert alert-success" style="display: none;"></div>
          
          <form id="createDoctorForm">
            <div class="form-group">
              <label class="form-label">Email tài khoản</label>
              <input type="email" id="docEmail" class="form-control" required placeholder="doctor@hospital.com">
            </div>
            <div class="form-group">
              <label class="form-label">Mật khẩu khởi tạo</label>
              <input type="password" id="docPassword" class="form-control" required placeholder="Nhập mật khẩu">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">Tên</label>
                <input type="text" id="docFirstName" class="form-control" required placeholder="Tên">
              </div>
              <div class="form-group">
                <label class="form-label">Họ</label>
                <input type="text" id="docLastName" class="form-control" required placeholder="Họ">
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Giới thiệu / Chuyên môn</label>
              <textarea id="docBio" class="form-control" rows="3" placeholder="Mô tả kinh nghiệm, chuyên môn"></textarea>
            </div>
            <button type="submit" class="btn btn-primary" style="margin-top: 1rem; width: 100%;">Tạo Hồ sơ Bác sĩ</button>
          </form>
        </div>

        <!-- USERS LIST -->
        <div class="glass-panel" style="padding: 2rem;">
          <h3 style="margin-bottom: 1.5rem; color: var(--primary-blue);">Danh sách Người dùng Hệ thống</h3>
          <div id="usersList" style="max-height: 500px; overflow-y: auto;">
            Loading users...
          </div>
        </div>
      </div>
    </div>
  `;
};

export const attachAdminUsersListeners = () => {
  const form = document.getElementById('createDoctorForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('docEmail').value;
      const password = document.getElementById('docPassword').value;
      const firstName = document.getElementById('docFirstName').value;
      const lastName = document.getElementById('docLastName').value;
      const bio = document.getElementById('docBio').value;
      
      const err = document.getElementById('createDoctorError');
      const succ = document.getElementById('createDoctorSuccess');
      err.style.display = 'none';
      succ.style.display = 'none';

      try {
        const btn = form.querySelector('button');
        btn.textContent = 'Creating...';
        btn.disabled = true;

        const authData = {
          email,
          username: email,
          password,
          password_confirm: password,
          role: 'DOCTOR'
        };
        const res = await AuthAPI.register(authData);
        const userId = res.user.id;

        const providerData = {
          user_id: userId,
          first_name: firstName,
          last_name: lastName,
          bio
        };
        await ProviderAPI.createProfile(providerData);

        succ.textContent = 'Doctor account created successfully!';
        succ.style.display = 'block';
        form.reset();
        loadUsers();
        
      } catch (error) {
        err.textContent = getErrorMessage(error, 'Failed to create doctor account.');
        err.style.display = 'block';
      } finally {
        const btn = form.querySelector('button');
        btn.textContent = 'Create Doctor Profile';
        btn.disabled = false;
      }
    });
  }

  // Load Users List
  const usersContainer = document.getElementById('usersList');
  const loadUsers = async () => {
    try {
      const data = await AuthAPI.getUsers();
      const users = data.results || data || [];

      if (users.length === 0) {
        usersContainer.innerHTML = '<p class="text-muted">No users found.</p>';
        return;
      }

      usersContainer.innerHTML = users.map(u => `
        <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 6px; margin-bottom: 0.8rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <strong>${u.email || u.username}</strong>
            <span class="badge ${u.status === 'ACTIVE' ? 'badge-success' : 'badge-warning'}">${u.status}</span>
          </div>
          <p style="margin: 0; font-size: 0.85rem;" class="text-muted">Role: ${u.roles ? u.roles.join(', ') : u.role || 'User'}</p>

          <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
            <button class="btn btn-secondary btn-sm toggle-status-btn" data-id="${u.id}" data-status="${u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'}">
              ${u.status === 'ACTIVE' ? 'Suspend' : 'Activate'}
            </button>
          </div>
        </div>
      `).join('');

      document.querySelectorAll('.toggle-status-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const uid = e.target.dataset.id;
          const newStatus = e.target.dataset.status;
          try {
            await AuthAPI.updateUserStatus(uid, newStatus);
            loadUsers();
          } catch (err) { alert(getErrorMessage(err, 'Lỗi cập nhật trạng thái user.')); }
        };
      });

    } catch (e) {
      usersContainer.innerHTML = `<p class="text-muted">Lỗi tải danh sách user: ${getErrorMessage(e)}</p>`;
    }
  };

  loadUsers();
};
