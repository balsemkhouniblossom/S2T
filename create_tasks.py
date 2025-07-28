from formations.models import Task
from users.models import Utilisateur
from formations.models import Formation
from datetime import datetime, timedelta

try:
    # Get users
    users = Utilisateur.objects.all()
    if users.count() >= 2:
        formateur_user = users[1]  # Second user as formateur
        apprenant_user = users[2] if users.count() > 2 else users[0]  # Third user or first as apprenant
    else:
        print("Not enough users in database")
        exit()
    
    formation = Formation.objects.first()
    
    # Create tasks for formateur if they don't exist
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
        print(f"Created formateur task 1 for {formateur_user.email}")
        
        Task.objects.create(
            createur=formateur_user,
            titre="Réviser les notes de cours",
            description="Relire et corriger les notes du dernier cours",
            priorite='moyenne',
            statut='a_faire',
            categorie='administration',
            date_echeance=datetime.now().date() + timedelta(days=7)
        )
        print(f"Created formateur task 2 for {formateur_user.email}")
    
    # Create tasks for apprenant if they don't exist  
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
        print(f"Created apprenant task 1 for {apprenant_user.email}")
        
        Task.objects.create(
            createur=apprenant_user,
            titre="Étudier pour l'examen",
            description="Réviser les chapitres 1-5 du cours Python",
            priorite='moyenne',
            statut='a_faire',
            categorie='etude',
            date_echeance=datetime.now().date() + timedelta(days=10)
        )
        print(f"Created apprenant task 2 for {apprenant_user.email}")
    
    print(f"Total tasks in database: {Task.objects.count()}")
    
except Exception as e:
    print(f"Error: {e}")
