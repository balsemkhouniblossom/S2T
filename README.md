# Training Management System

A comprehensive Django-based training management system with PostgreSQL integration, featuring user management, formation/course management, messaging, and payment processing.

## 🚀 Features

### 👥 User Management
- **Utilisateur**: Base user model with email authentication
- **Formateur**: Trainers who create and manage formations/courses  
- **Apprenant**: Learners who enroll in formations and courses
- **Administrateur**: System administrators with full management access
- Profile management with photos and CV uploads
- Notification system for all users

### 📚 Formation Management
- Create and manage training formations
- Room scheduling and planning
- Participant enrollment and tracking
- Attendance marking with presence codes
- Formation evaluations and feedback
- Automatic certificate generation

### 📖 Course Management  
- Individual course creation and publishing
- Resource management (files, videos, documents)
- Progress tracking for learners
- Course ratings and comments system
- Multi-level course difficulty

### 💬 Messaging System
- Private messaging between users
- Group chat functionality for formations
- Discussion threads and forums
- File attachments in messages
- Real-time communication features

### 💳 Payment System
- Individual and organization payments
- Invoice generation and management
- Discount codes and promotional offers
- Corporate sponsorship tracking
- Multiple payment methods support

## 🛠️ Technical Stack

- **Backend**: Django 4.2.7 with Python 3.12

### Prerequisites
# Dependencies are already installed in this project
# If you need to reinstall:
#### For Development (SQLite - Already configured)
```bash
1. Install PostgreSQL and create database:
   ```sql
   # Uncomment the PostgreSQL configuration
   # Comment out the SQLite configuration
   ```
   ```

### 3. Run the Application
```bash
## 🌐 Access Points

- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
  - Username: admin
  - Email: admin@training.com
  - Password: [your-password]

### 🏠 Homepage Navigation

From the homepage (`http://localhost:8000/`), users can access:

#### 📋 Public Access (All Visitors)
- **🎓 Training System Logo** → Returns to homepage
- **📚 Formations** → `/formations/` - Browse available training formations
- **📖 Cours** → `/courses/` - Browse individual courses
- **🔧 Accéder à l'Administration** → `/admin/` - Admin panel access
- **Connexion** → `/auth/login/` - User login page
- **Inscription** → `/auth/register/` - User registration page

#### 🔐 Authenticated User Access
Once logged in, additional navigation options appear:
- **💬 Messages** → `/messaging/inbox/` - Personal messaging system
- **📊 Dashboard** → `/users/dashboard/` - Role-based dashboard
- **Profil** → `/users/profile/` - User profile management
- **Déconnexion** → Logout functionality

#### 🎯 Quick Access URLs
- **Formations List**: http://localhost:8000/formations/
- **Courses List**: http://localhost:8000/courses/
- **Login**: http://localhost:8000/auth/login/
- **Register**: http://localhost:8000/auth/register/
- **Dashboard**: http://localhost:8000/dashboard/ (authenticated users)
- **Messages**: http://localhost:8000/messaging/inbox/ (authenticated users)

## 📁 Project Structure

```
training-management-system/
├── manage.py
├── requirements.txt
│   ├── models.py                 # User models (Utilisateur, Formateur, etc.)
│   ├── admin.py                  # Admin configurations
│   └── migrations/               # Database migrations
├── formations/                   # Formation management app
│   ├── models.py                 # Formation, Planning, Salle models
│   ├── admin.py                  # Admin configurations
│   └── migrations/
├── courses/                      # Course management app
│   ├── models.py                 # Cours, RessourceCours models
├── payments/                     # Payment processing app
│   ├── models.py                 # Paiement, Facture models
│   ├── admin.py                  # Admin configurations
    └── wsgi.py                   # WSGI application
```
- `Apprenant`: Learner profiles with company information
- `Administrateur`: Admin users with access levels

## 📁 Project Structure & Layout

```
training-management-system/
├── manage.py
├── requirements.txt
├── db.sqlite3                  python manage.py makemigrations users
python manage.py migrate  # Development database (SQLite)
├── users/                        # User management app
│   ├── models.py                 # User models (Utilisateur, Formateur, Apprenant, Admin)
│   ├── admin.py                  # Admin configurations
│   ├── forms.py                  # User forms
│   ├── views.py                  # User views
│   └── migrations/               # Database migrations
├── formations/                   # Formation management app
│   ├── models.py                 # Formation, Planning, Salle, Inscription, TrainerApplication
│   ├── admin.py                  # Admin configurations
│   ├── forms.py                  # Formation forms
│   ├── views.py                  # Formation views
│   ├── urls.py                   # Formation URLs
│   └── migrations/
├── courses/                      # Course management app
│   ├── models.py                 # Cours, RessourceCours, ProgressionCours
│   ├── admin.py                  # Admin configurations
│   ├── forms.py                  # Course forms
│   ├── views.py                  # Course views
│   └── migrations/
├── messaging/                    # Communication system app
│   ├── models.py                 # Message, GroupeChat, FilDiscussion, etc.
│   ├── admin.py                  # Admin configurations
│   └── migrations/
├── payments/                     # Payment processing app
│   ├── models.py                 # Organisation, Paiement, Facture, etc.
│   ├── admin.py                  # Admin configurations
│   └── migrations/
├── templates/                    # All HTML templates (UI)
│   ├── base.html                 # Main layout, navbar, footer, CSS
│   ├── home.html                 # Homepage
│   ├── formations/               # Formation-related templates
│   ├── courses/                  # Course-related templates
│   ├── users/                    # User-related templates
│   └── ...
├── static/                       # Static files (CSS, JS, images)
│   └── ...
├── media/                        # Uploaded files (profile images, CVs, resources, etc.)
└── training_management/          # Main Django settings
    ├── settings.py               # Django configuration
    ├── urls.py                   # URL routing
    └── wsgi.py                   # WSGI application
```

### �️ UI/UX & Design System

- **Modern, responsive design** using Google Fonts (Inter), gradients, and card-based layouts
- **Sticky navbar** with quick access to all main features
- **Consistent button and alert styles** for actions and feedback
- **Mobile-friendly**: All templates are responsive and adapt to all screen sizes
- **Visual cues**: Badges, icons (FontAwesome), and color codes for status (e.g., candidatures ouvertes/fermées)
- **Enhanced forms**: Grouped fields, clear labels, and validation feedback
- **User avatars** and profile images in navigation
- **Section separation**: Cards and spacing for clarity

## 🏗️ Main Django Models (Class Highlights)

### Users App
- `Utilisateur`: Custom user model (email login, name, photo, etc.)
- `Formateur`: Trainer profile (CV, competences, experience, tarif, disponible)
- `Apprenant`: Learner profile (company, objectives, organisation)
- `Administrateur`: Admin profile (access level, department)
## 🔧 Configuration
### Formations App
- `Formation`: Training formation (title, description, objectives, duration, level, price, formateur, participants, candidatures ouvertes, etc.)
- `Salle`: Training room (name, capacity, location, equipment)
- `Inscription`: Enrollment (apprenant, formation, status, dates)
- `TrainerApplication`: Application to become a trainer for a formation (motivation, experience, tarif, disponibilite, message)

### Courses App
- `Cours`: Individual course (title, description, content, formateur, duration, level, category, price, etc.)
- `RessourceCours`: Course resource (type, file/link, description, order)
- `ProgressionCours`: Learning progress (apprenant, cours, date)
### Media Files
### Messaging App
- `Message`: Private message (sender, recipient, subject, content, file, read status)
- `GroupeChat`: Group chat (name, description, members, formation, private)
- `MessageGroupe`: Group message (group, author, content, file, date)
- `FilDiscussion`: Discussion thread (formation, author, title, content, pinned, closed)
Uploaded files are stored in:
### Payments App
- `Organisation`: Company/sponsor (name, sector, contact, VAT, etc.)
- `Paiement`: Payment transaction (formation, apprenant/organisation, amount, date, status)
- `Facture`: Invoice (payment, file, date)

## 🎨 UI/UX Features & Customization

- **Base template (`base.html`)**: Centralizes all layout, navigation, and design. Uses Google Fonts, gradients, and card-based sections.
- **Sticky, shadowed navbar**: Always visible, with quick links and user avatar/profile.
- **Consistent button styles**: Primary, secondary, success, danger, and outline variants with hover effects.
- **Alerts and badges**: For candidatures, status, and user feedback.
- **Responsive cards**: Used for all main content blocks (formations, courses, messages, etc.).
- **Enhanced forms**: Grouped fields, clear error messages, and help texts.
- **Mobile-first**: All layouts adapt to mobile and tablet screens.
- **Easy customization**: Update `base.html` and static CSS for branding or color changes.

## 📝 Notable Features & Workflows

- **Trainer Application Workflow**: Trainers can apply to lead a formation via a dedicated form (motivation, experience, tarif, disponibilite, message). Status (candidatures ouvertes/fermées) is visible on both the formation detail and application pages.
- **Role-based navigation**: Menu adapts to user type (apprenant, formateur, admin).
- **Admin interface**: All models are fully manageable via Django admin, with inline editing, filters, and search.
- **Messaging**: Private and group chat, file attachments, and discussion threads.
- **Payments**: Individual and organization payments, invoices, and sponsorships.
- **Notifications**: System notifications for all users.
- **Attendance & Certificates**: Presence codes and automatic certificate generation.

## �️ How to Customize the UI

1. **Edit `templates/base.html`** for layout, navbar, and global styles.
2. **Update static CSS** (or add your own in `static/`) for colors, spacing, and branding.
3. **Use FontAwesome or Bootstrap Icons** for more visual cues.
4. **Modify templates in `templates/`** for each app to change page layouts or add new UI elements.
5. **All forms and cards** use consistent classes—customize them for your brand.

## 📸 Example UI Elements

- **Navbar**: Sticky, gradient background, user avatar, and quick links
- **Cards**: White, rounded, shadowed blocks for all main content
- **Buttons**: Modern, colored, with hover/active effects
- **Alerts/Badges**: Color-coded for status (success, danger, info)
- **Forms**: Grouped, with clear labels and validation

## 🚀 Next Steps

1. **Frontend Development**: Continue refining templates and UI components
2. **API Endpoints**: Implement REST API using Django REST Framework  
3. **Real-time Features**: Add WebSocket support for messaging
4. **Payment Integration**: Connect with payment gateways
5. **Email Notifications**: Configure email settings
6. **File Processing**: Add video/document processing
7. **Reporting**: Generate analytics and reports
```
media/
├── profiles/          # User profile images
├── cvs/              # Trainer CVs
├── cours/            # Course materials
├── messages/         # Message attachments
├── groupes/          # Group chat files
├── discussions/      # Forum attachments
├── attestations/     # Generated certificates
└── factures/         # Invoice PDFs
```

### Admin Interface
All models are fully configured in the Django admin with:
- List views with filtering and search
- Inline editing for related objects
- Custom admin actions
- Proper field organization

## 🚀 Next Steps

1. **Frontend Development**: Create custom templates and views
2. **API Endpoints**: Implement REST API using Django REST Framework  
3. **Real-time Features**: Add WebSocket support for messaging
4. **Payment Integration**: Connect with payment gateways
5. **Email Notifications**: Configure email settings
6. **File Processing**: Add video/document processing
7. **Reporting**: Generate analytics and reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions, please contact the development team.

---

**Project Status**: ✅ Database models complete, ✅ Admin interface ready, 🔄 Frontend in development
