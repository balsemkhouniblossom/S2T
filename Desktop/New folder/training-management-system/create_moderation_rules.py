"""
Script to create default moderation rules
Run with: python manage.py shell -c "exec(open('create_moderation_rules.py').read())"
"""

from moderation.models import ContentModerationRule

# Default moderation rules
default_rules = [
    {
        'name': 'Contenu Toxique - Insultes',
        'description': 'Detecte les insultes et le langage toxique en francais',
        'rule_type': 'toxicity',
        'keywords': [
            'con', 'connard', 'salope', 'pute', 'merde', 'putain', 'batard',
            'encule', 'fils de pute', 'ta gueule', 'ferme-la', 'debile',
            'cretin', 'abruti', 'idiot de merde', 'espece de con'
        ],
        'patterns': [
            r'\b(?:con+ard|sal[eo]pe?|put[ea]|merde|chier|foutre)\b',
            r'\b(?:ferme\s+ta\s+gueule|va\s+te\s+faire)\b',
            r'(?:espece\s+de?|sale)\s+(?:con|idiot|debile)',
        ],
        'threshold': 0.7,
        'auto_block': True,
        'severity': 'high',
        'active': True
    },
    {
        'name': 'Harcelement et Menaces',
        'description': 'Detecte les menaces et le harcelement',
        'rule_type': 'pattern',
        'keywords': [
            'je vais te tuer', 'tu vas mourir', 'je te connais', 'attention a toi',
            'tu me le paieras', 'je sais ou tu habites', 'tu vas le regretter'
        ],
        'patterns': [
            r'(?:je\s+vais\s+te|tu\s+vas)\s+(?:tuer|buter|defoncer|exploser)',
            r'(?:je\s+te\s+connais|je\s+sais\s+ou\s+tu)',
            r'(?:attention\s+a\s+toi|tu\s+me\s+le\s+paieras)',
            r'(?:tu\s+vas\s+le\s+regretter|je\s+vais\s+te\s+retrouver)'
        ],
        'threshold': 0.9,
        'auto_block': True,
        'severity': 'critical',
        'active': True
    },
    {
        'name': 'Contenu Sexuel Inapproprie',
        'description': 'Detecte le contenu sexuel explicite inapproprie',
        'rule_type': 'keyword',
        'keywords': [
            'sexe', 'nude', 'nue', 'penis', 'vagin', 'seins nus', 'porn',
            'porno', 'masturbation', 'orgasme', 'ejaculation', 'fellation'
        ],
        'patterns': [
            r'\b(?:sexe|porn|nude|nue)\b',
            r'(?:seins?\s+nus?|penis|vagin)',
            r'(?:masturb|orgasm|ejacul|fellat)'
        ],
        'threshold': 0.6,
        'auto_block': False,  # Manual review for context
        'severity': 'medium',
        'active': True
    },
    {
        'name': 'Spam Commercial',
        'description': 'Detecte le spam et la publicite non autorisee',
        'rule_type': 'spam',
        'keywords': [
            'achetez maintenant', 'offre limitee', 'gratuit', 'promotion',
            'visitez notre site', 'cliquez ici', 'argent facile', 'devenez riche'
        ],
        'patterns': [
            r'(?:https?://|www\.)\S+',  # URLs
            r'(?:achetez|vendez|gratuit|promotion|offre\s+speciale)',
            r'(?:contactez|appelez|envoyez|email)',
            r'[A-Z\s]{20,}',  # All caps
            r'(.)\1{4,}',  # Repeated characters
            r'(?:argent\s+facile|devenez\s+riche|opportunite\s+unique)'
        ],
        'threshold': 0.5,
        'auto_block': False,
        'severity': 'low',
        'active': True
    },
    {
        'name': 'Discrimination et Racisme',
        'description': 'Detecte les propos discriminatoires et racistes',
        'rule_type': 'pattern',
        'keywords': [
            'sale arabe', 'sale noir', 'sale juif', 'sale blanc', 'negro',
            'bougnoule', 'raton', 'youpin', 'bamboula', 'chinois', 'bride'
        ],
        'patterns': [
            r'(?:sale|espece\s+de)\s+(?:arabe|noir|juif|blanc)',
            r'\b(?:negro|bougnoule|raton|youpin|bamboula)\b',
            r'(?:bride|chinois\s+de\s+merde|sale\s+asiat)',
            r'(?:retourne\s+(?:dans\s+ton|chez\s+toi)|on\s+est\s+chez\s+nous)'
        ],
        'threshold': 0.8,
        'auto_block': True,
        'severity': 'critical',
        'active': True
    },
    {
        'name': 'Sentiment Tres Negatif',
        'description': 'Detecte un sentiment excessivement negatif dans les commentaires',
        'rule_type': 'sentiment',
        'keywords': [
            'nul', 'horrible', 'catastrophique', 'deteste', 'horreur',
            'pourri', 'decevant', 'waste of time', 'perte de temps'
        ],
        'patterns': [],
        'threshold': 0.8,  # High threshold for sentiment
        'auto_block': False,  # Just flag for review
        'severity': 'low',
        'active': True
    },
    {
        'name': 'Informations Personnelles',
        'description': 'Detecte le partage d informations personnelles sensibles',
        'rule_type': 'pattern',
        'keywords': [],
        'patterns': [
            r'\b\d{10,}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card pattern
            r'(?:mon\s+numero|appelle\s+moi|contacte\s+moi)\s*:?\s*\d+',
            r'(?:adresse|j\s+habite)\s*:?\s*\d+.*(?:rue|avenue|boulevard)',
        ],
        'threshold': 0.7,
        'auto_block': False,  # Flag for manual review
        'severity': 'medium',
        'active': True
    }
]

# Create rules if they don't exist
created_count = 0
for rule_data in default_rules:
    rule, created = ContentModerationRule.objects.get_or_create(
        name=rule_data['name'],
        defaults=rule_data
    )
    if created:
        created_count += 1
        print(f"Cree: {rule.name}")
    else:
        print(f"Existe deja: {rule.name}")

print(f"\n{created_count} nouvelles regles de moderation creees!")
print(f"Total des regles actives: {ContentModerationRule.objects.filter(active=True).count()}")

# Display summary
print("\nResume des regles par severite:")
severities = [('low', 'Faible'), ('medium', 'Moyenne'), ('high', 'Elevee'), ('critical', 'Critique')]
for severity, label in severities:
    count = ContentModerationRule.objects.filter(severity=severity, active=True).count()
    print(f"  {label}: {count} regles")

print("\nRegles avec blocage automatique:")
auto_block_rules = ContentModerationRule.objects.filter(auto_block=True, active=True)
for rule in auto_block_rules:
    print(f"  - {rule.name} ({rule.severity})")

print("\nLe systeme de moderation IA est maintenant configure et pret a fonctionner!")
