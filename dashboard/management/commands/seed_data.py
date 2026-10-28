import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from departments.models import Department, Specialization
from doctors.models import Doctor
from appointments.models import Appointment
from patients.models import MedicalRecord
from pharmacy.models import Medicine, MedicineCategory, Prescription, PrescriptionItem

class Command(BaseCommand):
    help = "Seed complete hospital management system data."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting system seeding process..."))

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@medcarehospital.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.create(user=admin_user, role='ADMIN', phone='+1 800-555-0199', address='Main Hospital Tower, Floor 4')
            self.stdout.write(self.style.SUCCESS("Created Superuser: admin / admin123"))

        # 2. Create Departments
        departments_data = [
            {'name': 'Cardiology', 'code': 'CARD', 'description': 'Comprehensive cardiovascular medical care, heart surgery, ECG diagnostics, and cardiac rehabilitation.', 'icon_class': 'fa-heartbeat', 'image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80'},
            {'name': 'Neurology', 'code': 'NEUR', 'description': 'Expert care for neurological disorders, brain health, spinal ailments, stroke, and nerve diseases.', 'icon_class': 'fa-brain', 'image_url': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=800&q=80'},
            {'name': 'Orthopedics', 'code': 'ORTH', 'description': 'Advanced bone, joint replacement, fracture management, spine care, and sports injury therapies.', 'icon_class': 'fa-bone', 'image_url': 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=800&q=80'},
            {'name': 'Pediatrics', 'code': 'PEDI', 'description': 'Specialized medical care and wellness monitoring for infants, toddlers, adolescents, and teens.', 'icon_class': 'fa-baby', 'image_url': 'https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&w=800&q=80'},
            {'name': 'Dermatology', 'code': 'DERM', 'description': 'Treatment for skin disorders, allergies, cosmetic dermatology, hair loss, and laser therapies.', 'icon_class': 'fa-allergies', 'image_url': 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80'},
            {'name': 'General Medicine', 'code': 'GENM', 'description': 'Primary healthcare, chronic disease management, routine health screening, and preventative care.', 'icon_class': 'fa-stethoscope', 'image_url': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=800&q=80'},
        ]

        created_departments = {}
        for d in departments_data:
            dept_obj, _ = Department.objects.get_or_create(
                name=d['name'],
                defaults={
                    'code': d['code'],
                    'description': d['description'],
                    'icon_class': d['icon_class'],
                    'image_url': d['image_url'],
                    'is_active': True
                }
            )
            created_departments[d['name']] = dept_obj

        # 3. Create Specializations
        specs_data = [
            {'name': 'Interventional Cardiology', 'code': 'SPEC-CARD-01', 'dept': 'Cardiology', 'desc': 'Catheter-based treatment of structural heart diseases.'},
            {'name': 'Pediatric Cardiology', 'code': 'SPEC-CARD-02', 'dept': 'Cardiology', 'desc': 'Heart conditions and congenital defects in children.'},
            {'name': 'Neurosurgery & Spine', 'code': 'SPEC-NEUR-01', 'dept': 'Neurology', 'desc': 'Surgical management of brain tumors and spine trauma.'},
            {'name': 'Clinical Neurology', 'code': 'SPEC-NEUR-02', 'dept': 'Neurology', 'desc': 'Treatment of stroke, epilepsy, and Parkinson disease.'},
            {'name': 'Joint Replacement Surgery', 'code': 'SPEC-ORTH-01', 'dept': 'Orthopedics', 'desc': 'Hip, knee, and robotic joint reconstructions.'},
            {'name': 'Sports Medicine & Arthroscopy', 'code': 'SPEC-ORTH-02', 'dept': 'Orthopedics', 'desc': 'Ligament repair and athlete rehabilitation.'},
            {'name': 'Neonatology', 'code': 'SPEC-PEDI-01', 'dept': 'Pediatrics', 'desc': 'Intensive medical care for newborn infants.'},
            {'name': 'Cosmetic & Clinical Dermatology', 'code': 'SPEC-DERM-01', 'dept': 'Dermatology', 'desc': 'Skin laser treatment, allergy tests, and dermatosurgery.'},
            {'name': 'Internal Medicine & Diabetology', 'code': 'SPEC-GENM-01', 'dept': 'General Medicine', 'desc': 'Comprehensive diabetes and hypertension management.'},
        ]

        created_specs = {}
        for sp in specs_data:
            dept_obj = created_departments.get(sp['dept'])
            if dept_obj:
                spec_obj, _ = Specialization.objects.get_or_create(
                    name=sp['name'],
                    department=dept_obj,
                    defaults={'code': sp['code'], 'description': sp['desc'], 'is_active': True}
                )
                created_specs[sp['name']] = spec_obj

        # 4. Create Sample Doctors
        doctors_list = [
            {
                'doctor_id': 'DOC-1001',
                'username': 'dr_sarah',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'dept_name': 'Cardiology',
                'spec_name': 'Interventional Cardiology',
                'qualification': 'MBBS, MD (Cardiology), FACC',
                'experience': 14,
                'phone': '+1 (555) 234-8901',
                'email': 'sarah.jenkins@medcare.org',
                'consultation_fee': 150.00,
                'availability': 'Mon - Fri (09:00 AM - 04:00 PM)',
                'about': 'Dr. Sarah Jenkins is a renowned specialist in invasive cardiology with over 14 years of clinical experience in coronary interventions.',
                'image_url': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=800&q=80'
            },
            {
                'doctor_id': 'DOC-1002',
                'username': 'dr_robert',
                'first_name': 'Robert',
                'last_name': 'Chen',
                'dept_name': 'Neurology',
                'spec_name': 'Neurosurgery & Spine',
                'qualification': 'MBBS, MS (Neurosurgery), FRCS',
                'experience': 18,
                'phone': '+1 (555) 345-9012',
                'email': 'robert.chen@medcare.org',
                'consultation_fee': 200.00,
                'availability': 'Tue - Sat (10:00 AM - 05:00 PM)',
                'about': 'Dr. Robert Chen leads the Neurological Sciences division, specializing in complex neurosurgical procedures.',
                'image_url': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=800&q=80'
            },
            {
                'doctor_id': 'DOC-1003',
                'username': 'dr_emily',
                'first_name': 'Emily',
                'last_name': 'Watson',
                'dept_name': 'Pediatrics',
                'spec_name': 'Neonatology',
                'qualification': 'MBBS, DCH, MD (Pediatrics)',
                'experience': 10,
                'phone': '+1 (555) 456-0123',
                'email': 'emily.watson@medcare.org',
                'consultation_fee': 100.00,
                'availability': 'Mon - Sat (08:30 AM - 02:30 PM)',
                'about': 'Dr. Emily Watson is passionate about child nutrition, pediatric immunizations, and developmental health monitoring.',
                'image_url': 'https://images.unsplash.com/photo-1594824813566-88855ce78961?auto=format&fit=crop&w=800&q=80'
            },
            {
                'doctor_id': 'DOC-1004',
                'username': 'dr_michael',
                'first_name': 'Michael',
                'last_name': 'Vance',
                'dept_name': 'Orthopedics',
                'spec_name': 'Joint Replacement Surgery',
                'qualification': 'MBBS, MS (Orthopedics), MCh',
                'experience': 16,
                'phone': '+1 (555) 567-1234',
                'email': 'michael.vance@medcare.org',
                'consultation_fee': 180.00,
                'availability': 'Mon - Thu (11:00 AM - 06:00 PM)',
                'about': 'Dr. Michael Vance has conducted over 2,000 successful hip and knee replacement surgeries.',
                'image_url': 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=800&q=80'
            },
            {
                'doctor_id': 'DOC-1005',
                'username': 'dr_alisha',
                'first_name': 'Alisha',
                'last_name': 'Patel',
                'dept_name': 'Dermatology',
                'spec_name': 'Cosmetic & Clinical Dermatology',
                'qualification': 'MBBS, MD (Dermatology)',
                'experience': 9,
                'phone': '+1 (555) 678-2345',
                'email': 'alisha.patel@medcare.org',
                'consultation_fee': 120.00,
                'availability': 'Mon - Fri (10:00 AM - 04:00 PM)',
                'about': 'Dr. Alisha Patel specializes in advanced clinical skin diagnostics, anti-aging therapies, and corrective laser care.',
                'image_url': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=800&q=80'
            },
            {
                'doctor_id': 'DOC-1006',
                'username': 'dr_david',
                'first_name': 'David',
                'last_name': 'Miller',
                'dept_name': 'General Medicine',
                'spec_name': 'Internal Medicine & Diabetology',
                'qualification': 'MBBS, MD (Internal Medicine)',
                'experience': 12,
                'phone': '+1 (555) 789-3456',
                'email': 'david.miller@medcare.org',
                'consultation_fee': 80.00,
                'availability': 'Mon - Sat (09:00 AM - 05:00 PM)',
                'about': 'Dr. David Miller provides outpatient consultation for diabetes, hypertension, and preventative care.',
                'image_url': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=800&q=80'
            }
        ]

        created_doctors = []
        for doc_info in doctors_list:
            u, created = User.objects.get_or_create(
                username=doc_info['username'],
                defaults={
                    'email': doc_info['email'],
                    'first_name': doc_info['first_name'],
                    'last_name': doc_info['last_name'],
                    'is_staff': True
                }
            )
            if created:
                u.set_password('doctor123')
                u.save()
                UserProfile.objects.create(user=u, role='DOCTOR', phone=doc_info['phone'])

            department = created_departments.get(doc_info['dept_name'])
            spec_ref = created_specs.get(doc_info['spec_name'])
            
            doctor_obj, _ = Doctor.objects.get_or_create(
                name=f"{doc_info['first_name']} {doc_info['last_name']}",
                defaults={
                    'doctor_id': doc_info['doctor_id'],
                    'user': u,
                    'department': department,
                    'specialization_ref': spec_ref,
                    'specialization': doc_info['spec_name'],
                    'qualification': doc_info['qualification'],
                    'experience': doc_info['experience'],
                    'phone': doc_info['phone'],
                    'email': doc_info['email'],
                    'consultation_fee': doc_info['consultation_fee'],
                    'availability': doc_info['availability'],
                    'about_doctor': doc_info['about'],
                    'image_url': doc_info['image_url'],
                    'status': 'Active',
                    'is_available': True
                }
            )
            created_doctors.append(doctor_obj)

        # 5. Create Sample Patients
        patients_list = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com', 'phone': '+1 555-111-2222', 'dob': '1990-05-15', 'gender': 'M'},
            {'username': 'emma_wilson', 'first_name': 'Emma', 'last_name': 'Wilson', 'email': 'emma.w@example.com', 'phone': '+1 555-333-4444', 'dob': '1994-08-22', 'gender': 'F'},
            {'username': 'alex_smith', 'first_name': 'Alex', 'last_name': 'Smith', 'email': 'alex.smith@example.com', 'phone': '+1 555-555-6666', 'dob': '1985-11-03', 'gender': 'M'},
        ]

        created_patients = []
        for p_info in patients_list:
            pu, created = User.objects.get_or_create(
                username=p_info['username'],
                defaults={
                    'email': p_info['email'],
                    'first_name': p_info['first_name'],
                    'last_name': p_info['last_name']
                }
            )
            if created:
                pu.set_password('patient123')
                pu.save()
                UserProfile.objects.create(
                    user=pu,
                    role='PATIENT',
                    phone=p_info['phone'],
                    gender=p_info['gender'],
                    date_of_birth=p_info['dob'],
                    address='123 Healthcare Ave, Metro City'
                )
            created_patients.append(pu)

        # 6. Create Pharmacy Categories & Medicines
        med_cats = ['Antibiotics', 'Cardiovascular', 'Analgesics & Antipyretics', 'Antidiabetic', 'Respiratory']
        cat_objects = {}
        for cname in med_cats:
            cobj, _ = MedicineCategory.objects.get_or_create(name=cname)
            cat_objects[cname] = cobj

        today = datetime.date.today()
        medicines_data = [
            {'id': 'MED-1001', 'name': 'Amoxicillin 500mg', 'generic': 'Amoxicillin Trihydrate', 'cat': 'Antibiotics', 'mfg': 'Pfizer Labs', 'batch': 'AMX-2026-A1', 'qty': 120, 'price': 14.50, 'exp': today + datetime.timedelta(days=365)},
            {'id': 'MED-1002', 'name': 'Azithromycin 250mg', 'generic': 'Azithromycin Dihydrate', 'cat': 'Antibiotics', 'mfg': 'Sun Pharma', 'batch': 'AZT-2026-B4', 'qty': 85, 'price': 18.00, 'exp': today + datetime.timedelta(days=400)},
            {'id': 'MED-1003', 'name': 'Atorvastatin 20mg', 'generic': 'Atorvastatin Calcium', 'cat': 'Cardiovascular', 'mfg': 'Novartis', 'batch': 'ATV-2025-C9', 'qty': 60, 'price': 22.50, 'exp': today + datetime.timedelta(days=280)},
            {'id': 'MED-1004', 'name': 'Metoprolol Succinate 50mg', 'generic': 'Metoprolol', 'cat': 'Cardiovascular', 'mfg': 'AstraZeneca', 'batch': 'MET-2026-D2', 'qty': 10, 'price': 16.00, 'exp': today + datetime.timedelta(days=200)}, # Low stock
            {'id': 'MED-1005', 'name': 'Paracetamol 650mg', 'generic': 'Acetaminophen', 'cat': 'Analgesics & Antipyretics', 'mfg': 'GSK Consumer', 'batch': 'PCM-2026-E7', 'qty': 350, 'price': 4.50, 'exp': today + datetime.timedelta(days=500)},
            {'id': 'MED-1006', 'name': 'Ibuprofen 400mg', 'generic': 'Ibuprofen', 'cat': 'Analgesics & Antipyretics', 'mfg': 'Abbott Healthcare', 'batch': 'IBU-2026-F1', 'qty': 8, 'price': 8.00, 'exp': today + datetime.timedelta(days=300)}, # Low stock
            {'id': 'MED-1007', 'name': 'Metformin 500mg', 'generic': 'Metformin Hydrochloride', 'cat': 'Antidiabetic', 'mfg': 'Merck KGaA', 'batch': 'MTF-2026-G8', 'qty': 200, 'price': 12.00, 'exp': today + datetime.timedelta(days=450)},
            {'id': 'MED-1008', 'name': 'Cephalexin 250mg (Old Stock)', 'generic': 'Cephalexin', 'cat': 'Antibiotics', 'mfg': 'Cipla Ltd', 'batch': 'CPX-2024-EX', 'qty': 25, 'price': 9.50, 'exp': today - datetime.timedelta(days=45)}, # Expired
        ]

        created_medicines = {}
        for m in medicines_data:
            med_obj, _ = Medicine.objects.get_or_create(
                medicine_id=m['id'],
                defaults={
                    'name': m['name'],
                    'generic_name': m['generic'],
                    'category': cat_objects.get(m['cat']),
                    'manufacturer': m['mfg'],
                    'batch_number': m['batch'],
                    'quantity': m['qty'],
                    'unit_price': m['price'],
                    'expiry_date': m['exp'],
                    'description': f"Pharmaceutical product manufactured by {m['mfg']}."
                }
            )
            created_medicines[m['name']] = med_obj

        # 7. Create Prescriptions & Prescription Items
        rx1, _ = Prescription.objects.get_or_create(
            prescription_id='RX-2026-0001',
            defaults={
                'patient': created_patients[0],
                'patient_name': 'John Doe',
                'patient_id_number': 'PAT-001',
                'patient_age': 35,
                'patient_gender': 'Male',
                'doctor': created_doctors[0],
                'department': created_doctors[0].department,
                'prescription_date': today - datetime.timedelta(days=2),
                'diagnosis': 'Stage 1 Hypertension and elevated LDL cholesterol.',
                'notes': 'Maintain a low-sodium diet, regular aerobic exercise 30 min daily, and repeat lipid profile in 6 weeks.',
                'status': 'Active'
            }
        )
        if created_medicines.get('Atorvastatin 20mg'):
            PrescriptionItem.objects.get_or_create(prescription=rx1, medicine=created_medicines['Atorvastatin 20mg'], dosage='20 mg', frequency='0-0-1 (Night)', duration='30 Days', quantity=30, instructions='After dinner with water')
        if created_medicines.get('Metoprolol Succinate 50mg'):
            PrescriptionItem.objects.get_or_create(prescription=rx1, medicine=created_medicines['Metoprolol Succinate 50mg'], dosage='50 mg', frequency='1-0-0 (Morning)', duration='30 Days', quantity=30, instructions='Before breakfast')

        self.stdout.write(self.style.SUCCESS("All hospital management data (Specializations, Departments, Doctors, Pharmacy & Prescriptions) successfully seeded!"))
