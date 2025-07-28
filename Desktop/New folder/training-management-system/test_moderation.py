#!/usr/bin/env python
"""
Script to test the AI content moderation system functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'training_management.settings')
django.setup()

# Now import Django models and services
from moderation.services import AIContentModerator
from moderation.models import ContentModerationRule, ContentModerationReport
from courses.models import Cours  # Use real model instead of dummy

def test_content_examples():
    """Test various content examples to verify moderation works"""
    moderator = AIContentModerator()
    
    # Test cases with expected results
    test_cases = [
        {
            'content': 'Ce cours est vraiment excellent! J\'ai beaucoup appris.',
            'expected_safe': True,
            'description': 'Contenu positif approprié'
        },
        {
            'content': 'Ce cours est nul, le formateur est un con!',
            'expected_safe': False,
            'description': 'Contenu avec insulte'
        },
        {
            'content': 'Je déteste cette formation, c\'est de la merde!',
            'expected_safe': False,
            'description': 'Contenu toxique'
        },
        {
            'content': 'Mon email est test@example.com et mon numéro 0123456789',
            'expected_safe': False,
            'description': 'Informations personnelles'
        },
        {
            'content': 'ACHETEZ MAINTENANT!!! OFFRE LIMITEE!!! CLIQUEZ ICI!!!',
            'expected_safe': False,
            'description': 'Contenu spam'
        },
        {
            'content': 'Les femmes sont moins intelligentes que les hommes',
            'expected_safe': False,
            'description': 'Contenu discriminatoire'
        }
    ]
    
    print("🧪 TEST DU SYSTÈME DE MODÉRATION IA")
    print("=" * 50)
    
    # Show active rules
    active_rules = ContentModerationRule.objects.filter(active=True)
    print(f"\n📋 Règles actives: {active_rules.count()}")
    for rule in active_rules:
        auto_status = "🔴 Auto-bloquage" if rule.auto_block else "👁️ Révision manuelle"
        print(f"  - {rule.name} ({rule.get_severity_display()}) {auto_status}")
    
    print("\n" + "=" * 50)
    print("🔍 TESTS DE CONTENU")
    print("=" * 50)
    
    results = []
    
    # Get a sample course for testing
    sample_course = Cours.objects.first()
    if not sample_course:
        print("⚠️ Aucun cours trouvé. Création d'un cours test...")
        from users.models import Formateur
        formateur = Formateur.objects.first()
        if not formateur:
            print("❌ Aucun formateur trouvé. Utilisation d'un objet simple.")
            # Create a simple test object without database dependencies
            class SimpleTestObject:
                pk = 1
                _meta = type('Meta', (), {'model_name': 'test', 'app_label': 'test'})
            sample_course = SimpleTestObject()
        else:
            sample_course = Cours.objects.create(
                titre="Cours Test",
                description="Cours test pour la modération",
                contenu="Contenu de test",
                formateur=formateur,
                duree_minutes=60,
                niveau='debutant',
                categorie='Test'
            )
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Contenu: \"{test_case['content']}\"")
        
        try:
            # Moderate the content using the existing method
            is_safe, confidence, severity, issues, auto_blocked = moderator.moderate_content(
                content_object=sample_course,
                content_text=test_case['content'],
                author=None,
                content_type_label='test'
            )
            
            # Check if result matches expectation
            test_passed = is_safe == test_case['expected_safe']
            status_icon = "✅" if test_passed else "❌"
            
            print(f"Résultat: {status_icon} {'Sûr' if is_safe else 'Dangereux'}")
            print(f"Confiance IA: {confidence * 100:.1f}%")
            print(f"Sévérité: {severity}")
            print(f"Auto-bloqué: {'Oui' if auto_blocked else 'Non'}")
            
            if issues:
                print(f"Problèmes détectés: {', '.join(issues)}")
            
            results.append({
                'test': test_case['description'],
                'passed': test_passed,
                'expected': 'Sûr' if test_case['expected_safe'] else 'Dangereux',
                'actual': 'Sûr' if is_safe else 'Dangereux'
            })
            
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            results.append({
                'test': test_case['description'],
                'passed': False,
                'expected': 'Sûr' if test_case['expected_safe'] else 'Dangereux',
                'actual': f'Erreur: {e}'
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed_tests = sum(1 for r in results if r['passed'])
    total_tests = len(results)
    
    print(f"Tests réussis: {passed_tests}/{total_tests}")
    print(f"Taux de réussite: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests < total_tests:
        print("\n❌ Tests échoués:")
        for result in results:
            if not result['passed']:
                print(f"  - {result['test']}: Attendu {result['expected']}, Obtenu {result['actual']}")
    
    print("\n" + "=" * 50)
    print("🎯 VALIDATION DU SYSTÈME")
    print("=" * 50)
    
    if passed_tests >= total_tests * 0.8:  # 80% success rate
        print("✅ Le système de modération fonctionne correctement!")
        print("   L'IA détecte efficacement le contenu inapproprié.")
    else:
        print("⚠️ Le système nécessite des ajustements.")
        print("   Vérifiez les règles de modération et leurs paramètres.")
    
    # Check recent reports
    recent_reports = ContentModerationReport.objects.order_by('-created_at')[:5]
    if recent_reports:
        print(f"\n📋 Derniers rapports créés: {recent_reports.count()}")
        for report in recent_reports:
            print(f"  - {report.created_at.strftime('%H:%M:%S')}: {report.severity} ({'Bloqué' if report.auto_blocked else 'En attente'})")

if __name__ == '__main__':
    try:
        test_content_examples()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
