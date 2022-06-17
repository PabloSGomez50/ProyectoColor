# Django imports
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token

# Project imports
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from .models import User, Project, Category, Skill, Comment
from .forms import ProjectForm
from PIL import Image
import json

# Create your views here.
def test(request):
    """
    Test Template view
    """
    # if request.method == 'POST':
    #     print(f'Post data: \n{request.POST}\n\n')
    #     print(f'Meta: \n{request.headers}\n\n')
    #     print(f'Cookies:\n{request.COOKIES}')
    #     return JsonResponse({'message': 'bien ahi'})
    data = Project.objects.all()
    users = User.objects.filter(is_superuser=False)
    context = {'data': data, 'users': users, 'form': ProjectForm()}

    return render(request, 'projects/index.html', context)

def img_valid(image):
    try:
        Image.init()
        FileExtensionValidator(allowed_extensions=[ext.lower()[1:] for ext in Image.EXTENSION])(image)
        return True
    except ValidationError:
        return False

# def get_csrf(request):
#     print(request.get_host())
#     response = JsonResponse({'detail': 'CSRF cookie set'})
#     response['X-CSRFToken'] = get_token(request)
#     # response['X-CSRFToken'] = request.META['CSRF_COOKIE']
#     return response

def session_view(request):
    """
    Check or update the login user and retrieve the session cookie
    """
    
    if request.user.is_authenticated:
        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Token doesn\'t match.'}, status=400)

        return JsonResponse({
            'isAuth': True,
            'user': request.user.serialize(), 
            'token': token.key
        })
        
    return JsonResponse({'isAuth': False})

@csrf_exempt
def login_view(request):

    if request.method == "POST":
        # Attempt to sign user in
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            token = Token.objects.get(user=user)

            return JsonResponse({
                'message': 'User has been Logged in.',
                'user': user.serialize(),
                'token': token.key
            }, status=200)
        else:
            return JsonResponse({'message': 'Invalid username and/or password.'}, status=400)

@csrf_exempt
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You\'re not logged in.'}, status=400)

    logout(request)
    return JsonResponse({'message': 'User has been logout.'}, status=200)

@csrf_exempt
def register(request):
    """
    View Function to register a user
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST Request'})
    
    data = json.loads(request.body)
    username = data['username']
    email = data["email"]
    # Ensure password matches confirmation
    password = data["password"]
    confirmation = data["confirmation"]

    if password != confirmation:
        return JsonResponse({'error': 'Passwords must match.'}, status=400)

    try:
        user = User.objects.create_user(username, email, password)
        user.save()
        token = Token.objects.create(user=user)
    except IntegrityError:
        return JsonResponse({'error': 'Username already taken.'}, status=400)

    login(request, user)

    return JsonResponse({
        'message': 'User has been registered.',
        'user': user.serialize(),
        'token': token.key
        }, status=201)

def get_user(request, pk):
    """
    Retrieve the profile of a determine user
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'You must need to do a get request'}, status=400)
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Users not found.'}, status=404)

    projects = user.my_projects.all()
    return JsonResponse({'user': user.serialize(), 'projects': [project.serialize() for project in projects]})

@csrf_exempt
def edit_user(request):
    """
    Edit user profile to add some caracteristics
    """
    print(f'POST: {(request.POST)} de tipo {type(request.POST)}')
    print(request.FILES)
    if request.method == 'POST':
        token = request.POST.get('auth')
        data = request.POST.get('data', {})
        keys = data.keys()
        images = request.FILES

        try:
            user = Token.objects.get(key=token).user
            print(user)
            print(request.user == user)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Token not found.'}, status=404)

        print(type(data))
        print(data.get('contant'))
        print(f'Las imagenes son {images} y su tipo {type(images)}')
        # try:
        #     for s in keys:
        #         user[s] = data[s]
        # except IndexError:
        #     print(f'the key {s} is not available.')
        return JsonResponse({'message': 'Datos aceptados'})
        

        
# @api_view(['GET'])
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

# @api_view(['GET', 'POST', 'PUT'])
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

    if request.method == 'POST':
        image = request.FILES
        data = request.POST.get('data', {})
        keys = list(data.keys())
        data = data.values()
        mod = []

        # Check for the changes made by POST request
        project1 = project.serialize()
        for index, s in enumerate(data):
            if s != project1[keys[index]] and keys[index] not in ['image', 'pub_date']:
                project1[keys[index]] = s
                mod.append(keys[index])
        
        
        if img_valid(image):
            project.image = image

        project.pub_date = timezone.now()
        project.members.set([user['id'] for user in project1['members'] if user in users])
        project.categories.set([cat['id'] for cat in project1['categories'] if cat in categories])

        project.save()
        return JsonResponse({'data': project1, 'modify': mod})

    return JsonResponse({'error': 'You must need to do a GET or PUT request'}, status=400)

# @api_view(['POST'])
@csrf_exempt
def create_project(request):
    """
    Create a new project with the data send through post request
    """

    if request.method != "POST":
        return JsonResponse({'error': "POST request required."}, status=400)

    data = request.POST.get('data', {})
    token = request.POST.get('auth')
    images = request.FILES
    print(f'token {token}')
    
    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Token not found.'}, status=404)
    print(f'{user} del tipo {type(user)}')
    print(data)
    print(f' Las imagenes {images} del tipo {type(images)} y su tamaño {len(images)}')

    title = data.get('title')

    project = Project(title = title, owner = user)

    if data.get('description') is not None:
        project.description = data.get('description')

    if img_valid(images):
        project.image.save(images.name, images)

    project.members.set([user])

    if data.get('members') is not None:
        try:
            users = User.objects.filter(id__in = [x['id'] for x in data.get('members')])
            project.members.add(users)
        except User.DoesNotExist:
            return JsonResponse({'error': "Users not found."}, status=404)

    if data.get('categories') is not None:
        try:
            categories = Category.objects.filter(id__in = [x['id'] for x in data.get('categories')])
            project.categories.set(categories)
        except Category.DoesNotExist:
            return JsonResponse({'error': "Category not found."}, status=404)
    
    project.save()
    
    return JsonResponse({'message': f'The project {title} was created'}, status=201)


def create_comment(request, pk):
    """
    Receive and store a new comment in project pk
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'The request needs to be POST method.'}, stauts=400)

    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({'error': "Project not found."}, status=404)
        
    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Token not found.'}, status=404)

    # payload = request.POST
    data = request.POST.get('data', {})
    token = request.POST.get('auth')
    content = data.get('content')

    if len(content) > 0 and len(content) < 256:
        comment = Comment.objects.create(
            content=content,
            user=user,
            project=project
        )

        return JsonResponse({
            'message': f'The comment has been created in {comment.project.title}',
            'user': user.serialize(),
            'project': project.serialize()
        })

    return JsonResponse({'message': 'The comment couldn\'t be created'}, status=400)


def api_test(request):
    # project = Project.objects.get(pk=3)

    if request.method == 'GET':
        return JsonResponse(Skill.objects.get(pk=1).serialize())
        
    if request.method == 'POST':
        print(request.POST)
        # print(json.loads(request.body))
        print(request.FILES)
        # print(request.body)
        # project.image = data
        # project.save()
        return JsonResponse({'message': 'The object was created'}, status=200)
