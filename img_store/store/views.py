from django.shortcuts import render
# from django.http import HttpResponse
# Create your views here.
def index(request):
    message = "Salut tout le monde !"
    context = {
        'message': message
    }
    return render(request, 'store/index.html', context)