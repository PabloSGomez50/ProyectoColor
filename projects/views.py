# Django imports
from django.http import JsonResponse
from django.shortcuts import redirect, render

# Project imports
from .models import Image, User
from .forms import ImageUploadForm

# Create your views here.
def index(request):
    """
    API panel template
    """
    data = Image.objects.all()
    user = User.objects.all()
    context = {'data': data, 'user': user}

    return render(request,"projects/index.html", context)

def api(request):
    """
    Test API request
    """
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('projects:index')
    else:
        form = ImageUploadForm()

    return render(request, 'projects/upload.html', {'form': form})