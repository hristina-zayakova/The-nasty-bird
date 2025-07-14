from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# Create your views here.

def home_view(request: HttpRequest) -> HttpResponse:
    context = {
        'page_title': 'Budgie - Smart Budget Tracking',
        'app_name': 'Budgie',
        'app_description': 'Take control of your finances with our smart budget tracking app',
    }
    return render(request, 'index.html', context)
