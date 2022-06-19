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
# from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from .models import User, Project, Category, Skill, Comment
from .forms import ProjectForm, UserForm
from PIL import Image

import json
from .utils import img_valid, doc_valid, edit_model_data, edit_model_files

# Create your views here.
def test(request):
    """
    Test Template view
    """
    data = Project.objects.all()
    users = User.objects.filter(is_superuser=False)
    context = {'data': data, 'users': users, 'form': ProjectForm()}

    return render(request, 'projects/index.html', context)

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

    if request.method == 'POST':
        token = request.POST.get('auth')

        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Token not found.'}, status=404)

        if user != request.user:
            return JsonResponse({'error': 'The user is not the same that the session'}, status=401)

        data = json.loads(request.POST.get('data', '{}'))
        # keys = data.keys()
        # user_keys = list(user.__dict__.keys())
        files = request.FILES
        
        """
        for key in files:
            if key not in user_keys:
                print(f'ERROR: {key} attribute is not valid.')
                continue
                # raise KeyError(f'ERROR: {key} attribute is not valid.')
            if img_valid(files[key]) or doc_valid(files[key]):
                setattr(user, key, files[key])
                print(f'value: {files[key]}')
            else:
                print(f'ERROR: {files[key]} is not an Image or Doc file.')
                # raise ValidationError(f'ERROR: {files[key]} is not an Image file.')
        """
        edit_model_files(user, files)
        try:
            edit_model_data(user, data)
        except KeyError as e:
            print(e.args[0])
            return JsonResponse({'error': f'The key {e.args[1]} couldn\'t be store'}, status=400)
        
        print(user.serialize(), user.email, user.profile_img)
        print(user.description)
        # user.save()
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
        proj_users = [user.serialize() for user in project.members.all()]
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

    # Modify the project data
    if request.method == 'POST':
        token = request.POST.get('auth')

        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Token not found.'}, status=404)
        
        if user != request.user or user not in proj_users:
            return JsonResponse({'error': 'The user is not the same that the session'}, status=401)

        data = json.loads(request.POST.get('data', '{}'))
        files = request.FILES

        # Check for the changes made by POST request
        try:
            edit_model_data(project, data)
        except KeyError as e:
            print(e.args[0])
            return JsonResponse({'error': f'The key {e.args[1]} couldn\'t be store'}, status=400)

        edit_model_files(project, files)
        project.pub_date = timezone.now()
        try:
            project.members.set([user['id'] for user in data.get('members') if user in users])
            project.categories.set([cat['id'] for cat in data.get('categories') if cat in categories])
        except TypeError:
            return JsonResponse({'error': 'Cannot set the members'})

        print(project.serialize())

        return JsonResponse({'success': 'everything it\'s fine.'})
        
    return JsonResponse({'error': 'You must need to do a GET or PUT request'}, status=400)

# @api_view(['POST'])
@csrf_exempt
def create_project(request):
    """
    Create a new project with the data send through post request
    """

    if request.method != "POST":
        return JsonResponse({'error': "POST request required."}, status=400)
    # project_model = Project.objects.model

    data = json.loads(request.POST.get('data', '{}'))
    token = request.POST.get('auth')
    files = request.FILES
    
    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Token not found.'}, status=404)

    if user != request.user:
        return JsonResponse({'error': 'The user is not the same that the session'}, status=401)

    print(f'{user} del tipo {type(user)}')
    print(data)
    print(f' Las imagenes {files} del tipo {type(files)} y su tamaño {len(files)}')

    title = data.get('title')
    if title is None:
        return JsonResponse({'error': 'The project must need a title'}, status=400)

    # The project must need to get asigned the user as owner and member
    project = Project(owner = user)
    project.members.set([user])

    try:
        edit_model_data(project, data)
    except KeyError as e:
        print(e.args[0])
        return JsonResponse({'error': f'The key {e.args[1]} couldn\'t be store'}, status=400)

    edit_model_files(project, files)

    # if data.get('description') is not None:
    #     project.description = data.get('description')

    # if img_valid(files):
    #     project.image.save(files.name, files)

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
    
    print(project.serialize())
    # project.save()
    
    return JsonResponse({'message': f'The project {title} was created'}, status=201)

@csrf_exempt
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
        
    
    token = request.POST.get('auth')
    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Token not found.'}, status=404)

    if user != request.user:
        return JsonResponse({'error': 'The user is not the same that the session'}, status=401)

    # payload = request.POST
    data = json.loads(request.POST.get('data', '{}'))
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


# def api_test(request):
#     # project = Project.objects.get(pk=3)

#     if request.method == 'GET':
#         return JsonResponse(Skill.objects.get(pk=1).serialize())
        
#     if request.method == 'POST':
#         print(request.POST)
#         # print(json.loads(request.body))
#         print(request.FILES)
#         # print(request.body)
#         # project.image = data
#         # project.save()
#         return JsonResponse({'message': 'The object was created'}, status=200)
