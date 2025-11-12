from django.shortcuts import render

def main(request):
    return render(request, 'main.html')

def systemstock(request):
    return render(request, 'systemstock.html')
# Create your views here.
#main/views.py
