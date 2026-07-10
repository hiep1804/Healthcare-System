import { Navbar } from '../components/Navbar.js';
import { AuthAPI, PatientAPI, ProviderAPI, getUser, getErrorMessage } from '../api.js';

export const ProfilePage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">My Profile</h1>
        <p class="text-muted">Manage your personal information.</p>
      </div>

      <div class="glass-panel" style="padding: 2rem;">
        <div id="profileError" style="margin-bottom: 1rem;"></div>
        <form id="profileForm" style="display: none;">
          <div id="dynamicFields"></div>
          
          <button type="submit" class="btn btn-primary" style="margin-top: 1rem;">
            Save Changes
          </button>
        </form>
        <div id="loadingIndicator" style="text-align: center; color: var(--text-muted);">
          Loading profile data...
        </div>
      </div>
    </div>
  `;
};

export const attachProfileListeners = async () => {
  const user = getUser();
  if (!user) return;

  const form = document.getElementById('profileForm');
  const fieldsContainer = document.getElementById('dynamicFields');
  const errorDiv = document.getElementById('profileError');
  const loading = document.getElementById('loadingIndicator');

  if (!form || !fieldsContainer) return;

  const showError = (msg) => {
    errorDiv.innerHTML = `<div class="alert alert-error">${msg}</div>`;
  };
  const showSuccess = (msg) => {
    errorDiv.innerHTML = `<div class="alert alert-success">${msg}</div>`;
  };

  try {
    let profileData = null;
    let authData = await AuthAPI.getMe(); // Get base auth data

    // Render fields based on role
    let fieldsHTML = '';

    if (user.role === 'ADMIN') {
      fieldsHTML = `
        <div class="form-group">
          <label class="form-label">Email</label>
          <input type="text" class="form-input" value="${authData.email || ''}" disabled />
        </div>
        <div class="form-group">
          <label class="form-label">Username</label>
          <input type="text" class="form-input" value="${authData.username || ''}" disabled />
        </div>
        <div class="form-group">
          <label class="form-label">Phone Number</label>
          <input type="text" class="form-input" id="phoneInput" value="${authData.phone || ''}" />
        </div>
      `;
    } else if (user.role === 'PATIENT') {
      profileData = await PatientAPI.getMe();
      if (!profileData) {
        showError('Patient profile not found. Please create one first.');
        loading.style.display = 'none';
        return;
      }
      fieldsHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">First Name</label>
            <input type="text" class="form-input" id="firstNameInput" value="${profileData.first_name || ''}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Last Name</label>
            <input type="text" class="form-input" id="lastNameInput" value="${profileData.last_name || ''}" required />
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Date of Birth</label>
            <input type="date" class="form-input" id="dobInput" value="${profileData.date_of_birth || ''}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Gender</label>
            <select class="form-input" id="genderInput">
              <option value="M" ${profileData.gender === 'M' ? 'selected' : ''}>Male</option>
              <option value="F" ${profileData.gender === 'F' ? 'selected' : ''}>Female</option>
              <option value="O" ${profileData.gender === 'O' ? 'selected' : ''}>Other</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Contact Number</label>
          <input type="text" class="form-input" id="contactInput" value="${profileData.contact_number || ''}" required />
        </div>
        <div class="form-group">
          <label class="form-label">Address</label>
          <input type="text" class="form-input" id="addressInput" value="${profileData.address || ''}" required />
        </div>
        <div class="form-group">
          <label class="form-label">Emergency Contact</label>
          <input type="text" class="form-input" id="emergencyInput" value="${profileData.emergency_contact || ''}" required />
        </div>
      `;
    } else if (user.role === 'DOCTOR') {
      profileData = await ProviderAPI.getMe();
      if (!profileData) {
        showError('Doctor profile not found.');
        loading.style.display = 'none';
        return;
      }
      fieldsHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label">First Name</label>
            <input type="text" class="form-input" id="firstNameInput" value="${profileData.first_name || ''}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Last Name</label>
            <input type="text" class="form-input" id="lastNameInput" value="${profileData.last_name || ''}" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Bio</label>
          <textarea class="form-input" id="bioInput" rows="3">${profileData.bio || ''}</textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Location</label>
          <input type="text" class="form-input" id="locationInput" value="${profileData.location || ''}" />
        </div>
        <div class="form-group">
          <label class="form-label">Clinic</label>
          <input type="text" class="form-input" id="clinicInput" value="${profileData.clinic || ''}" />
        </div>
      `;
    }

    fieldsContainer.innerHTML = fieldsHTML;
    loading.style.display = 'none';
    form.style.display = 'block';

    // Handle form submit
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorDiv.innerHTML = '';
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = 'Saving...';
      btn.disabled = true;

      try {
        if (user.role === 'ADMIN') {
          await AuthAPI.updateMe({
            phone: document.getElementById('phoneInput').value
          });
        } else if (user.role === 'PATIENT') {
          await PatientAPI.updateMe({
            first_name: document.getElementById('firstNameInput').value,
            last_name: document.getElementById('lastNameInput').value,
            date_of_birth: document.getElementById('dobInput').value,
            gender: document.getElementById('genderInput').value,
            contact_number: document.getElementById('contactInput').value,
            address: document.getElementById('addressInput').value,
            emergency_contact: document.getElementById('emergencyInput').value
          });
        } else if (user.role === 'DOCTOR') {
          await ProviderAPI.updateMe({
            first_name: document.getElementById('firstNameInput').value,
            last_name: document.getElementById('lastNameInput').value,
            bio: document.getElementById('bioInput').value,
            location: document.getElementById('locationInput').value,
            clinic: document.getElementById('clinicInput').value
          });
        }
        showSuccess('Profile updated successfully.');
      } catch (err) {
        showError(getErrorMessage(err, 'Failed to update profile.'));
      } finally {
        btn.textContent = originalText;
        btn.disabled = false;
      }
    });

  } catch (err) {
    showError(getErrorMessage(err, 'Failed to load profile data.'));
    loading.style.display = 'none';
  }
};
