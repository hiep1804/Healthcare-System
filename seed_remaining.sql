-- current_medications
INSERT INTO current_medications (id, patient_id, drug_name, dosage, frequency, prescribed_by, is_active, created_at, updated_at)
VALUES (gen_random_uuid(), '439a3cc6-096d-49c4-b39d-b16f94fd4368', 'Amlodipine', '5mg', 'Once daily', '', TRUE, NOW(), NOW()) ON CONFLICT DO NOTHING;

-- notification_templates
INSERT INTO notification_templates (id, code, channel, subject_template, body_template, created_at, updated_at)
VALUES (gen_random_uuid(), 'APPT_REMINDER', 'EMAIL', 'Reminder: Appointment Tomorrow', 'You have an appointment tomorrow.', NOW(), NOW()) ON CONFLICT DO NOTHING;

-- plans
INSERT INTO plans (id, code, name, description, price, billing_cycle, is_active, created_at, updated_at)
VALUES ('e8a61cb3-e5e6-42fc-a7bc-c15be9975b94', 'PREMIUM', 'Premium Plan', 'Full access', 1000000, 'MONTHLY', TRUE, NOW(), NOW()) ON CONFLICT DO NOTHING;

-- insurance_policies
INSERT INTO insurance_policies (id, patient_id, provider_name, policy_number, start_date, expiry_date, status, co_pay_percentage, created_at, updated_at)
VALUES (gen_random_uuid(), '439a3cc6-096d-49c4-b39d-b16f94fd4368', 'Bao Viet', 'BV123456', CURRENT_DATE, CURRENT_DATE + 365, 'ACTIVE', 20.00, NOW(), NOW()) ON CONFLICT DO NOTHING;
