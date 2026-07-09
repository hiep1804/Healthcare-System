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

const BASE_URL = 'http://127.0.0.1';

export const getToken = () => localStorage.getItem('access_token');
export const setToken = (token) => localStorage.setItem('access_token', token);
export const removeToken = () => localStorage.removeItem('access_token');
export const getUser = () => JSON.parse(localStorage.getItem('user'));
export const setUser = (user) => localStorage.setItem('user', JSON.stringify(user));

export const apiFetch = async (serviceName, endpoint, options = {}) => {
  const port = API_PORTS[serviceName];
  if (!port) throw new Error(`Unknown service: ${serviceName}`);

  const url = `${BASE_URL}:${port}/api/v1${endpoint}`;
  
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
    data = await response.json();
  } else if (response.status !== 204) {
    data = await response.text();
  }

  if (!response.ok) {
    throw { status: response.status, data };
  }

  return data;
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
};

// 2. Patient Service
export const PatientAPI = {
  getProfile: (patientId) => apiFetch('patient', `/patients/${patientId}`).catch(() => null), // Return null if not created yet
  createProfile: (data) => apiFetch('patient', `/patients`, { method: 'POST', body: JSON.stringify(data) }),
  updateProfile: (patientId, data) => apiFetch('patient', `/patients/${patientId}`, { method: 'PATCH', body: JSON.stringify(data) })
};

// 3. Provider Service
export const ProviderAPI = {
  getProviders: () => apiFetch('provider', '/providers'),
  getSpecialties: () => apiFetch('provider', '/specialties')
};

// 4. Appointment Service
export const AppointmentAPI = {
  getAppointments: () => apiFetch('appointment', '/appointments'),
  createAppointment: (data) => apiFetch('appointment', '/appointments', { method: 'POST', body: JSON.stringify(data) })
};

// 5. Consultation Service
export const ConsultationAPI = {
  getConsultations: () => apiFetch('consultation', '/consultations')
};

// 6. Medical Record Service
export const MedicalRecordAPI = {
  getRecords: (patientId) => apiFetch('medical_record', `/patients/${patientId}/records`)
};

// 7. Notification Service
export const NotificationAPI = {
  getTemplates: () => apiFetch('notification', '/notification-templates')
};

// 8. Audit Service
export const AuditAPI = {
  getEvents: () => apiFetch('audit', '/audit/events')
};

// 9. Subscription Service
export const SubscriptionAPI = {
  getPlans: () => apiFetch('subscription', '/plans')
};

// 10. Insurance Service
export const InsuranceAPI = {
  getPolicies: () => apiFetch('insurance', '/insurance-policies')
};
