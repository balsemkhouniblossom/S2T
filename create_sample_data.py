"""
Sample data creation script for Training Management System
Run with: python manage.py shell -c "exec(open('create_sample_data.py').read())"
"""

from django.contrib.auth import get_user_model
from users.models import Formateur, Apprenant, Administrateur
from formations.models import Formation, Salle, Task
from courses.models import Cours
from messaging.models import Message
from datetime import datetime, timedelta

User = get_user_model()

# Create sample users
print("Creating sample users...")

# Create admin user (if not exists)
if not User.objects.filter(email='admin@example.com').exists():
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        nom='Dupont',
        prenom='Jean',
        password='admin123'
    )
    admin_user.user_type = 'administrateur'
    admin_user.save()
    admin_profile = Administrateur.objects.create(
        utilisateur=admin_user,
        niveau_acces='complet'
    )
    print("Admin user created: admin@example.com")

# Create formateur
if not User.objects.filter(email='formateur@example.com').exists():
    formateur_user = User.objects.create_user(
        username='formateur',
        email='formateur@example.com',
        nom='Martin',
        prenom='Sophie',
        password='formateur123'
    )
    formateur_user.user_type = 'formateur'
    formateur_user.save()
    formateur_profile = Formateur.objects.create(
        utilisateur=formateur_user,
        competences='Django, Python, React, HTML, CSS',
        experience=5,
        description='Developpeuse web experimentee specialisee en Django et React.',
        tarif_horaire=50.00
    )
    print("Formateur created: formateur@example.com")

# Create apprenant
if not User.objects.filter(email='apprenant@example.com').exists():
    apprenant_user = User.objects.create_user(
        username='apprenant',
        email='apprenant@example.com',
        nom='Durand',
        prenom='Pierre',
        password='apprenant123'
    )
    apprenant_user.user_type = 'apprenant'
    apprenant_user.save()
    apprenant_profile = Apprenant.objects.create(
        utilisateur=apprenant_user,
        entreprise='TechCorp',
        niveau_etude='master'
    )
    print("Apprenant created: apprenant@example.com")

# Create sample room
if not Salle.objects.filter(nom='Salle A1').exists():
    salle = Salle.objects.create(
        nom='Salle A1',
        capacite=25,
        equipements='Projecteur, Ordinateurs, Tableau interactif',
        localisation='Batiment A, 1er etage'
    )
    print("Sample room created")

# Create sample formation
if not Formation.objects.filter(titre='Introduction a Django').exists():
    try:
        formateur = Formateur.objects.get(utilisateur__email='formateur@example.com')
        formation = Formation.objects.create(
            titre='Introduction a Django',
            description='Apprenez les bases du framework Django pour developper des applications web robustes.',
            formateur=formateur,
            date_debut='2025-08-01 09:00:00',
            date_fin='2025-08-05 17:00:00',
            duree_heures=35,
            prix=299.99,
            niveau='debutant',
            prerequis='Connaissances de base en Python',
            statut='publiee'
        )
        print("Sample formation created")
    except Exception as e:
        print(f"Error creating formation: {e}")

# Create sample course
if not Cours.objects.filter(titre='HTML & CSS Basics').exists():
    try:
        formateur = Formateur.objects.get(utilisateur__email='formateur@example.com')
        cours = Cours.objects.create(
            titre='HTML & CSS Basics',
            description='Maitrisez les fondamentaux du developpement web avec HTML et CSS.',
            formateur=formateur,
            contenu='Ce cours couvre les bases du HTML et CSS...',
            duree_minutes=120,
            niveau='debutant',
            categorie='Web Development',
            mots_cles='html, css, web, frontend',
            publie=True
        )
        print("Sample course created")
    except Exception as e:
        print(f"Error creating course: {e}")

# Create sample tasks
print("Creating sample tasks...")

try:
    formateur_user = User.objects.get(email='formateur@example.com')
    apprenant_user = User.objects.get(email='apprenant@example.com')
    formation = Formation.objects.first()
    
    # Tasks for formateur
    if not Task.objects.filter(createur=formateur_user).exists():
        Task.objects.create(
            createur=formateur_user,
            titre="Préparer le cours sur Django",
            description="Mettre à jour le contenu du cours et préparer les exercices pratiques",
            priorite='haute',
            statut='en_cours',
            categorie='formation',
            date_echeance=datetime.now().date() + timedelta(days=3),
            formation_liee=formation
        )
        
        Task.objects.create(
            createur=formateur_user,
            titre="Réviser les notes de cours",
            description="Relire et corriger les notes du dernier cours",
            priorite='moyenne',
            statut='a_faire',
            categorie='administration',
            date_echeance=datetime.now().date() + timedelta(days=7)
        )
        
        Task.objects.create(
            createur=formateur_user,
            titre="Évaluer les projets étudiants",
            description="Corriger et noter les projets soumis par les apprenants",
            priorite='haute',
            statut='terminee',
            categorie='evaluation',
            date_completion=datetime.now().date() - timedelta(days=1)
        )
    
    # Tasks for apprenant
    if not Task.objects.filter(createur=apprenant_user).exists():
        Task.objects.create(
            createur=apprenant_user,
            titre="Terminer le projet Django",
            description="Finaliser l'application web et la tester",
            priorite='haute',
            statut='en_cours',
            categorie='projet',
            date_echeance=datetime.now().date() + timedelta(days=5),
            formation_liee=formation
        )
        
        Task.objects.create(
            createur=apprenant_user,
            titre="Étudier pour l'examen",
            description="Réviser les chapitres 1-5 du cours Python",
            priorite='moyenne',
            statut='a_faire',
            categorie='etude',
            date_echeance=datetime.now().date() + timedelta(days=10)
        )
        
        Task.objects.create(
            createur=apprenant_user,
            titre="Lire la documentation React",
            description="Comprendre les concepts de base de React",
            priorite='basse',
            statut='a_faire',
            categorie='etude',
            date_echeance=datetime.now().date() + timedelta(days=14)
        )
    
    print("Sample tasks created successfully")
    
except Exception as e:
    print(f"Error creating sample tasks: {e}")


# === DASHBOARD FEATURE DATA ===
from courses.models import ProgressionCours, Quiz, QuizResult, Certification, CertificationProgress, LearningGoal, RessourceCours
from django.utils import timezone

try:
    apprenant_user = User.objects.get(email='apprenant@example.com')
    # Use the first two courses for dashboard data
    cours1 = Cours.objects.first()
    cours2 = Cours.objects.last()

    # Create resources for each course
    res1 = RessourceCours.objects.create(titre='Intro', cours=cours1)
    res2 = RessourceCours.objects.create(titre='Avancé', cours=cours1)
    res3 = RessourceCours.objects.create(titre='Déploiement', cours=cours2)

    # Progressions
    prog1 = ProgressionCours.objects.create(apprenant=apprenant_user, cours=cours1, progression_pourcentage=50, temps_passe_minutes=60)
    prog1.ressources_completees.set([res1])
    prog2 = ProgressionCours.objects.create(apprenant=apprenant_user, cours=cours2, progression_pourcentage=33, temps_passe_minutes=40)
    prog2.ressources_completees.set([res3])

    # Quizzes
    quiz1 = Quiz.objects.create(titre='Quiz 1', cours=cours1)
    quiz2 = Quiz.objects.create(titre='Quiz 2', cours=cours2)

    # Quiz Results
    QuizResult.objects.create(quiz=quiz1, apprenant=apprenant_user, score=8, total=10, passed=True)
    QuizResult.objects.create(quiz=quiz2, apprenant=apprenant_user, score=4, total=10, passed=False)

    # Certifications
    cert1 = Certification.objects.create(titre='Certif 1', cours=cours1, description='Certification 1')
    cert2 = Certification.objects.create(titre='Certif 2', cours=cours2, description='Certification 2')

    # Certification Progress
    CertificationProgress.objects.create(apprenant=apprenant_user, certification=cert1, completed=True)
    CertificationProgress.objects.create(apprenant=apprenant_user, certification=cert2, completed=False)

    # Learning Goals
    LearningGoal.objects.create(apprenant=apprenant_user, objectif_lecons=5, lecons_terminees=3, periode='Hebdomadaire', date_debut=timezone.now().date(), date_fin=timezone.now().date() + timezone.timedelta(days=7), atteint=False)
    LearningGoal.objects.create(apprenant=apprenant_user, objectif_lecons=10, lecons_terminees=10, periode='Mensuel', date_debut=timezone.now().date().replace(day=1), date_fin=timezone.now().date(), atteint=True)

    print("Dashboard sample data created!")
except Exception as e:
    print(f"Error creating dashboard sample data: {e}")

print("\nSample data creation completed!")
print("\nTest accounts:")
print("Admin: admin@example.com / admin123")
print("Formateur: formateur@example.com / formateur123") 
print("Apprenant: apprenant@example.com / apprenant123")
