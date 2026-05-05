from django.shortcuts import render

# Create your views here.
# Create your views here.
def home(request):
    return render(request, 'main/home.html')

def about_me(request):
    return render(request, 'main/about_me.html')