import { Navbar } from '../components/Navbar.js';
import { AuthAPI, setToken, setUser, getErrorMessage } from '../api.js';

export const AuthPage = () => {
  return `
    <div class="container">
      <div class="glass-panel animate-fade-in" style="max-width: 400px; margin: 4rem auto; padding: 2rem;">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: var(--primary-blue);">Welcome Back</h2>
        <div id="loginError" class="alert alert-error" style="display: none;"></div>
        <form id="loginForm">
          <div class="form-group">
            <label class="form-label">Email / Username</label>
            <input type="text" id="email" class="form-control" required placeholder="Enter your email">
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" id="password" class="form-control" required placeholder="Enter your password">
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Login</button>
        </form>
        <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem;">
          <a href="#/register" style="color: var(--secondary-teal); text-decoration: none;">Create an account</a>
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
        btn.textContent = 'Logging in...';
        btn.disabled = true;

        const res = await AuthAPI.login(email, password);
        
        setToken(res.access_token);
        setUser(res.user);
        window.location.hash = '#/';
      } catch (error) {
        err.textContent = getErrorMessage(error, 'Login failed. Please check your credentials.');
        err.style.display = 'block';
        const btn = form.querySelector('button');
        btn.textContent = 'Login';
        btn.disabled = false;
      }
    });
  }
};
