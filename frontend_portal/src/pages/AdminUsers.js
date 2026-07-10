import { Navbar } from '../components/Navbar.js';
import { AuthAPI, ProviderAPI, getErrorMessage } from '../api.js';

export const AdminUsersPage = () => {
  return `
    ${Navbar()}
    <div class="container" style="padding-top: 2rem;">
      <h1 style="color: var(--primary-blue); margin-bottom: 2rem;">User Management</h1>
      
      <div class="glass-panel" style="max-width: 600px; padding: 2rem;">
        <h3 style="margin-bottom: 1.5rem;">Create Doctor Account</h3>
        <div id="createDoctorError" class="alert alert-error" style="display: none;"></div>
        <div id="createDoctorSuccess" class="alert alert-success" style="display: none;"></div>
        
        <form id="createDoctorForm">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" id="docEmail" class="form-control" required placeholder="doctor@hospital.com">
          </div>
          <div class="form-group">
            <label class="form-label">Temporary Password</label>
            <input type="password" id="docPassword" class="form-control" required placeholder="Enter password">
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">First Name</label>
              <input type="text" id="docFirstName" class="form-control" required placeholder="First name">
            </div>
            <div class="form-group">
              <label class="form-label">Last Name</label>
              <input type="text" id="docLastName" class="form-control" required placeholder="Last name">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Specialty/Bio</label>
            <textarea id="docBio" class="form-control" rows="3" placeholder="Brief biography or specialty details"></textarea>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top: 1rem;">Create Doctor Profile</button>
        </form>
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

        // 1. Create Auth Identity as DOCTOR
        const authData = {
          email,
          username: email,
          password,
          password_confirm: password,
          role: 'DOCTOR' // API Gateway will verify if current user is ADMIN
        };
        const res = await AuthAPI.register(authData);
        const userId = res.user.id;

        // 2. Create Provider Profile
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
};
