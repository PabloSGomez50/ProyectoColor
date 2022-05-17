# Django imports
from django.http import JsonResponse
from django.shortcuts import redirect, render

# Project imports
from .models import User, Project

# from .forms import # Create your views here.
def test(request):
    """
    Test Template view
    """

    data = Project.objects.all()
    users = User.objects.all()
    context = {'data': data, 'users': users}

    return render(request, 'projects/index.html', context)

def project_list(request):
    """
    Collect all the active projects and send an JSON response
    """
    projects = []
    if request.method == 'GET':
        try:
            projects = Project.objects.filter(public = True)
        except Project.DoesNotExist:
            return JsonResponse({
                'error': f'Projects not available'
            }, satus=400)
    return JsonResponse([project.serialize() for project in projects], safe=False)