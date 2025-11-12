from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from searcher.models import Cars, Cartarget
def main(request):
    emptyvins=Cars.objects.filter(uuid="")
    ctx={
    'emptyvins':list(emptyvins.values())
    }
    return render(request, 'dashboard.html', ctx)


def assigncar(request):
    carmodel=request.GET.get('carmodel')
    cartarget=request.GET.get('cartarget')
    vin=request.GET.get('vin')
    cartargets=Cartarget.objects.get(model_code=carmodel).targets
    thistarget=next((target for target in cartargets if target['uuid'] == cartarget))
    car=Cars.objects.get(vin=vin)
    #yearttt = thistarget.get('constructionYearTo')
    car.bodytype=thistarget['bodyType']
    car.name=thistarget['fullName']
    car.yearfrom=thistarget.get('constructionYearFrom') or '-'
    car.yearto=thistarget.get('constructionYearTo') or '-'
    car.uuid=f"VHC-{thistarget['uuid']}"
    car.drivetype=thistarget['driveType']
    car.enginetype=thistarget['engineType']
    car.enginecodes=thistarget['engineCodes']
    car.cylinders=thistarget['cylinders']
    car.valve=thistarget['valves']
    car.save()
    print(cartarget, thistarget.get('constructionYearFrom') or '-', thistarget.get('constructionYearFrom') or '-')
    return JsonResponse({
        'rr':'rr'
    })
#controller/views.py
