import { Navbar } from '../components/Navbar.js';
import { AuthAPI, PatientAPI, setToken, setUser, getErrorMessage } from '../api.js';

export const RegisterPage = () => {
  return `
    <div class="container">
      <div class="glass-panel animate-fade-in" style="max-width: 520px; margin: 3rem auto; padding: 2.5rem;">
        <h2 style="text-align: center; margin-bottom: 0.5rem; color: var(--primary-blue); font-size: 1.8rem;">Đăng ký Tài khoản Bệnh nhân</h2>
        <p class="text-muted" style="text-align: center; margin-bottom: 1.5rem; font-size: 0.9rem;">Tạo tài khoản để sử dụng dịch vụ chăm sóc sức khỏe trực tuyến</p>
        <div id="registerError" class="alert alert-error" style="display: none;"></div>
        <form id="registerForm">
          <div class="form-group">
            <label class="form-label">Email tài khoản</label>
            <input type="email" id="regEmail" class="form-control" required placeholder="Nhập địa chỉ email">
          </div>
          <div class="form-group">
            <label class="form-label">Mật khẩu</label>
            <input type="password" id="regPassword" class="form-control" required placeholder="Tạo mật khẩu an toàn">
          </div>
          <div class="form-group">
            <label class="form-label">Xác nhận mật khẩu</label>
            <input type="password" id="regConfirmPassword" class="form-control" required placeholder="Nhập lại mật khẩu">
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Tên</label>
              <input type="text" id="regFirstName" class="form-control" required placeholder="Tên bệnh nhân">
            </div>
            <div class="form-group">
              <label class="form-label">Họ & Tên lót</label>
              <input type="text" id="regLastName" class="form-control" required placeholder="Họ và tên lót">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Số điện thoại</label>
            <input type="text" id="regPhone" class="form-control" placeholder="Nhập số điện thoại liên hệ">
          </div>
          <div class="form-group">
            <label class="form-label">Địa chỉ cư trú</label>
            <input type="text" id="regAddress" class="form-control" placeholder="Số nhà, đường, quận/huyện, tỉnh/thành">
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1.2rem; font-weight: 600;">Đăng ký tài khoản</button>
        </form>
        <div style="text-align: center; margin-top: 1.2rem; font-size: 0.9rem;">
          <a href="#/login" style="color: var(--secondary-teal); text-decoration: none; font-weight: 500;">Đã có tài khoản? Đăng nhập ngay</a>
        </div>
      </div>
    </div>
  `;
};

export const attachRegisterListeners = () => {
  const form = document.getElementById('registerForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('regEmail').value;
      const password = document.getElementById('regPassword').value;
      const confirmPassword = document.getElementById('regConfirmPassword').value;
      const firstName = document.getElementById('regFirstName').value;
      const lastName = document.getElementById('regLastName').value;
      const phone = document.getElementById('regPhone').value;
      const address = document.getElementById('regAddress').value;
      
      const err = document.getElementById('registerError');
      err.style.display = 'none';

      if (password !== confirmPassword) {
        err.textContent = 'Mật khẩu và xác nhận mật khẩu không khớp nhau.';
        err.style.display = 'block';
        return;
      }

      try {
        const btn = form.querySelector('button');
        btn.textContent = 'Đang đăng ký...';
        btn.disabled = true;

        const authData = {
          email,
          username: email,
          password,
          password_confirm: confirmPassword,
          first_name: firstName,
          last_name: lastName,
          phone,
          role: 'PATIENT'
        };
        const res = await AuthAPI.register(authData);
        const userId = res.user.id;

        setToken(res.access_token);
        setUser(res.user);

        const patientData = {
          user_id: userId,
          first_name: firstName,
          last_name: lastName,
          phone,
          address
        };
        await PatientAPI.createProfile(patientData);

        window.location.hash = '#/';
      } catch (error) {
        let msg = getErrorMessage(error, 'Đăng ký không thành công.');
        if (error && error.data) {
          if (error.data.email) msg = 'Email này đã tồn tại trên hệ thống.';
          else if (error.data.phone) msg = 'Số điện thoại này đã được sử dụng.';
        }
        err.textContent = msg;
        err.style.display = 'block';
        const btn = form.querySelector('button');
        btn.textContent = 'Đăng ký tài khoản';
        btn.disabled = false;
        
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    });
  }
};
