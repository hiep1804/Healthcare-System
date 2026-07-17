import { Navbar } from '../components/Navbar.js';
import { AuthAPI, PatientAPI, setToken, setUser, getErrorMessage } from '../api.js';

export const RegisterPage = () => {
  return `
    <div class="container">
      <div class="glass-panel animate-fade-in" style="max-width: 500px; margin: 4rem auto; padding: 2rem;">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: var(--primary-blue);">Create an Account</h2>
        <div id="registerError" class="alert alert-error" style="display: none;"></div>
        <form id="registerForm">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" id="regEmail" class="form-control" required placeholder="Enter your email">
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" id="regPassword" class="form-control" required placeholder="Create a password">
          </div>
          <div class="form-group">
            <label class="form-label">Confirm Password</label>
            <input type="password" id="regConfirmPassword" class="form-control" required placeholder="Confirm your password">
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">First Name</label>
              <input type="text" id="regFirstName" class="form-control" required placeholder="First name">
            </div>
            <div class="form-group">
              <label class="form-label">Last Name</label>
              <input type="text" id="regLastName" class="form-control" required placeholder="Last name">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Phone</label>
            <input type="text" id="regPhone" class="form-control" placeholder="Phone number (optional)">
          </div>
          <div class="form-group">
            <label class="form-label">Address</label>
            <input type="text" id="regAddress" class="form-control" placeholder="Full address">
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;">Register</button>
        </form>
        <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem;">
          <a href="#/login" style="color: var(--secondary-teal); text-decoration: none;">Already have an account? Login</a>
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
        err.textContent = 'Passwords do not match.';
        err.style.display = 'block';
        return;
      }

      try {
        const btn = form.querySelector('button');
        btn.textContent = 'Registering...';
        btn.disabled = true;

        // 1. Register Auth Identity
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

        // 2. We got tokens back! Let's temporarily log them in so PatientAPI works
        setToken(res.access_token);
        setUser(res.user);

        // 3. Create Patient Profile
        const patientData = {
          user_id: userId,
          first_name: firstName,
          last_name: lastName,
          phone,
          address
        };
        await PatientAPI.createProfile(patientData);

        // 4. Redirect to Dashboard
        window.location.hash = '#/';
      } catch (error) {
        err.textContent = getErrorMessage(error, 'Registration failed.');
        err.style.display = 'block';
        const btn = form.querySelector('button');
        btn.textContent = 'Register';
        btn.disabled = false;
        
        // Clear broken token
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    });
  }
};
