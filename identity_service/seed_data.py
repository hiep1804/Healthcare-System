import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User, Role, UserRole

def seed():
    print("Seeding database...")
    # Create roles
    roles = ['PATIENT', 'DOCTOR', 'ADMIN', 'PROVIDER_ADMIN']
    role_objs = {}
    for r in roles:
        role_objs[r], created = Role.objects.get_or_create(name=r, defaults={'description': f'{r} role'})
        if created:
            print(f"Created role {r}")
    
    # Create admin user
    if not User.objects.filter(email='admin@example.com').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123',
            first_name='System',
            last_name='Admin'
        )
        UserRole.objects.create(user=admin, role=role_objs['ADMIN'])
        print("Created admin@example.com (password123)")
    
    # Create test patient
    if not User.objects.filter(email='patient@example.com').exists():
        patient = User.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='password123',
            first_name='Nguyen',
            last_name='Van A'
        )
        UserRole.objects.create(user=patient, role=role_objs['PATIENT'])
        print("Created patient@example.com (password123)")

    # Create test doctor
    if not User.objects.filter(email='doctor@example.com').exists():
        doctor = User.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='password123',
            first_name='Tran',
            last_name='Van B'
        )
        UserRole.objects.create(user=doctor, role=role_objs['DOCTOR'])
        print("Created doctor@example.com (password123)")

    print("Seeding complete!")

if __name__ == '__main__':
    seed()
