import { Navbar } from '../components/Navbar.js';
import { SubscriptionAPI, getUser, getErrorMessage } from '../api.js';

export const SubscriptionsPage = () => {
  const user = getUser();
  const isAdmin = user && user.role === 'ADMIN';

  return `
    ${Navbar()}
    <div class="container animate-fade-in" style="padding-bottom: 4rem;">
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--primary-blue);">Gói Dịch vụ & Quyền lợi Chăm sóc Sức khỏe</h1>
        <p class="text-muted">Lựa chọn gói dịch vụ chăm sóc sức khỏe phù hợp và quản lý các gói đã kích hoạt.</p>
      </div>

      ${isAdmin ? `
        <!-- ADMIN CREATE PLAN SECTION -->
        <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin: 0;">Tạo Gói Dịch vụ Mới (Admin)</h2>
            <button id="showAddPlanBtn" class="btn btn-secondary btn-sm">+ Tạo Gói Mới</button>
          </div>

          <div id="addPlanContainer" style="display: none; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <form id="addPlanForm">
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                <div class="form-group"><label class="form-label">Tên gói</label><input type="text" id="planName" class="form-input" required placeholder="Gói Vàng" /></div>
                <div class="form-group"><label class="form-label">Mã gói (Code)</label><input type="text" id="planCode" class="form-input" required placeholder="GOLD_PLAN" /></div>
                <div class="form-group"><label class="form-label">Giá (VND)</label><input type="number" id="planPrice" class="form-input" required placeholder="500000" /></div>
              </div>
              <div class="form-group"><label class="form-label">Mô tả</label><input type="text" id="planDesc" class="form-input" placeholder="Mô tả quyền lợi" /></div>
              <button type="submit" class="btn btn-primary btn-sm">Tạo Gói</button>
              <button type="button" id="cancelPlanBtn" class="btn btn-secondary btn-sm">Hủy</button>
            </form>
          </div>
        </div>
      ` : ''}

      <!-- ACTIVE SUBSCRIPTIONS SECTION -->
      <div class="glass-panel" style="padding: 2rem; margin-bottom: 2rem;">
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">Gói dịch vụ đang kích hoạt của tôi</h2>
        <div id="mySubscriptionsList">Đang tải gói dịch vụ...</div>
      </div>

      <!-- AVAILABLE PLANS GRID -->
      <div class="glass-panel" style="padding: 2rem;">
        <h2 style="font-size: 1.3rem; color: var(--primary-blue); margin-bottom: 1rem;">Các Gói Dịch vụ Khả dụng</h2>
        <div id="plansList" class="dashboard-grid">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
            Đang tải các gói dịch vụ...
          </div>
        </div>
      </div>
    </div>
  `;
};

export const attachSubscriptionsListeners = async () => {
  const container = document.getElementById('plansList');
  if (!container) return;

  const user = getUser();
  const isAdmin = user && user.role === 'ADMIN';

  // Admin Plan form
  if (isAdmin) {
    const showBtn = document.getElementById('showAddPlanBtn');
    const cancelBtn = document.getElementById('cancelPlanBtn');
    const planContainer = document.getElementById('addPlanContainer');
    const planForm = document.getElementById('addPlanForm');

    if (showBtn) showBtn.onclick = () => planContainer.style.display = 'block';
    if (cancelBtn) cancelBtn.onclick = () => planContainer.style.display = 'none';

    if (planForm) {
      planForm.onsubmit = async (e) => {
        e.preventDefault();
        try {
          await SubscriptionAPI.createPlan({
            name: document.getElementById('planName').value,
            code: document.getElementById('planCode').value,
            price: document.getElementById('planPrice').value,
            description: document.getElementById('planDesc').value,
            billing_cycle: 'MONTHLY'
          });
          alert('Đã tạo gói mới!');
          planContainer.style.display = 'none';
          loadPlans();
        } catch (err) { alert(getErrorMessage(err, 'Lỗi tạo gói')); }
      };
    }
  }

  // Load My Active Subscriptions
  const mySubContainer = document.getElementById('mySubscriptionsList');
  const loadMySubscriptions = async () => {
    try {
      const data = await SubscriptionAPI.getSubscriptions();
      let subs = [];
      if (Array.isArray(data)) {
        subs = data;
      } else if (data && data.id) {
        subs = [data];
      } else if (data && data.results) {
        subs = data.results;
      }

      if (subs.length === 0) {
        mySubContainer.innerHTML = '<p class="text-muted">Bạn chưa đăng ký gói dịch vụ nào.</p>';
        return;
      }

      mySubContainer.innerHTML = subs.map(s => {
        const planName = s.plan_detail?.name || `Gói #${s.id ? s.id.substring(0,8) : 'Active'}`;
        return `
          <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(59,130,246,0.3); padding: 1.2rem; border-radius: 8px; margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <h3 style="color: var(--primary-blue); font-size: 1.1rem; margin: 0 0 0.3rem 0;">${planName}</h3>
              <p style="margin: 0; font-size: 0.9rem;">Trạng thái: <span class="badge badge-success">${s.status || 'ACTIVE'}</span></p>
              <p style="margin: 0.2rem 0 0 0; font-size: 0.85rem;" class="text-muted">Hạn sử dụng: ${s.current_period_end ? new Date(s.current_period_end).toLocaleDateString() : 'N/A'}</p>
            </div>
            <button class="btn btn-secondary btn-sm cancel-sub-btn" data-id="${s.id}">Hủy gói</button>
          </div>
        `;
      }).join('');

      document.querySelectorAll('.cancel-sub-btn').forEach(btn => {
        btn.onclick = async (e) => {
          if (confirm('Bạn có chắc muốn hủy gói này?')) {
            try {
              await SubscriptionAPI.cancelSubscription(e.target.dataset.id);
              alert('Đã hủy gói.');
              loadMySubscriptions();
            } catch (err) { alert(getErrorMessage(err, 'Lỗi hủy gói.')); }
          }
        };
      });

    } catch (e) {
      if (e && e.status === 404) {
        mySubContainer.innerHTML = '<p class="text-muted">Bạn chưa đăng ký gói dịch vụ nào.</p>';
      } else {
        mySubContainer.innerHTML = '<p class="text-muted">Không có thông tin gói đang sử dụng.</p>';
      }
    }
  };

  // Load Available Plans
  const loadPlans = async () => {
    try {
      const data = await SubscriptionAPI.getPlans(isAdmin ? 'all=true' : '');
      const plans = data.results || data || [];
      
      if (plans.length === 0) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">No subscription plans found.</div>`;
        return;
      }

      container.innerHTML = plans.map(p => {
        const isActivePlan = p.is_active !== false;
        let actionBtnHTML = `<button class="btn btn-primary subscribe-btn" style="width: 100%;" data-id="${p.id}">Đăng ký Gói này</button>`;

        if (isAdmin) {
          if (isActivePlan) {
            actionBtnHTML = `<button class="btn btn-secondary deactivate-plan-btn" style="width: 100%; color: #ef4444; border-color: #ef4444;" data-id="${p.id}">🚫 Vô hiệu hóa (Hủy gói)</button>`;
          } else {
            actionBtnHTML = `<button class="btn btn-secondary activate-plan-btn" style="width: 100%; color: #10b981; border-color: #10b981;" data-id="${p.id}">✓ Kích hoạt lại Gói</button>`;
          }
        }

        return `
          <div class="stat-card glass-panel" style="align-items: center; text-align: center; padding: 2rem 1.5rem; opacity: ${isActivePlan ? '1' : '0.6'};">
            <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 0.5rem;">
              <span class="badge ${isActivePlan ? 'badge-success' : 'badge-warning'}">${isActivePlan ? 'HOẠT ĐỘNG' : 'ĐÃ VÔ HIỆU HÓA'}</span>
            </div>
            <h2 style="color: var(--primary-blue); font-size: 1.4rem; margin-bottom: 0.5rem;">${p.name}</h2>
            <div style="font-size: 1.8rem; font-weight: bold; margin: 0.8rem 0;">${Number(p.price || p.price_per_month || 0).toLocaleString()} VND</div>
            <p style="margin-bottom: 1.5rem; font-size: 0.9rem; color: var(--text-muted); min-height: 40px;">${p.description || 'Quyền lợi khám bệnh ưu đãi.'}</p>
            ${actionBtnHTML}
          </div>
        `;
      }).join('');

      // Patient subscribe event
      document.querySelectorAll('.subscribe-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const planId = e.target.dataset.id;
          if (confirm('Xác nhận đăng ký gói dịch vụ này?')) {
            try {
              await SubscriptionAPI.subscribePlan(planId);
              alert('Đăng ký thành công!');
              loadMySubscriptions();
            } catch (err) { alert(getErrorMessage(err, 'Lỗi đăng ký gói.')); }
          }
        };
      });

      // Admin deactivate plan event
      document.querySelectorAll('.deactivate-plan-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const planId = e.target.dataset.id;
          if (confirm('Bạn có chắc muốn VÔ HIỆU HÓA (Hủy) gói dịch vụ này? Bệnh nhân sẽ không thể đăng ký mới gói này nữa.')) {
            try {
              await SubscriptionAPI.deletePlan(planId);
              alert('Đã vô hiệu hóa gói dịch vụ thành công!');
              loadPlans();
            } catch (err) { alert(getErrorMessage(err, 'Lỗi vô hiệu hóa gói.')); }
          }
        };
      });

      // Admin activate plan event
      document.querySelectorAll('.activate-plan-btn').forEach(btn => {
        btn.onclick = async (e) => {
          const planId = e.target.dataset.id;
          if (confirm('Xác nhận KÍCH HOẠT LẠI gói dịch vụ này?')) {
            try {
              await SubscriptionAPI.updatePlan(planId, { is_active: true });
              alert('Đã kích hoạt lại gói dịch vụ thành công!');
              loadPlans();
            } catch (err) { alert(getErrorMessage(err, 'Lỗi kích hoạt lại gói.')); }
          }
        };
      });

    } catch (e) {
      const msg = getErrorMessage(e, 'Failed to load plans.');
      container.innerHTML = `<div class="alert alert-error" style="grid-column: 1 / -1;">${msg}</div>`;
    }
  };

  loadMySubscriptions();
  loadPlans();
};
