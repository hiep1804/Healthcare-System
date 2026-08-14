import { Navbar } from '../components/Navbar.js';
import { InsuranceAPI, getUser, getErrorMessage } from '../api.js';

export const InsurancePage = () => {
  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Quản lý Bảo hiểm Y tế & Bồi thường</h1>
        <p class="text-muted">Quản lý thẻ bảo hiểm y tế, kiểm tra hạn mức thanh toán và nộp yêu cầu bồi thường bảo hiểm.</p>
      </div>

      <!-- ADD POLICY SECTION -->
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Thẻ Bảo hiểm Y tế của tôi</h2>
          <button id="showAddPolicyBtn" class="btn btn-secondary btn-sm">+ Thêm Thẻ BHYT / Bảo hiểm</button>
        </div>

        <div id="addPolicyContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
          <form id="addPolicyForm">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">Đơn vị cung cấp (Provider Name)</label>
                <input type="text" id="policyProvider" class="form-input" required placeholder="Bảo Việt, Prudential, BHYT..." />
              </div>
              <div class="form-group">
                <label class="form-label">Số thẻ / Số Hợp đồng (Policy Number)</label>
                <input type="text" id="policyNumber" class="form-input" required placeholder="HC-123456789" />
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">Có hiệu lực từ</label>
                <input type="date" id="policyValidFrom" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Có hiệu lực đến</label>
                <input type="date" id="policyValidUntil" class="form-input" required />
              </div>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Lưu Thẻ Bảo hiểm</button>
            <button type="button" id="cancelPolicyBtn" class="btn btn-secondary btn-sm">Hủy</button>
          </form>
        </div>

        <div id="insuranceList" class="dashboard-grid">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
            Đang tải thông tin thẻ bảo hiểm...
          </div>
        </div>
      </div>

      <!-- CLAIMS SECTION -->
      <div class="glass-panel" style="padding: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Yêu cầu Bồi thường (Insurance Claims)</h2>
          <button id="showAddClaimBtn" class="btn btn-secondary btn-sm">+ Nộp Yêu cầu Bồi thường</button>
        </div>

        <div id="addClaimContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
          <form id="addClaimForm">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label class="form-label">ID Thẻ Bảo hiểm (Policy UUID)</label>
                <input type="text" id="claimPolicyId" class="form-input" required placeholder="UUID thẻ bảo hiểm" />
              </div>
              <div class="form-group">
                <label class="form-label">Số tiền yêu cầu (VND)</label>
                <input type="number" id="claimAmount" class="form-input" required placeholder="500000" />
              </div>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Gửi Yêu cầu Bồi thường</button>
            <button type="button" id="cancelClaimBtn" class="btn btn-secondary btn-sm">Hủy</button>
          </form>
        </div>

        <div id="claimsList" class="dashboard-grid">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
            Loading claims...
          </div>
        </div>
      </div>
    </div>
  `;
};

export const attachInsuranceListeners = async () => {
  const container = document.getElementById('insuranceList');
  if (!container) return;
  const user = getUser();
  if (!user) return;

  // Policy Form logic
  const showPolBtn = document.getElementById('showAddPolicyBtn');
  const cancelPolBtn = document.getElementById('cancelPolicyBtn');
  const polContainer = document.getElementById('addPolicyContainer');
  const polForm = document.getElementById('addPolicyForm');

  if (showPolBtn) showPolBtn.onclick = () => polContainer.style.display = 'block';
  if (cancelPolBtn) cancelPolBtn.onclick = () => polContainer.style.display = 'none';

  if (polForm) {
    polForm.onsubmit = async (e) => {
      e.preventDefault();
      try {
        await InsuranceAPI.createPolicy({
          patient_id: user.id,
          provider_name: document.getElementById('policyProvider').value,
          policy_number: document.getElementById('policyNumber').value,
          start_date: document.getElementById('policyValidFrom').value,
          expiry_date: document.getElementById('policyValidUntil').value
        });
        alert('Đã lưu thẻ bảo hiểm thành công!');
        polContainer.style.display = 'none';
        loadPolicies();
      } catch (err) { alert(getErrorMessage(err, 'Lỗi lưu thẻ bảo hiểm')); }
    };
  }

  // Claim Form logic
  const showClaimBtn = document.getElementById('showAddClaimBtn');
  const cancelClaimBtn = document.getElementById('cancelClaimBtn');
  const claimContainer = document.getElementById('addClaimContainer');
  const claimForm = document.getElementById('addClaimForm');

  if (showClaimBtn) showClaimBtn.onclick = () => claimContainer.style.display = 'block';
  if (cancelClaimBtn) cancelClaimBtn.onclick = () => claimContainer.style.display = 'none';

  if (claimForm) {
    claimForm.onsubmit = async (e) => {
      e.preventDefault();
      try {
        const amount = document.getElementById('claimAmount').value;
        const dummyApptId = crypto.randomUUID ? crypto.randomUUID() : '00000000-0000-0000-0000-000000000000';
        await InsuranceAPI.createClaim({
          patient_id: user.id,
          policy: document.getElementById('claimPolicyId').value,
          appointment_id: dummyApptId,
          total_amount: amount,
          claimed_amount: amount
        });
        alert('Đã nộp yêu cầu bồi thường!');
        claimContainer.style.display = 'none';
        loadClaims();
      } catch (err) { alert(getErrorMessage(err, 'Lỗi nộp claim')); }
    };
  }

  // Load Policies
  const loadPolicies = async () => {
    try {
      const data = await InsuranceAPI.getPolicies();
      const policies = data.results || data || [];
      
      if (policies.length === 0) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No insurance policies found.</div>`;
        return;
      }

      container.innerHTML = policies.map(p => `
        <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1.5rem;">
          <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-bottom: 0.5rem;">${p.provider_name}</h3>
          <p style="margin-bottom: 0.5rem; font-size: 0.95rem;"><strong>Policy #:</strong> ${p.policy_number}</p>
          <span style="display: inline-block; padding: 4px 10px; background: ${p.is_active ? '#def7ec' : '#fde8e8'}; color: ${p.is_active ? '#03543f' : '#9b1c1c'}; border-radius: 12px; font-size: 0.8rem; font-weight: bold; margin-bottom: 0.8rem;">
            ${p.is_active ? 'ACTIVE' : 'INACTIVE'}
          </span>
          <button class="btn btn-secondary btn-sm check-eligibility-btn" style="width: 100%;" data-id="${p.id}">Kiểm tra Quyền lợi</button>
        </div>
      `).join('');

      document.querySelectorAll('.check-eligibility-btn').forEach(btn => {
        btn.onclick = async (e) => {
          try {
            const res = await InsuranceAPI.checkEligibility(e.target.dataset.id);
            alert(`Kết quả kiểm tra BHYT: ${res.status || 'Hợp lệ và đang hoạt động'}`);
          } catch (err) { alert(getErrorMessage(err, 'Kiểm tra thất bại.')); }
        };
      });

    } catch (e) {
      const msg = getErrorMessage(e, 'Failed to load policies.');
      container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">${msg}</div>`;
    }
  };

  // Load Claims
  const claimsContainer = document.getElementById('claimsList');
  const loadClaims = async () => {
    try {
      const data = await InsuranceAPI.getClaims();
      const claims = data.results || data || [];

      if (claims.length === 0) {
        claimsContainer.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No claims submitted yet.</div>`;
        return;
      }

      claimsContainer.innerHTML = claims.map(c => `
        <div class="stat-card glass-panel" style="align-items: flex-start; padding: 1.5rem;">
          <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin-bottom: 0.5rem;">Amount: ${Number(c.amount_claimed).toLocaleString()} VND</h3>
          <p style="margin-bottom: 0.5rem; font-size: 0.95rem;"><strong>Status:</strong> ${c.status || 'SUBMITTED'}</p>
        </div>
      `).join('');
    } catch (e) {
      claimsContainer.innerHTML = `<p class="text-muted">Chưa có thông tin bồi thường.</p>`;
    }
  };

  loadPolicies();
  loadClaims();
};
