from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from students.models import Student, StudentAttendance
from teachers.models import Teacher
from core.models import Department, AcademicYear, Semester
from courses.models import Course, CourseOffering, Enrollment
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Generate test data for the school management system'

    def create_departments(self):
        departments = [
            ('Computer Science', 'CS'),
            ('Electrical Engineering', 'EE'),
            ('Business Administration', 'BA'),
            ('Mathematics', 'MATH'),
            ('Physics', 'PHY')
        ]
        
        created_departments = []
        for name, code in departments:
            dept, _ = Department.objects.get_or_create(
                name=name,
                code=code
            )
            created_departments.append(dept)
        return created_departments

    def create_academic_years(self):
        current_year = timezone.now().year
        years = []
        for year in range(current_year - 2, current_year + 2):
            year_str = f"{year}-{year + 1}"
            start_date = datetime(year, 9, 1)  # Academic year starts in September
            end_date = datetime(year + 1, 8, 31)  # Ends in August next year
            
            academic_year, _ = AcademicYear.objects.get_or_create(
                year=year_str,
                defaults={
                    'is_current': year == current_year,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            years.append(academic_year)
        return years

    def create_semesters(self, academic_years):
        semesters = []
        current_month = timezone.now().month

        for academic_year in academic_years:
            year = int(academic_year.year.split('-')[0])
            
            # Fall semester (Sep-Dec)
            fall, _ = Semester.objects.get_or_create(
                academic_year=academic_year,
                name='FALL',
                defaults={
                    'start_date': datetime(year, 9, 1),
                    'end_date': datetime(year, 12, 31),
                    'is_current': academic_year.is_current and 9 <= current_month <= 12
                }
            )
            semesters.append(fall)

            # Spring semester (Jan-May)
            spring, _ = Semester.objects.get_or_create(
                academic_year=academic_year,
                name='SPRING',
                defaults={
                    'start_date': datetime(year + 1, 1, 15),
                    'end_date': datetime(year + 1, 5, 31),
                    'is_current': academic_year.is_current and 1 <= current_month <= 5
                }
            )
            semesters.append(spring)

            # Summer semester (Jun-Aug)
            summer, _ = Semester.objects.get_or_create(
                academic_year=academic_year,
                name='SUMMER',
                defaults={
                    'start_date': datetime(year + 1, 6, 1),
                    'end_date': datetime(year + 1, 8, 15),
                    'is_current': academic_year.is_current and 6 <= current_month <= 8
                }
            )
            semesters.append(summer)

        return semesters

    def create_courses(self, departments):
        courses_data = {
            'CS': [
                ('CS101', 'Introduction to Programming', 3, 'Learn the basics of programming using Python'),
                ('CS201', 'Data Structures', 3, 'Study fundamental data structures and algorithms'),
                ('CS301', 'Database Systems', 3, 'Introduction to database design and SQL'),
                ('CS401', 'Software Engineering', 4, 'Software development methodologies and project management')
            ],
            'EE': [
                ('EE101', 'Circuit Analysis', 3, 'Basic concepts of electrical circuits'),
                ('EE201', 'Digital Electronics', 3, 'Digital logic design and Boolean algebra'),
                ('EE301', 'Signals and Systems', 3, 'Analysis of continuous and discrete-time signals')
            ],
            'BA': [
                ('BA101', 'Business Fundamentals', 3, 'Introduction to business concepts and practices'),
                ('BA201', 'Marketing Management', 3, 'Marketing strategies and consumer behavior'),
                ('BA301', 'Financial Accounting', 3, 'Principles of accounting and financial reporting')
            ]
        }

        created_courses = []
        for dept in departments:
            if dept.code in courses_data:
                for code, name, credits, description in courses_data[dept.code]:
                    course, _ = Course.objects.get_or_create(
                        code=code,
                        defaults={
                            'name': name,
                            'department': dept,
                            'credits': credits,
                            'description': description
                        }
                    )
                    created_courses.append(course)
        return created_courses

    def create_students(self, departments):
        students = []
        current_year = AcademicYear.objects.filter(is_current=True).first()
        graduation_year = AcademicYear.objects.filter(year__startswith=str(timezone.now().year + 4)).first()
        
        # Get last student ID
        last_student = Student.objects.order_by('-student_id').first()
        if last_student:
            last_id = int(last_student.student_id[3:])
        else:
            last_id = 0
            
        for i in range(50):  # Create 50 students
            student_id = f'STU{last_id + i + 1:06d}'  # e.g., STU000001
            
            while Student.objects.filter(student_id=student_id).exists():
                last_id += 1
                student_id = f'STU{last_id + i + 1:06d}'

            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'{first_name.lower()}.{last_name.lower()}'
            
            # Ensure unique username
            username_count = 1
            base_username = username
            while User.objects.filter(username=username).exists():
                username = f'{base_username}{username_count}'
                username_count += 1
            
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=f'{username}@example.com'
            )

            student = Student.objects.create(
                user=user,
                student_id=student_id,
                department=random.choice(departments),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
                address=fake.address(),
                phone=fake.phone_number()[:15],
                admission_year=current_year,
                graduation_year=graduation_year,
                is_active=True
            )
            students.append(student)
        return students

    def create_attendance(self, students, current_semester):
        # Get course offerings for the current semester
        course_offerings = CourseOffering.objects.filter(semester=current_semester)
        
        # Generate attendance for the last 90 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                for student in students:
                    enrolled_offerings = Enrollment.objects.filter(
                        student=student,
                        course_offering__in=course_offerings,
                        withdrawn=False
                    ).select_related('course_offering')

                    for enrollment in enrolled_offerings:
                        # 85% chance of being present, 10% absent, 5% late
                        rand = random.random()
                        if rand < 0.85:
                            is_present = True
                            note = ''
                        else:
                            is_present = False
                            note = 'Excused absence'

                        StudentAttendance.objects.get_or_create(
                            student=student,
                            date=current_date,
                            defaults={
                                'is_present': is_present,
                                'note': note
                            }
                        )
            current_date += timedelta(days=1)

    def create_enrollments(self, students, courses, semesters):
        grades = ['A', 'B', 'C', 'D', 'F', 'W', 'I']
        weights = [0.15, 0.3, 0.3, 0.1, 0.05, 0.05, 0.05]  # Distribution of grades
        active_offerings = []
        for semester in semesters:
            for course in courses:
                # Create a unique teacher for each course
                first_name = fake.first_name()
                last_name = fake.last_name()
                username = f'teacher_{course.code.lower()}'
                email = f'{username}@example.com'
                teacher, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
                    }
                )
                teacher_id = f'TCH{course.code}'
                teacher_profile, _ = Teacher.objects.get_or_create(
                    user=teacher,
                    defaults={
                        'teacher_id': teacher_id,
                        'phone': fake.phone_number()[:15],
                        'address': fake.address(),
                        'department': course.department,
                        'date_of_birth': fake.date_of_birth(minimum_age=30, maximum_age=60),
                        'qualification': random.choice(['Ph.D.', 'Master', 'Bachelor']),
                        'joining_date': timezone.now().date() - timedelta(days=random.randint(365, 3650))
                    }
                )
                # Ensure at least 5 active offerings with positive max_students
                is_active = True if len(active_offerings) < 5 else random.choice([True, False])
                max_students = random.randint(10, 50)
                offering, _ = CourseOffering.objects.get_or_create(
                    course=course,
                    semester=semester,
                    teacher=teacher_profile,
                    defaults={
                        'max_students': max_students,
                        'is_active': is_active
                    }
                )
                if is_active:
                    active_offerings.append(offering)
                # Enroll random students
                for student in random.sample(students, k=random.randint(15, 30)):
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        course_offering=offering,
                        defaults={
                            'withdrawn': False,
                            'enrollment_date': timezone.now()
                        }
                    )
                    # Only add grades for past semesters
                    if semester.end_date < timezone.now().date():
                        is_withdrawn = random.random() < 0.05  # 5% chance of withdrawal
                        if is_withdrawn:
                            enrollment.withdrawn = True
                            enrollment.withdrawal_date = semester.end_date - timedelta(days=random.randint(1, 30))
                            enrollment.grade = 'W'
                        else:
                            # Generate assignment scores (30% of total grade)
                            assignment_score = max(0, random.uniform(15, 30))  # Out of 30, non-negative
                            # Generate midterm score (30% of total grade)
                            midterm_score = max(0, random.uniform(15, 30))  # Out of 30, non-negative
                            # Generate final score (40% of total grade)
                            final_score = max(0, random.uniform(20, 40))  # Out of 40, non-negative
                            # Calculate total score
                            total_score = assignment_score + midterm_score + final_score
                            # Assign letter grade based on total score
                            if total_score >= 90:
                                letter_grade = 'A'
                            elif total_score >= 80:
                                letter_grade = 'B'
                            elif total_score >= 70:
                                letter_grade = 'C'
                            elif total_score >= 60:
                                letter_grade = 'D'
                            else:
                                letter_grade = 'F'
                            enrollment.assignment_score = assignment_score
                            enrollment.midterm_score = midterm_score
                            enrollment.final_score = final_score
                            enrollment.grade = letter_grade
                        enrollment.save()

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating departments...')
        departments = self.create_departments()

        self.stdout.write('Creating academic years...')
        academic_years = self.create_academic_years()

        self.stdout.write('Creating semesters...')
        semesters = self.create_semesters(academic_years)

        self.stdout.write('Creating courses...')
        courses = self.create_courses(departments)

        self.stdout.write('Creating students...')
        students = self.create_students(departments)

        self.stdout.write('Creating enrollments...')
        self.create_enrollments(students, courses, semesters)

        current_semester = Semester.objects.filter(is_current=True).first()
        if current_semester:
            self.stdout.write('Creating attendance records...')
            self.create_attendance(students, current_semester)

        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))
