from django.shortcuts import render


from django.http import HttpResponse

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /",
        content_type="text/plain"
    )
# Create your views here.
# Create your views here.
def home(request):
    return render(request, 'main/home.html')

def about_me(request):
    return render(request, 'main/about_me.html')