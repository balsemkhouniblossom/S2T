from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from formations.models import Formation, Salle, Planning
from users.models import Formateur, Utilisateur


class Command(BaseCommand):
    help = 'Create sample formations and planning sessions for demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create or get a formateur
        formateur, created = self.get_or_create_formateur()
        if created:
            self.stdout.write(f'Created formateur: {formateur}')
        else:
            self.stdout.write(f'Using existing formateur: {formateur}')
        
        # Create formations if they don't exist
        formations_created = self.create_formations(formateur)
        
        # Create planning sessions for each formation
        for formation in formations_created:
            sessions_created = self.create_planning_sessions(formation)
            self.stdout.write(f'Created {sessions_created} sessions for {formation.titre}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(formations_created)} formations with planning sessions!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'You can now access the Django admin at: http://127.0.0.1:8000/admin/formations/planning/'
            )
        )

    def get_or_create_formateur(self):
        formateur = Formateur.objects.first()
        if formateur:
            return formateur, False
        
        # Create a new formateur
        user = Utilisateur.objects.create_user(
            email='formateur.demo@formation.com',
            password='demo123',
            nom='Demo',
            prenom='Formateur',
            telephone='0123456789'
        )
        
        formateur = Formateur.objects.create(
            utilisateur=user,
            specialites='Python, Django, Web Development',
            experience_annees=5,
            cv='Formateur expérimenté en développement web'
        )
        
        return formateur, True

    def create_formations(self, formateur):
        if Formation.objects.exists():
            return list(Formation.objects.all())
        
        formations_data = [
            {
                'titre': 'Python pour Débutants',
                'description': 'Formation complète pour apprendre Python depuis les bases',
                'objectifs': 'Maîtriser les fondamentaux de Python et créer des programmes simples',
                'duree_heures': 30,
                'niveau': 'debutant',
                'prix': 450.00,
                'participants_max': 15,
                'prerequisites': 'Aucun prérequis nécessaire',
                'statut': 'publiee',
            },
            {
                'titre': 'Django Framework Avancé',
                'description': 'Développement web professionnel avec Django',
                'objectifs': 'Créer des applications web robustes et sécurisées',
                'duree_heures': 45,
                'niveau': 'intermediaire',
                'prix': 750.00,
                'participants_max': 12,
                'prerequisites': 'Connaissance de Python requise',
                'statut': 'publiee',
            },
            {
                'titre': 'Data Science & Machine Learning',
                'description': 'Analyse de données et apprentissage automatique avec Python',
                'objectifs': 'Maîtriser les outils de data science et créer des modèles ML',
                'duree_heures': 60,
                'niveau': 'avance',
                'prix': 1200.00,
                'participants_max': 10,
                'prerequisites': 'Python intermédiaire, bases statistiques',
                'statut': 'brouillon',
            }
        ]
        
        formations = []
        base_date = timezone.now() + timedelta(days=7)
        
        for i, data in enumerate(formations_data):
            formation = Formation.objects.create(
                formateur=formateur,
                date_debut=base_date + timedelta(days=i*14),
                date_fin=base_date + timedelta(days=i*14 + 21),
                **data
            )
            formations.append(formation)
            self.stdout.write(f'Created formation: {formation.titre}')
        
        return formations

    def create_planning_sessions(self, formation):
        # Get or create training rooms
        salles = self.get_or_create_salles()
        
        # Session templates based on formation level
        session_templates = {
            'debutant': [
                {'sujet': 'Introduction et environnement', 'description': 'Installation et premier programme'},
                {'sujet': 'Variables et types de données', 'description': 'Manipulation des données de base'},
                {'sujet': 'Structures de contrôle', 'description': 'Conditions et boucles'},
                {'sujet': 'Fonctions et modules', 'description': 'Organisation du code'},
                {'sujet': 'Gestion des erreurs', 'description': 'Try/except et debugging'},
                {'sujet': 'Projet final', 'description': 'Application des concepts appris'},
            ],
            'intermediaire': [
                {'sujet': 'Architecture Django', 'description': 'MVC/MVT et structure des projets'},
                {'sujet': 'Modèles et ORM', 'description': 'Base de données et relations'},
                {'sujet': 'Vues et Templates', 'description': 'Logique métier et présentation'},
                {'sujet': 'Formulaires et validation', 'description': 'Saisie et validation de données'},
                {'sujet': 'Authentification et sécurité', 'description': 'Gestion des utilisateurs'},
                {'sujet': 'APIs REST', 'description': 'Django REST Framework'},
                {'sujet': 'Déploiement', 'description': 'Mise en production'},
            ],
            'avance': [
                {'sujet': 'Exploration des données', 'description': 'Pandas et analyse exploratoire'},
                {'sujet': 'Visualisation', 'description': 'Matplotlib, Seaborn et graphiques'},
                {'sujet': 'Preprocessing', 'description': 'Nettoyage et préparation des données'},
                {'sujet': 'Machine Learning supervisé', 'description': 'Classification et régression'},
                {'sujet': 'Machine Learning non-supervisé', 'description': 'Clustering et réduction de dimension'},
                {'sujet': 'Deep Learning', 'description': 'Réseaux de neurones avec TensorFlow'},
                {'sujet': 'Projet ML complet', 'description': 'De la donnée au modèle en production'},
            ]
        }
        
        sessions = session_templates.get(formation.niveau, session_templates['debutant'])
        
        created_count = 0
        start_date = formation.date_debut
        
        for i, session_data in enumerate(sessions):
            # Schedule sessions every 2-3 days
            session_date = start_date + timedelta(days=i*3, hours=9)  # 9 AM
            
            # Vary session duration based on content
            if 'projet' in session_data['sujet'].lower():
                duration = 240  # 4 hours for projects
            elif 'introduction' in session_data['sujet'].lower():
                duration = 120  # 2 hours for intro
            else:
                duration = 180  # 3 hours standard
            
            planning = Planning.objects.create(
                formation=formation,
                salle=salles[i % len(salles)],  # Rotate through available rooms
                date_session=session_date,
                duree_session=duration,
                sujet=session_data['sujet'],
                description=session_data['description'],
                code_presence=f'{formation.niveau.upper()[:3]}{formation.id:02d}{i+1:02d}'
            )
            created_count += 1
        
        return created_count

    def get_or_create_salles(self):
        if Salle.objects.exists():
            return list(Salle.objects.all())
        
        salles_data = [
            {
                'nom': 'Salle Python Lab',
                'capacite': 20,
                'localisation': 'Bâtiment A - 1er étage',
                'equipements': 'Ordinateurs, Python préinstallé, Projecteur 4K'
            },
            {
                'nom': 'Salle Web Dev',
                'capacite': 15,
                'localisation': 'Bâtiment A - 2e étage',
                'equipements': 'Stations de développement, Serveurs de test'
            },
            {
                'nom': 'Salle Data Science',
                'capacite': 12,
                'localisation': 'Bâtiment B - RDC',
                'equipements': 'Workstations GPU, Datasets, Tableau interactif'
            },
            {
                'nom': 'Salle Conférence',
                'capacite': 30,
                'localisation': 'Bâtiment Central',
                'equipements': 'Amphithéâtre, Système audio/vidéo professionnel'
            }
        ]
        
        salles = []
        for salle_data in salles_data:
            salle = Salle.objects.create(**salle_data)
            salles.append(salle)
            self.stdout.write(f'Created room: {salle.nom}')
        
        return salles
