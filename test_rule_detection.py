#!/usr/bin/env python
"""
Simple test script to verify AI moderation rules work correctly
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

from moderation.models import ContentModerationRule
from moderation.services import AIContentModerator
import re

def test_rule_detection():
    """Test individual rule detection logic"""
    
    print("🧪 TEST DES RÈGLES DE MODÉRATION")
    print("=" * 50)
    
    # Get active rules
    active_rules = ContentModerationRule.objects.filter(active=True)
    print(f"\n📋 Règles actives: {active_rules.count()}")
    
    test_cases = [
        {
            'content': 'Ce cours est vraiment excellent! J\'ai beaucoup appris.',
            'expected_triggers': [],
            'description': 'Contenu positif approprié'
        },
        {
            'content': 'Ce cours est nul, le formateur est un con!',
            'expected_triggers': ['Contenu Toxique - Insultes'],
            'description': 'Contenu avec insulte'
        },
        {
            'content': 'Je déteste cette formation, c\'est de la merde!',
            'expected_triggers': ['Contenu Toxique - Insultes'],
            'description': 'Contenu toxique'
        },
        {
            'content': 'Mon email est test@example.com et mon numéro 0123456789',
            'expected_triggers': ['Informations Personnelles'],
            'description': 'Informations personnelles'
        },
        {
            'content': 'ACHETEZ MAINTENANT!!! OFFRE LIMITEE!!! CLIQUEZ ICI!!!',
            'expected_triggers': ['Spam Commercial'],
            'description': 'Contenu spam'
        },
        {
            'content': 'Les femmes sont moins intelligentes que les hommes',
            'expected_triggers': ['Discrimination et Racisme'],
            'description': 'Contenu discriminatoire'
        }
    ]
    
    print("\n" + "=" * 50)
    print("🔍 TESTS DE DÉTECTION DE RÈGLES")
    print("=" * 50)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Contenu: \"{test_case['content']}\"")
        
        triggered_rules = []
        
        # Test each rule against the content
        for rule in active_rules:
            if check_rule_matches(rule, test_case['content']):
                triggered_rules.append(rule.name)
        
        print(f"Règles déclenchées: {triggered_rules or 'Aucune'}")
        print(f"Attendu: {test_case['expected_triggers'] or 'Aucune'}")
        
        # Check if results match expectations
        test_passed = set(triggered_rules) >= set(test_case['expected_triggers'])
        status_icon = "✅" if test_passed else "❌"
        print(f"Résultat: {status_icon}")
        
        results.append({
            'test': test_case['description'],
            'passed': test_passed,
            'triggered': triggered_rules,
            'expected': test_case['expected_triggers']
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
                print(f"  - {result['test']}")
                print(f"    Attendu: {result['expected']}")
                print(f"    Obtenu: {result['triggered']}")
    
    print("\n" + "=" * 50)
    print("📋 DÉTAILS DES RÈGLES")
    print("=" * 50)
    
    for rule in active_rules:
        print(f"\n🔍 {rule.name}")
        print(f"  Type: {rule.rule_type}")
        print(f"  Sévérité: {rule.get_severity_display()}")
        print(f"  Auto-bloquage: {'Oui' if rule.auto_block else 'Non'}")
        if rule.keywords:
            print(f"  Mots-clés: {rule.keywords}")
        if rule.patterns:
            print(f"  Motifs: {rule.patterns}")

def check_rule_matches(rule, content):
    """Check if a rule matches the given content"""
    content_lower = content.lower()
    
    # Keyword-based rules
    if rule.rule_type == 'keyword' and rule.keywords:
        # Support JSON list or comma-separated string
        if isinstance(rule.keywords, (list, tuple)):
            raw_keywords = rule.keywords
        else:
            raw_keywords = str(rule.keywords).split(',')
        keywords = [str(k).strip().lower() for k in raw_keywords if str(k).strip()]
        for keyword in keywords:
            if keyword in content_lower:
                return True
    
    # Pattern-based rules
    if rule.rule_type == 'pattern' and rule.patterns:
        # Support JSON list or comma-separated string
        if isinstance(rule.patterns, (list, tuple)):
            raw_patterns = rule.patterns
        else:
            raw_patterns = str(rule.patterns).split(',')
        patterns = [str(p).strip() for p in raw_patterns if str(p).strip()]
        for pattern in patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            except re.error:
                continue
    
    # Combined rules can use both keywords and patterns
    if rule.rule_type == 'combined':
        # Check keywords
        if rule.keywords:
            if isinstance(rule.keywords, (list, tuple)):
                raw_keywords = rule.keywords
            else:
                raw_keywords = str(rule.keywords).split(',')
            keywords = [str(k).strip().lower() for k in raw_keywords if str(k).strip()]
            for keyword in keywords:
                if keyword in content_lower:
                    return True
        
        # Check patterns
        if rule.patterns:
            if isinstance(rule.patterns, (list, tuple)):
                raw_patterns = rule.patterns
            else:
                raw_patterns = str(rule.patterns).split(',')
            patterns = [str(p).strip() for p in raw_patterns if str(p).strip()]
            for pattern in patterns:
                try:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
                except re.error:
                    continue
    
    return False

if __name__ == '__main__':
    try:
        test_rule_detection()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
