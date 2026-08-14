const API_PORTS = {
  identity: 8001,
  patient: 8002,
  provider: 8003,
  appointment: 8004,
  consultation: 8005,
  medical_record: 8006,
  notification: 8007,
  audit: 8008,
  subscription: 8009,
  insurance: 8010,
};
const BASE_URL = 'http://127.0.0.1:8000'; // API Gateway

export const getToken = () => localStorage.getItem('access_token');
export const setToken = (token) => localStorage.setItem('access_token', token);
export const removeToken = () => localStorage.removeItem('access_token');
export const getUser = () => JSON.parse(localStorage.getItem('user'));
export const setUser = (user) => localStorage.setItem('user', JSON.stringify(user));

export const apiFetch = async (serviceName, endpoint, options = {}) => {
  // We ignore serviceName now because API Gateway routes based on the endpoint path itself!
  const url = `${BASE_URL}/api/v1${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeToken();
    window.location.hash = '#/login';
    throw new Error('Unauthorized');
  }

  const contentType = response.headers.get('content-type');
  let data = null;
  if (contentType && contentType.includes('application/json')) {
    const json = await response.json();
    data = json.data !== undefined ? json.data : json;
  } else if (response.status !== 204) {
    data = await response.text();
  }

  if (!response.ok) {
    throw { status: response.status, data };
  }

  return data;
};

// Helper function to extract error message from API response
export const getErrorMessage = (error, defaultMsg = 'An error occurred') => {
  if (error && error.data) {
    if (typeof error.data === 'string') return error.data;
    if (error.data.error) {
      if (typeof error.data.error === 'string') return error.data.error;
      if (error.data.error.message) return error.data.error.message;
      if (error.data.error.detail) return error.data.error.detail;
    }
    if (error.data.detail) return error.data.detail;
    
    // Extract first array error if it's a validation dict
    const keys = Object.keys(error.data);
    if (keys.length > 0 && Array.isArray(error.data[keys[0]])) {
      return `${keys[0]}: ${error.data[keys[0]][0]}`;
    }
    return JSON.stringify(error.data);
  }
  return error.message || defaultMsg;
};

// 1. Identity Service
export const AuthAPI = {
  login: (username, password) => apiFetch('identity', '/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  }),
  register: (userData) => apiFetch('identity', '/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData)
  }),
  getMe: () => apiFetch('identity', '/users/me'),
  updateMe: (data) => apiFetch('identity', '/users/me', { method: 'PATCH', body: JSON.stringify(data) }),
  getUsers: () => apiFetch('identity', '/users'),
  updateUserStatus: (userId, status, reason = '') => apiFetch('identity', `/users/${userId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, reason })
  }),
  assignRole: (userId, role) => apiFetch('identity', `/users/${userId}/roles`, {
    method: 'POST',
    body: JSON.stringify({ role })
  })
};

// 2. Patient Service
export const PatientAPI = {
  getPatients: () => apiFetch('patient', '/patients'),
  getProfile: (patientId) => apiFetch('patient', `/patients/${patientId}`).catch(() => null),
  createProfile: (data) => apiFetch('patient', `/patients`, { method: 'POST', body: JSON.stringify(data) }),
  updateProfile: (patientId, data) => apiFetch('patient', `/patients/${patientId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getMe: () => apiFetch('patient', '/patients/me').catch(() => null),
  updateMe: (data) => apiFetch('patient', '/patients/me', { method: 'PATCH', body: JSON.stringify(data) }),
  // Allergies
  getAllergies: (patientId) => apiFetch('patient', `/patients/${patientId}/allergies`),
  addAllergy: (patientId, data) => apiFetch('patient', `/patients/${patientId}/allergies`, { method: 'POST', body: JSON.stringify(data) }),
  // Conditions
  getConditions: (patientId) => apiFetch('patient', `/patients/${patientId}/conditions`),
  addCondition: (patientId, data) => apiFetch('patient', `/patients/${patientId}/conditions`, { method: 'POST', body: JSON.stringify(data) }),
  // Medications
  getMedications: (patientId) => apiFetch('patient', `/patients/${patientId}/medications`),
  addMedication: (patientId, data) => apiFetch('patient', `/patients/${patientId}/medications`, { method: 'POST', body: JSON.stringify(data) }),
  // Consents
  getConsents: (patientId) => apiFetch('patient', `/patients/${patientId}/consents`),
  createConsent: (patientId, data) => apiFetch('patient', `/patients/${patientId}/consents`, { method: 'POST', body: JSON.stringify(data) }),
  revokeConsent: (patientId, consentId) => apiFetch('patient', `/patients/${patientId}/consents/${consentId}`, { method: 'DELETE' })
};

// 3. Provider Service
export const ProviderAPI = {
  getProviders: (params = '') => apiFetch('provider', `/providers${params ? '?' + params : ''}`),
  getSpecialties: () => apiFetch('provider', '/specialties'),
  createSpecialty: (data) => apiFetch('provider', '/specialties', { method: 'POST', body: JSON.stringify(data) }),
  createProfile: (data) => apiFetch('provider', '/providers', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => apiFetch('provider', '/providers/me').catch(() => null),
  updateMe: (data) => apiFetch('provider', '/providers/me', { method: 'PATCH', body: JSON.stringify(data) }),
  getLicenses: (providerId) => apiFetch('provider', `/providers/${providerId}/licenses`),
  uploadLicense: (providerId, data) => apiFetch('provider', `/providers/${providerId}/licenses`, { method: 'POST', body: JSON.stringify(data) }),
  verifyProvider: (providerId, status, notes = '') => {
    let statusValue = status;
    if (status === true) statusValue = 'VERIFIED';
    else if (status === false) statusValue = 'REJECTED';
    return apiFetch('provider', `/providers/${providerId}/verification`, {
      method: 'PATCH',
      body: JSON.stringify({ status: statusValue, notes })
    });
  },
  getServices: (providerId) => apiFetch('provider', `/providers/${providerId}/services`),
  createService: (providerId, data) => apiFetch('provider', `/providers/${providerId}/services`, { method: 'POST', body: JSON.stringify(data) }),
  updateService: (providerId, serviceId, data) => apiFetch('provider', `/providers/${providerId}/services/${serviceId}`, { method: 'PATCH', body: JSON.stringify(data) })
};

// 4. Appointment Service
export const AppointmentAPI = {
  getAppointments: () => apiFetch('appointment', '/appointments'),
  getProviderSlots: (providerId) => apiFetch('appointment', `/appointments/providers/${providerId}/slots`),
  createSchedule: (providerId, data) => apiFetch('appointment', `/appointments/providers/${providerId}/schedules`, { method: 'POST', body: JSON.stringify(data) }),
  generateSlots: (providerId, data) => apiFetch('appointment', `/appointments/providers/${providerId}/slots/generate`, { method: 'POST', body: JSON.stringify(data) }),
  holdSlot: (data) => apiFetch('appointment', '/appointments/hold', { method: 'POST', body: JSON.stringify(data) }),
  createAppointment: (data) => apiFetch('appointment', '/appointments', { method: 'POST', body: JSON.stringify(data) }),
  cancelAppointment: (id) => apiFetch('appointment', `/appointments/${id}/cancel`, { method: 'PATCH' }),
  confirmAppointment: (id) => apiFetch('appointment', `/appointments/${id}/confirm`, { method: 'PATCH' }),
  completeAppointment: (id) => apiFetch('appointment', `/appointments/${id}/complete`, { method: 'PATCH' })
};

// 5. Consultation Service
export const ConsultationAPI = {
  getConsultations: () => apiFetch('consultation', '/consultations'),
  getConsultation: (id) => apiFetch('consultation', `/consultations/${id}`),
  createConsultation: (data) => apiFetch('consultation', '/consultations', { method: 'POST', body: JSON.stringify(data) }),
  startConsultation: (id) => apiFetch('consultation', `/consultations/${id}/start`, { method: 'PATCH' }),
  completeConsultation: (id) => apiFetch('consultation', `/consultations/${id}/complete`, { method: 'PATCH' }),
  addNote: (id, data) => apiFetch('consultation', `/consultations/${id}/notes`, { method: 'POST', body: JSON.stringify(data) }),
  addDiagnosis: (id, data) => apiFetch('consultation', `/consultations/${id}/diagnoses`, { method: 'POST', body: JSON.stringify(data) }),
  createPrescription: (id, data) => apiFetch('consultation', `/consultations/${id}/prescriptions`, { method: 'POST', body: JSON.stringify(data) }),
  getPrescriptions: (id) => apiFetch('consultation', `/consultations/${id}/prescriptions`).catch(() => ({ id: null, items: [] }))
};

// 6. Medical Record Service
export const MedicalRecordAPI = {
  getRecords: (patientId) => apiFetch('medical_record', `/patients/${patientId}/records`),
  createRecord: (patientId, data) => apiFetch('medical_record', `/patients/${patientId}/records`, { method: 'POST', body: JSON.stringify(data) }),
  uploadDocument: (patientId, data) => apiFetch('medical_record', `/patients/${patientId}/documents`, { method: 'POST', body: JSON.stringify(data) }),
  getVitals: (patientId) => apiFetch('medical_record', `/patients/${patientId}/vitals`),
  recordVitals: (patientId, data) => apiFetch('medical_record', `/patients/${patientId}/vitals`, { method: 'POST', body: JSON.stringify(data) }),
  getLabResults: (patientId) => apiFetch('medical_record', `/patients/${patientId}/lab-results`),
  createLabResult: (patientId, data) => apiFetch('medical_record', `/patients/${patientId}/lab-results`, { method: 'POST', body: JSON.stringify(data) })
};

// 7. Notification Service
export const NotificationAPI = {
  getTemplates: () => apiFetch('notification', '/notification-templates'),
  createTemplate: (data) => apiFetch('notification', '/notification-templates', { method: 'POST', body: JSON.stringify(data) }),
  updateTemplate: (id, data) => apiFetch('notification', `/notification-templates/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  sendNotification: (data) => apiFetch('notification', '/notifications/send', { method: 'POST', body: JSON.stringify(data) }),
  getJobs: () => apiFetch('notification', '/notification-jobs'),
  retryJob: (id) => apiFetch('notification', `/notification-jobs/${id}/retry`, { method: 'POST' })
};

// 8. Audit Service
export const AuditAPI = {
  getEvents: (query = '') => apiFetch('audit', `/audit/search${query ? '?' + query : ''}`)
};

// 9. Subscription Service
export const SubscriptionAPI = {
  getPlans: (params = '') => apiFetch('subscription', `/plans${params ? '?' + params : ''}`),
  createPlan: (data) => apiFetch('subscription', '/plans', { method: 'POST', body: JSON.stringify(data) }),
  updatePlan: (id, data) => apiFetch('subscription', `/plans/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deletePlan: (id) => apiFetch('subscription', `/plans/${id}`, { method: 'DELETE' }),
  getSubscriptions: () => apiFetch('subscription', '/subscriptions'),
  subscribePlan: (planId) => {
    const user = getUser();
    return apiFetch('subscription', '/subscriptions', {
      method: 'POST',
      body: JSON.stringify({
        patient_id: user?.id,
        plan: planId
      })
    });
  },
  cancelSubscription: (id) => apiFetch('subscription', `/subscriptions/${id}/cancel`, { method: 'PATCH' }),
  getUsage: (id) => apiFetch('subscription', `/subscriptions/${id}/usage`)
};

// 10. Insurance Service
export const InsuranceAPI = {
  getPolicies: () => apiFetch('insurance', '/insurance-policies'),
  createPolicy: (data) => apiFetch('insurance', '/insurance-policies', { method: 'POST', body: JSON.stringify(data) }),
  checkEligibility: (policy_id, data = {}) => apiFetch('insurance', `/insurance-policies/${policy_id}/eligibility-check`, { method: 'POST', body: JSON.stringify(data) }),
  getClaims: () => apiFetch('insurance', '/claims'),
  createClaim: (data) => apiFetch('insurance', '/claims', { method: 'POST', body: JSON.stringify(data) })
};

// 11. AI CDS Service
export const CDSAPI = {
  createConversation: (data) => apiFetch('cds', '/cds/conversations', { method: 'POST', body: JSON.stringify(data) }),
  getConversation: (id) => apiFetch('cds', `/cds/conversations/${id}`),
  sendMessage: (id, content) => apiFetch('cds', `/cds/conversations/${id}/messages`, { method: 'POST', body: JSON.stringify({ content }) }),
  actOnRecommendation: (recId, action, doctor_note = '') => apiFetch('cds', `/cds/recommendations/${recId}`, {
    method: 'PATCH',
    body: JSON.stringify({ action, doctor_note })
  }),
  checkDrugInteractions: (drug_names, patient_allergies = []) => apiFetch('cds', '/cds/drug-interactions', {
    method: 'POST',
    body: JSON.stringify({ drug_names, patient_allergies })
  })
};

