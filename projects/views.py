# Django imports
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt

# Project imports
from rest_framework.decorators import api_view
from .models import User, Project, Category, Skill, Comment
from .forms import ProjectForm
import json

# Create your views here.
def test(request):
    """
    Test Template view
    """

    data = Project.objects.all()
    users = User.objects.filter(is_superuser=False)
    context = {'data': data, 'users': users, 'form': ProjectForm()}

    return render(request, 'projects/index.html', context)

@api_view(['GET'])
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

        paginator = Paginator(list(projects), 2)
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

@api_view(['GET', 'PUT'])
@csrf_exempt
def project_detail(request, pk):
    """
    Retrieve and modify a project by id/pk
    """

    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({'error': "Project not found."}, status=404)
    
    try:
        users = [user.serialize() for user in User.objects.filter(is_superuser=False)]
    except User.DoesNotExist:
        return JsonResponse({'error': "Users not found."}, status=404)

    try:
        categories = [cat.serialize() for cat in Category.objects.all()]
    except Category.DoesNotExist:
        return JsonResponse({'error': "Categories not found."}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'project': project.serialize(),
            'users': users,
            'categories': categories
        }, status=200)

    data = json.loads(request.body)
    keys = list(data.keys())
    data = data.values()
    mod = []

    if request.method == 'PUT':
        project1 = project.serialize()

        for index, s in enumerate(data):
            if s != project1[keys[index]] and keys[index] not in ['image', 'pub_date']:
                project1[keys[index]] = s
                mod.append(keys[index])
        
        project.pub_date = timezone.now()
        project.members.set([user['id'] for user in project1['members'] if user in users])
        project.categories.set([cat['id'] for cat in project1['categories'] if cat in categories])

        return JsonResponse({'data': project1, 'modify': mod})

@api_view(['GET', 'POST'])
def create_project(request):
    """
    Create a new project with the data send through post request
    """

    if request.method != "POST":
        return JsonResponse({'error': "POST request required."}, status=400)

    data = json.loads(request.body)
    try:
        owner = User.objects.get(pk = data['owner']['id'])
        users = User.objects.filter(id__in = [x['id'] for x in data['members']])
    except User.DoesNotExist:
        return JsonResponse({'error': "Users not found."}, status=404)

    try:
        categories = Category.objects.filter(id__in = [x['id'] for x in data['categories']])
    except Category.DoesNotExist:
        return JsonResponse({'error': "Category not found."}, status=404)
    
    title = data['title']

    
    return JsonResponse({'title': title, 'users': [user.serialize() for user in users], 'owner': owner.serialize()})
    
    project = Project.objects.create(
        title = data['title'],
        content = data.get('content', ''),
        owner = owner,
    )
    project.members.set(users)
    project.catogies.set(categories)

def api_test(request):
    project = Project.objects.get(pk=3).serialize()

    if request.method == 'GET':
        return JsonResponse(Skill.objects.get(pk=1).serialize())
        
    if request.method == 'POST':
        return JsonResponse(project, status=200)