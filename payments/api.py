from django.http import JsonResponse
from users.models import Apprenant

def apprenant_organisation_api(request, apprenant_id):
    try:
        apprenant = Apprenant.objects.get(pk=apprenant_id)
        org = apprenant.organisation
        if org:
            return JsonResponse({'organisation_id': org.id, 'organisation_nom': org.nom})
        else:
            return JsonResponse({'organisation_id': None, 'organisation_nom': None})
    except Apprenant.DoesNotExist:
        return JsonResponse({'error': 'Apprenant not found'}, status=404)
