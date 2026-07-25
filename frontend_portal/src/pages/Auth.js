import { Navbar } from '../components/Navbar.js';
import { AuthAPI, setToken, setUser, getErrorMessage } from '../api.js';

export const AuthPage = () => {
  return `
    <div class="container">
      <div class="glass-panel animate-fade-in" style="max-width: 420px; margin: 4rem auto; padding: 2.5rem;">
        <h2 style="text-align: center; margin-bottom: 0.5rem; color: var(--primary-blue); font-size: 1.8rem;">Đăng nhập Hệ thống</h2>
        <p class="text-muted" style="text-align: center; margin-bottom: 1.5rem; font-size: 0.9rem;">Hệ thống Quản lý Y tế & Chăm sóc Sức khỏe</p>
        <div id="loginError" class="alert alert-error" style="display: none;"></div>
        <form id="loginForm">
          <div class="form-group">
            <label class="form-label">Tên đăng nhập / Email</label>
            <input type="text" id="email" class="form-control" required placeholder="Nhập email hoặc tên đăng nhập">
          </div>
          <div class="form-group">
            <label class="form-label">Mật khẩu</label>
            <input type="password" id="password" class="form-control" required placeholder="Nhập mật khẩu">
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1.2rem; font-weight: 600;">Đăng nhập</button>
        </form>
        <div style="text-align: center; margin-top: 1.2rem; font-size: 0.9rem;">
          <a href="#/register" style="color: var(--secondary-teal); text-decoration: none; font-weight: 500;">Chưa có tài khoản? Đăng ký ngay</a>
        </div>
      </div>
    </div>
  `;
};

export const attachAuthListeners = () => {
  const form = document.getElementById('loginForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const err = document.getElementById('loginError');
      err.style.display = 'none';

      try {
        const btn = form.querySelector('button');
        btn.textContent = 'Đang đăng nhập...';
        btn.disabled = true;

        const res = await AuthAPI.login(email, password);
        
        setToken(res.access_token);
        setUser(res.user);
        window.location.hash = '#/';
      } catch (error) {
        err.textContent = 'Email hoặc mật khẩu không chính xác. Vui lòng thử lại!';
        err.style.display = 'block';
        const btn = form.querySelector('button');
        btn.textContent = 'Đăng nhập';
        btn.disabled = false;
      }
    });
  }
};
