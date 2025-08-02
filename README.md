# School Management System

A comprehensive web-based school management system built with Django and Oracle Database, designed to streamline academic operations and enhance educational administration.

## Features

- **User Management**
  - Role-based access control (Admin, Teachers, Students)
  - Secure authentication and authorization
  - Profile management with photo upload

- **Academic Management**
  - Department and course management
  - Semester-wise course offerings
  - Course prerequisites tracking
  - Student enrollment system

- **Grade Management**
  - Assignment tracking (30% of total grade)
  - Midterm examinations (30% of total grade)
  - Final examinations (40% of total grade)
  - Automated grade calculation
  - Grade history and transcripts

- **Attendance Tracking**
  - Daily attendance recording
  - Attendance reports and statistics
  - Automated attendance percentage calculation
  - Course-wise attendance tracking

- **Reporting System**
  - Academic performance reports
  - Attendance reports
  - Grade distribution analytics
  - Semester-wise progress tracking

## Technology Stack

- **Backend**: Django 5.1.4
- **Database**: Oracle
- **Frontend**: Bootstrap 5
- **Additional Libraries**:
  - Chart.js for data visualization
  - Pillow for image processing
  - Faker for test data generation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/LimViboth/SchoolManagementSystem.git
   cd SchoolManagementSystem
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Oracle Database:
   - Create a new Oracle database
   - Update database settings in `settings.py`

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Generate test data (optional):
   ```bash
   python manage.py generate_test_data
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
SchoolManagementSystem/
├── core/                   # Core functionality and shared components
├── students/              # Student management app
├── teachers/              # Teacher management app
├── courses/              # Course and enrollment management
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
└── manage.py            # Django management script
```

## Database Schema

### Core Models
- Department
- AcademicYear
- Semester

### Student Models
- Student (Profile)
- StudentAttendance

### Teacher Models
- Teacher (Profile)
- TeacherAttendance

### Course Models
- Course
- CourseOffering
- Enrollment
- Assignment
- AssignmentSubmission

## Usage

### Student Features
1. View personal profile and academic information
2. Check current semester grades and attendance
3. View grade history and GPA trends
4. Access course materials and assignments

### Teacher Features
1. Manage course offerings
2. Record student attendance
3. Input and manage grades
4. Create and grade assignments

### Admin Features
1. Manage departments and courses
2. Handle student and teacher enrollment
3. Generate academic reports
4. Configure system settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Acknowledgments

- Django Framework team
- Oracle Database
- Bootstrap team
- All contributors and testers

