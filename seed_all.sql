-- specialties
INSERT INTO specialties (id, name, description, created_at) VALUES ('9f87422b-5b23-455a-947b-118df28d6330', 'Cardiology', 'Heart related', NOW()) ON CONFLICT DO NOTHING;

-- clinics
INSERT INTO clinics (id, name, address, contact_number, description, created_at) VALUES ('a42a0b4d-9db8-403d-82d6-444f6f8bb1a2', 'City Hospital', 'HCM City', '0987654321', '', NOW()) ON CONFLICT DO NOTHING;

-- Update provider to attach to clinic
UPDATE providers SET clinic_id = 'a42a0b4d-9db8-403d-82d6-444f6f8bb1a2' WHERE id = '2c4afd8f-93ff-4eb9-ac7e-740db1265a07';

-- provider_services
INSERT INTO provider_services (id, provider_id, specialty_id, service_name, price, duration_minutes, created_at, updated_at) VALUES ('1b8d60c2-550a-4fb4-b816-0155b40d6cfa', '2c4afd8f-93ff-4eb9-ac7e-740db1265a07', '9f87422b-5b23-455a-947b-118df28d6330', 'General Consultation', 500000, 30, NOW(), NOW()) ON CONFLICT DO NOTHING;

-- time_slots
INSERT INTO time_slots (id, provider_id, date, start_time, end_time, status, hold_expires_at, created_at) 
VALUES ('c38e974e-6e8d-4a11-b44c-1d5d518d6bc1', '2c4afd8f-93ff-4eb9-ac7e-740db1265a07', CURRENT_DATE + 1, '10:00:00', '10:30:00', 'BOOKED', NULL, NOW()) ON CONFLICT DO NOTHING;

-- appointments
INSERT INTO appointments (id, patient_id, provider_id, slot_id, service_id, status, hold_expires_at, amount, currency, notes, created_at, updated_at) 
VALUES ('c38e974e-6e8d-4a11-b44c-1d5d518d6bc3', '439a3cc6-096d-49c4-b39d-b16f94fd4368', '2c4afd8f-93ff-4eb9-ac7e-740db1265a07', 'c38e974e-6e8d-4a11-b44c-1d5d518d6bc1', '1b8d60c2-550a-4fb4-b816-0155b40d6cfa', 'CONFIRMED', NULL, 500000, 'VND', 'Routine checkup', NOW(), NOW()) ON CONFLICT DO NOTHING;

-- allergies
INSERT INTO allergies (id, patient_id, allergen, severity, reaction, note, is_active, created_at, updated_at)
VALUES (gen_random_uuid(), '439a3cc6-096d-49c4-b39d-b16f94fd4368', 'Penicillin', 'HIGH', 'Rash', '', TRUE, NOW(), NOW());

-- medical_conditions
INSERT INTO medical_conditions (id, patient_id, condition_name, icd_code, status, note, created_at, updated_at)
VALUES (gen_random_uuid(), '439a3cc6-096d-49c4-b39d-b16f94fd4368', 'Hypertension', 'I10', 'ACTIVE', '', NOW(), NOW());

-- current_medications
INSERT INTO current_medications (id, patient_id, drug_name, dosage, frequency, is_active, created_at, updated_at)
VALUES (gen_random_uuid(), '439a3cc6-096d-49c4-b39d-b16f94fd4368', 'Amlodipine', '5mg', 'Once daily', TRUE, NOW(), NOW());

-- notification_templates
INSERT INTO notification_templates (id, code, name, type, title_template, body_template, created_at, updated_at)
VALUES (gen_random_uuid(), 'APPT_REMINDER', 'Appointment Reminder', 'SYSTEM', 'Reminder: Appointment Tomorrow', 'You have an appointment tomorrow.', NOW(), NOW());

-- plans
INSERT INTO plans (id, code, name, description, type, billing_cycle, price, currency, is_active, max_users, max_storage_gb, created_at, updated_at)
VALUES ('e8a61cb3-e5e6-42fc-a7bc-c15be9975b94', 'PREMIUM', 'Premium Plan', 'Full access', 'CLINIC', 'MONTHLY', 1000000, 'VND', TRUE, 10, 50, NOW(), NOW()) ON CONFLICT DO NOTHING;

-- insurance_policies (if exists)
INSERT INTO insurance_policies (id, patient_id, provider_name, policy_number, group_number, plan_type, status, created_at, updated_at)
VALUES (gen_random_uuid(), '439a3cc6-096d-49c4-b39d-b16f94fd4368', 'Bao Viet', 'BV123456', '', 'PPO', 'ACTIVE', NOW(), NOW());

-- audit_logs
INSERT INTO audit_logs (id, event_type, user_id, user_role, resource_type, resource_id, action, status, ip_address, created_at)
VALUES (gen_random_uuid(), 'SYSTEM_EVENT', NULL, '', 'System', '', 'Seed Data', 'SUCCESS', '127.0.0.1', NOW());
