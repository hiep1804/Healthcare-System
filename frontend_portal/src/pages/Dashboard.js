import { Navbar } from '../components/Navbar.js';
import { getUser, PatientAPI, getErrorMessage } from '../api.js';

export const DashboardPage = () => {
  const user = getUser();
  if (!user) return '';

  const isPatient = user.role === 'PATIENT';
  const isProvider = user.role === 'PROVIDER';

  return `
    ${Navbar()}
    <div class="container animate-fade-in">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Dashboard</h1>
        <p class="text-muted">Welcome back, ${user.email}. Here is your healthcare overview.</p>
      </div>

      <div class="dashboard-grid">
        ${isPatient ? `
          <div class="stat-card glass-panel" id="patientProfileWidget">
            <h3>Patient Profile</h3>
            <div class="value" style="font-size: 1.2rem; font-weight: normal; margin-top: 10px;" id="profileStatus">Loading...</div>
            <button class="btn btn-primary" id="setupProfileBtn" style="margin-top: 1rem; width: fit-content; display: none;">Setup Profile</button>
          </div>
          <div class="stat-card glass-panel">
            <h3>Upcoming Appointments</h3>
            <div class="value">0</div>
            <a href="#/appointments" class="btn btn-primary" style="margin-top: 1rem; width: fit-content; text-decoration: none;">View Schedule</a>
          </div>
          <div class="stat-card glass-panel">
            <h3>Medical Records</h3>
            <div class="value">0</div>
            <a href="#/medical-records" style="margin-top: 1rem; color: var(--secondary-teal); text-decoration: none; font-weight: 500;">View History &rarr;</a>
          </div>
        ` : ''}

        ${isProvider ? `
          <div class="stat-card glass-panel">
            <h3>Today's Schedule</h3>
            <div class="value">0</div>
            <a href="#/appointments" class="btn btn-primary" style="margin-top: 1rem; width: fit-content; text-decoration: none;">View Appointments</a>
          </div>
          <div class="stat-card glass-panel">
            <h3>Pending Consultations</h3>
            <div class="value">0</div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
};

export const attachDashboardListeners = async () => {
  const user = getUser();
  if (!user || user.role !== 'PATIENT') return;

  const profileStatus = document.getElementById('profileStatus');
  const setupProfileBtn = document.getElementById('setupProfileBtn');

  if (profileStatus) {
    try {
      const profile = await PatientAPI.getProfile(user.id);
      if (profile) {
        profileStatus.innerHTML = `Name: <b>${profile.first_name} ${profile.last_name}</b><br>DOB: ${profile.date_of_birth || 'N/A'}`;
      } else {
        profileStatus.textContent = "Profile not set up yet.";
        setupProfileBtn.style.display = "inline-block";
      }
    } catch (e) {
      profileStatus.textContent = "Error fetching profile or Patient Service (8002) is down.";
    }
  }

  if (setupProfileBtn) {
    setupProfileBtn.addEventListener('click', async () => {
      try {
        setupProfileBtn.textContent = 'Saving...';
        await PatientAPI.createProfile({
          user_id: user.id,
          first_name: "John",
          last_name: "Doe",
          date_of_birth: "1990-01-01",
          gender: "MALE",
          phone_number: "+123456789"
        });
        alert('Profile created! Refreshing...');
        window.location.reload();
      } catch (e) {
        alert('Failed to create profile. Is Patient Service (8002) running?');
        setupProfileBtn.textContent = 'Setup Profile';
      }
    });
  }
};
