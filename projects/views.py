# Django imports
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage

# Project imports
from .models import User, Project
from .forms import UserForm, ProjectForm, CommentForm
import json

# Create your views here.
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
        # Get the project list
        try:
            projects = Project.objects.filter(public = True)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Projects not available'}, satus=404)

        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            page = 1

        paginator = Paginator(projects, 2)
        next_link = f'project_list?page={page}'
        prev_link = f'project_list?page={page}'

        try:
            data = paginator.page(page)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        if data.has_next():
            next_link = f'project_list?page={data.next_page_number()}'
        if data.has_previous():
            prev_link = f'project_list?page={data.previous_page_number()}'

    return JsonResponse({
        'data': [project.serialize() for project in data],
        'count': paginator.count,
        'numpages': paginator.num_pages,
        'nextlink': next_link,
        'prevlink': prev_link
    })

def project_test(request):
    """
    Collect all the active projects and send an JSON response
    """
    projects = []
    if request.method == 'GET':
        # Get the project list
        try:
            projects = Project.objects.filter(public = True)
        except Project.DoesNotExist:
            return JsonResponse({
                'error': f'Projects not available'
            }, satus=400)

    return JsonResponse([project.serialize() for project in projects], safe= False)

def project_detail(request, pk):
    """
    Retrieve and modify a project by id/pk
    """

    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({'error': "Project not found."}, status=404)

    if request.method == 'GET':
        return JsonResponse(project.serialize())

    elif request.method == 'POST':
        return JsonResponse({'upload': False})

    elif request.method == 'PUT':
        return JsonResponse(status = 200)

def api_test(request):
    project = Project.objects.get(pk=1)

    if request.method == 'GET':
        form = ProjectForm()
        return render(request, 'projects/project.html', {'form': form})

    if request.method == 'POST':
        data = request.POST
        form = ProjectForm(data, initial= project)
        if form.is_valid():
            form.cleaned_data
            # project = data
            # project.save()
        return JsonResponse(project, safe=False)