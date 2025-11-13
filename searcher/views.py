from django.shortcuts import render, redirect
import requests as req
from django.http import JsonResponse, HttpResponse
import json
from bs4 import BeautifulSoup as bs
from django.db.models import Value, BooleanField, Case, When, Q
from django.db.models.expressions import RawSQL
from .models import Cars, Products, Brand, Brandpdcts, Refpdcts, Carmodel, Cartarget, Token, Config, Refbrands
import re
import base64
import threading
from .funcs import processproducts, sendtelegram, processindirectref, processbranddirectref, processbrandproducts, getnewtoken



# Create your views here.
#repref: ref results from rep
#directref: ref result from azshp
def encode_to_base64(input_string):
    # Encode the input string to Base64
    encoded_bytes = base64.b64encode(input_string.encode('utf-8'))
    # Convert bytes to a string and remove padding characters ('=')
    encoded_str = encoded_bytes.decode('utf-8').rstrip('=')
    return encoded_str
def vindata(request):

    vin=request.GET.get('vin').strip().lower()
    # get car from database first
    #cars=Cars.objects.filter(vin=vin)
    cars = Cars.objects.filter(
        Q(vin__iexact=vin) | Q(vinequ__icontains=vin)
    )

    if cars:
        print('>>> vin data in db')
        # check if it was created without car #RRDFE145
        if cars[0].uuid=='':
            # print('>>> Sending telegram message')
            # send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            # params = {
            #     'chat_id': chat_id,
            #     'text': vin
            # }
            #
            # response = req.get(send_message_url, params=params)
            print('>>> uuid is empty, means the vin is saved and wating for data manually')
            return JsonResponse({
                'success':False,
                'error':'Multiple vehicules detecté'
            #fromdb will indicate if the data is from db, this will be used to handle data in frontend
            })
        return JsonResponse({
            'success':True,
            #fromdb will indicate if the data is from db, this will be used to handle data in frontend
            'fromdb':True,
            'data':list(cars.values())
        })
    #else:
    print('>>> vin data not in db, searching .....')
    # if none in database then get it from 3rd party
    # another bearer =====> leiqduRW_AAtUhiexlfzsUlWJqE
    #data=asyncio.run(fetch_data(vin))
                #print(data)

                # Process the data from the external API
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive",
      }
    vinurl=f"https://www.repxpert.ma/api/Repxpert-MA/vehicleKeySystems/vin/vehicles/{vin}?globalCarPark=true&fields=DEFAULT,modelSeries(DEFAULT)&vehicleType=passengerCar&lang=fr&curr=RXP&catalogCountry=MA"

    res=req.get(vinurl, headers=headers)
    data=json.loads(res.content.decode('utf-8'))
    print('>> data', data)
        
    try:
        if len(data['targets']) == 1:
            # check if there is car with the same uuid, somtimes multiple vins can be in one car, the vin has only a small difference
            uuidcar = Cars.objects.filter(uuid=f"VHC-{data['targets'][0]['uuid']}")
            print('>>> length of cars', len(uuidcar), [i.id for i in uuidcar])
            if uuidcar:
                print('>> there is car and length is just1 to check if this gives more than one car')
                if not vin in uuidcar[0].vinequ:
                    print('>> adding vineq')
                    uuidcar[0].vinequ.append(vin)
                    uuidcar[0].save()
                return JsonResponse({
                    'success': True,
                    'fromdb': True,
                    'data': list(uuidcar.values())
                })

            yearttt = data['targets'][0].get('constructionYearTo')

            # Create a new car entry in the database
            Cars.objects.create(
                vin=vin,
                bodytype=data['targets'][0]['bodyType'],
                name=data['targets'][0]['fullName'],
                yearfrom=data['targets'][0]['constructionYearFrom'],
                yearto=yearttt,
                uuid=f"VHC-{data['targets'][0]['uuid']}",
                drivetype=data['targets'][0]['driveType'],
                enginetype=data['targets'][0]['engineType'],
                enginecodes=data['targets'][0]['engineCodes'],
                cylinders=data['targets'][0]['cylinders'],
                valve=data['targets'][0]['valves'],
            )

            return JsonResponse({
                'success': True,
                'fromdb': False,
                'data': data['targets']
            })

        else:
            # Create a placeholder car entry in the database
            Cars.objects.create(
                vin=vin,
                bodytype='',
                name='',
                yearfrom='',
                yearto='',
                uuid='',
                drivetype='',
                enginetype='',
                enginecodes='',
                cylinders=0,
                valve=0,
            )

            # Asynchronous request to send Telegram message
            print('>>> Sending telegram message in async')
            threading.Thread(target=sendtelegram, args=(vin,)).start()

            return JsonResponse({
                'success': False,
                'error': 'Multiple vehicles detected'
            })

        return JsonResponse({'success': False, 'error': 'Error processing request'})
    except Exception as e:
        print('>> error', e)
        threading.Thread(target=getnewtoken).start()
        return JsonResponse({
            'success': False,
        })
def getprudcts(request):
    categoryname=request.GET.get('categoryname')
    carid=request.GET.get('carid').replace("VHC-", '')
    # category and assamblgroup come both from the frontend with a dash(-)
    assamblyandcategory=request.GET.get('categoryid')
    categoryid=request.GET.get('categoryid').split('-')
    print('>>>> searching db')
    products = Products.objects.filter(categoryid=categoryid[0], assemblyGroups=categoryid[1])
    #products = []
    products = [product for product in products if carid in product.car_codes]
    if len(products)>0:
        brands=Brand.objects.get(code=f'{assamblyandcategory}-{carid}')
        print('there is data in db')
        return JsonResponse({
        'trs':render(request, 'pdctstrs.html', {'products':products, 'fromdb':True, 'brands':brands.brands, 'assamblyandcategory':assamblyandcategory, 'categoryname':categoryname}).content.decode('utf-8'),
        })
    else:

        print('>>>> searching in rep')
        headers={
            "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
            "Connection": "keep-alive"
        }

        assamblyurl=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query=::linkages.target:Vehicle%21{carid}:assemblyGroups:{categoryid[1]}&pageSize=40&categoryCode={categoryid[0]}&lang=fr&curr=RXP&catalogCountry=MA"

        res=req.get(assamblyurl, headers=headers)
        # with open('data.json', 'w') as ff:
        #     print(json.loads(res.content.decode('utf-8'))['products'], file=ff)
        try:
            products=json.loads(res.content.decode('utf-8'))['products']
        except:
            threading.Thread(target=getnewtoken).start()
            return JsonResponse({
            'trs':render(request, 'pdctstrs.html', {'products':[{'fullName':'Les Données serons disponible dans un instant'}], 'fromdb':False, 'brands':[], 'assamblyandcategory':'--', 'repref':True, 'categoryname':categoryname}).content.decode('utf-8'),
            })
        brands=json.loads(res.content.decode('utf-8'))['facets'][0]['values']
        if not Brand.objects.filter(code=f'{assamblyandcategory}-{carid}').exists():
            print('>>>>> create brands')
            Brand.objects.create(code=f'{assamblyandcategory}-{carid}', brands=brands)
        #this should run on another thread
        print('>>> process the data in another thread wit args')
        ref=''
        threading.Thread(target=processproducts, args=(ref, products, carid, categoryid)).start()
        print('>>> return the response')
        return JsonResponse({
            'trs':render(request, 'pdctstrs.html', {'products':products, 'brands':brands, 'assamblyandcategory':assamblyandcategory, 'categoryname':categoryname}).content.decode('utf-8')
        })

def getproducdataforsuppliers(request):
    # I need to find a good way to sho this inof in the frontend (I did!)
    code=request.GET.get('code')
    p=Products.objects.filter(code=code).first()
    url=f'https://www.repxpert.ma/api/Repxpert-MA/products/{code}/linkages/manufacturers?targetTypeCodes=passengerCar&globalCarPark=true&fields=FULL&lang=fr&curr=RXP&catalogCountry=MA'
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive",
    }
    res=req.get(url, headers=headers, timeout=10)
    print('>> res car', res.content)
    cars=json.loads(res.content.decode('utf-8'))['manufacturers']
    print('>> cars', cars)
    
    if len(p.oems)==0:
        print('No OEMS')
        print('>>>> searching in rep')
        headers={
            "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
            "Connection": "keep-alive"
        }
        url=f"https://www.repxpert.ma/api/Repxpert-MA/products/{code}/oenumbers?lang=fr&curr=RXP&catalogCountry=MA"
        try:
            res=req.get(url, headers=headers, timeout=10)
            oems=json.loads(res.content.decode('utf-8'))['oenumbers']
            print('>>> assigning oems')
            p.oems=oems
            p.save()
            return render( request, 'getproducdataforsuppliers.html', {
            'cars':cars,
            'oems':oems,
            'features':p.features
            })
        except req.exceptions.Timeout:
            print('>>> ERROR in getting oems')
            oems=[{"manufacturer": {"name": "ERROR"}, "numbers": [{"normalizedNumber": "ERROR", "number": "ERROR"}]}]
            return render( request, 'getproducdataforsuppliers.html', {
            'cars':cars,
            'oems':oems,
            'features':p.features
            })
    else:
        print('>>> there are oems in db')
        print('>>>> cars', cars)

        return render( request, 'getproducdataforsuppliers.html', {
        'oems':p.oems,
        'cars':cars,
        'fromdb':True,
        'features':p.features
        })
# THIS WILL DISPLAY data for local
def getproductoems(request):
    # I need to find a good way to sho this inof in the frontend (I did!)
    code=request.GET.get('code')
    p=Products.objects.filter(code=code).first()
    url=f'https://www.repxpert.ma/api/Repxpert-MA/products/{code}/linkages/manufacturers?targetTypeCodes=passengerCar&globalCarPark=false&fields=FULL&lang=fr&curr=RXP&catalogCountry=MA'
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive",
    }
    res=req.get(url, headers=headers, timeout=10)
    cars=json.loads(res.content.decode('utf-8'))['manufacturers']
    
    print('>> ', p, Products.objects.filter(code=code))
    if len(p.oems)==0:
        print('No OEMS')
        print('>>>> searching in rep')
        headers={
            "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
            "Connection": "keep-alive"
        }

        url=f"https://www.repxpert.ma/api/Repxpert-MA/products/{code}/oenumbers?lang=fr&curr=RXP&catalogCountry=MA"
        try:
            res=req.get(url, headers=headers, timeout=10)
            oems=json.loads(res.content.decode('utf-8'))['oenumbers']
            print('>>> assigning oems')
            p.oems=oems
            p.save()
            return JsonResponse({
            'cars':render(request, 'cars.html', {'cars':cars}).content.decode('utf-8'),
            'oems':render(request, 'oems.html', {'oems':oems}).content.decode('utf-8'),
            'features':render(request, 'features.html', {'features':p.features}).content.decode('utf-8'),
            })
        except req.exceptions.Timeout:
            print('>>> ERROR in getting oems')
            oems=[{"manufacturer": {"name": "ERROR"}, "numbers": [{"normalizedNumber": "ERROR", "number": "ERROR"}]}]
            return JsonResponse({
            'cars':render(request, 'cars.html', {'cars':cars}).content.decode('utf-8'),
            'oems':render(request, 'oems.html', {'oems':oems}).content.decode('utf-8'),
            'features':render(request, 'features.html', {'features':p.features}).content.decode('utf-8')
            })
    else:
        return JsonResponse({
        'oems':render(request, 'oems.html', {'oems':p.oems}).content.decode('utf-8'),
        'cars':render(request, 'cars.html', {'cars':cars}).content.decode('utf-8'),
        'fromdb':True,
        'features':render(request, 'features.html', {'features':p.features}).content.decode('utf-8')
        })


def getbrandpdcts(request):
    carid=request.GET.get('carid').replace("VHC-", '')
    brandid=request.GET.get('brandid')
    count=request.GET.get('count')
    brandname=request.GET.get('brandname').split('##')[0].strip()
    # category and assamblgroup come both from the frontend with a dash(-)
    assamblyandcategory=request.GET.get('assamblyandcategory')
    # category=0 assambly=1
    categoryid=assamblyandcategory.split('-')
    print('>>>> brandname', brandname)

    # old code, searching db, then searchin rep, now we need to search rep first, cause there might be just one product
    # print('>>>> searching db')
    # products = Products.objects.filter(categoryid=categoryid[0], assemblyGroups=categoryid[1], brandid=brandid)
    # #products = []
    # products = [product for product in products if carid in product.car_codes]
    # if len(products)>0:
    #     print('>>>>>> brand products in db')
    #     return JsonResponse({
    #         'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':True, }).content.decode('utf-8'),
    #     })
    # else:
    #     print('>>>>>> No data in db')
    #     print('>>>>> search rep')
    #     headers={
    #         "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
    #         "Connection": "keep-alive"
    #     }
    #     brandsurl=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query=::linkages.target:Vehicle%21{carid}:brand:{brandid}:assemblyGroups:{categoryid[1]}&pageSize=40&categoryCode={categoryid[0]}&lang=fr&curr=RXP&catalogCountry=MA"
    #     res=req.get(brandsurl, headers=headers)
    #     # with open('data.json', 'w') as ff:
    #     #     print(json.loads(res.content.decode('utf-8'))['products'], file=ff)
    #     products=json.loads(res.content.decode('utf-8'))['products']
    #     print(len(products))
    #     for index, i in enumerate(products):
    #         try:
    #             p=Products.objects.get(code=i['code'])
    #             print('>>> assign brandid')
    #             # assign the brandid
    #             p.brandid=brandid
    #             cars=p.car_codes or []
    #             if not carid in cars:
    #                 cars.append(carid)
    #                 p.car_codes=cars
    #             p.save()
    #         except Exception as e:
    #             print(">> ERR in gettig the product", e)
    #             try:
    #                 Products.objects.create(
    #                 car_codes=[carid],
    #                 features=i.get('classifications', [{'features':''}])[0].get('features'),
    #                 fullName=i.get('fullName'),
    #                 brand=i.get('brand', '').get('name'),
    #                 brandref=i['catalogArticleNumber'],
    #                 brandid=brandid,
    #                 refs=[i.get('catalogArticleNumber', '')],
    #                 code=i.get('code', ''),
    #                 image=i.get('images', [{'url':''}])[0].get('url'),
    #                 categoryid=categoryid[0],
    #                 assemblyGroups=categoryid[1],
    #                 ean=i.get('ean', ''))
    #             except Exception as e:
    #                 print('>>>> ERR in creating product: ', e, index)
    #     return JsonResponse({
    #         'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':False, }).content.decode('utf-8'),
    #     })

    # new code
    #update: search the db first, when length of products is not count > search rep
    #try:
    #print('trying to get brandproducts')
    #brandpdcts=Brandpdcts.objects.get(code=f'{brandid}-{carid}-{assamblyandcategory}')
    # am gonna use brand name, since it's already there, cause products get created without a brandid
    products = Products.objects.filter(categoryid=categoryid[0], assemblyGroups=categoryid[1], brand=brandname, car_codes__icontains=carid)
    # products = Products.objects.filter(categoryid=categoryid[0], assemblyGroups=categoryid[1], brandid=brandid, car_codes__icontains=carid)
    print('>> len before', len(products), categoryid[1],categoryid[0], carid)
    # products = Products.objects.filter(categoryid=categoryid[0], assemblyGroups=categoryid[1], brandid=brandid)
    #products = []
    #products = [product for product in products if carid in product.car_codes]
    print('>> count, len(products)', count, len(products))
    if len(products)==int(count)>0:
        return JsonResponse({
            'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':True, }).content.decode('utf-8'),
        })
    # except Exception as e:
    else:
        print('>>>>> search rep, products != count')
        headers={
            "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
            "Connection": "keep-alive"
        }
        brandsurl=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query=::linkages.target:Vehicle%21{carid}:brand:{brandid}:assemblyGroups:{categoryid[1]}&pageSize=120&categoryCode={categoryid[0]}&lang=fr&curr=RXP&catalogCountry=MA"
        res=req.get(brandsurl, headers=headers)
        # with open('data.json', 'w') as ff:
        #     print(json.loads(res.content.decode('utf-8'))['products'], file=ff)
        res.raise_for_status()
        try:
            products=json.loads(res.content.decode('utf-8'))['products']
        except:
            threading.Thread(target=getnewtoken).start()
            return JsonResponse({
            'trs':render(request, 'pdctstrs.html', {'products':[{'fullName':'Les Données serons disponible dans un instant'}], 'fromdb':False, 'brands':[], 'assamblyandcategory':'--', 'repref':True}).content.decode('utf-8'),
            })
        # processbrandproducts
        ref=''
        threading.Thread(target=processbrandproducts, args=(ref, products, brandid, categoryid, carid)).start()
        Brandpdcts.objects.create(code=f'{brandid}-{carid}-{assamblyandcategory}', loaded=True)
        return JsonResponse({
            'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':False, }).content.decode('utf-8'),
        })

def checksuppliers(request):
    ref=request.GET.get('ref').strip().replace(' ', '').lower()
    print('>>> ', ref)
    res=req.get('http://localhost:5000/products/checkfromadashi', {'ref':ref})
    return JsonResponse(json.loads(res.text))

def getrefdata(request):
    ref=request.GET.get('ref').strip().replace(' ', '').lower()
    assambly=request.GET.get('assambly')
    categoryid=request.GET.get('categoryid')
    print(ref, assambly)

    try:
        print('trying to get refproducts')
        refpdcts=Refpdcts.objects.get(code=f'{ref}-{assambly}')
        products = Products.objects.filter(assemblyGroups=assambly).annotate(
            has_ref=Case(
                When(refs__icontains=f'"{ref}"', then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).filter(has_ref=True)
        products.update(categoryid=categoryid)
        print('>>> products', products)
        return JsonResponse({
        'trs':render(request, 'pdctstrs.html', {'products':products, 'fromdb':True,'brands':refpdcts.brands, 'assamblyandcategory':assambly, 'repref':True}).content.decode('utf-8'),
        })
    except Exception as e:
        print(e, '>>> searchin rep')
        headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive"
        }
        url=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query={ref}::assemblyGroups:{assambly}&pageSize=40&lang=fr&curr=RXP&catalogCountry=MA"
        res=req.get(url, headers=headers)
        # with open('data.json', 'w') as ff:
        #     print(json.loads(res.content.decode('utf-8'))['products'], file=ff)
        res.raise_for_status()
        brands=json.loads(res.content.decode('utf-8'))['facets'][0]['values']
        try:
            products=json.loads(res.content.decode('utf-8'))['products']
        except:
            threading.Thread(target=getnewtoken).start()
            return JsonResponse({
            'trs':render(request, 'pdctstrs.html', {'products':[{'fullName':'Les Données serons disponible dans un instant'}], 'fromdb':False, 'brands':[], 'assamblyandcategory':'--', 'repref':True}).content.decode('utf-8'),
            })
        for index, i in enumerate(products):
            try:
                p=Products.objects.get(code=i['code'])
                print('>>> assign assambly and adding ref to refs')
                # assign the brandid
                refs=p.refs # it needs to be populated all ready, since it's in db da means it has refs RR520
                if ref not in refs:
                    refs.append(ref)
                    p.refs=refs
                p.assemblyGroups=assambly
                p.save()
            except Exception as e:
                print(">> ERR in gettig the product")
                try:
                    print(">> trying to create product")
                    product=Products.objects.create(
                    car_codes=[],
                    features=i.get('classifications', [{'features':''}])[0].get('features'),
                    fullName=i.get('fullName'),
                    brand=i.get('brand', '').get('name'),
                    brandref=i['catalogArticleNumber'],
                    code=i.get('code', ''),
                    image=i.get('images', [{'url':''}])[0].get('url'),
                    assemblyGroups=assambly,
                    categoryid=categoryid,
                    ean=i.get('ean', ''))
                    if ref==i.get('catalogArticleNumber'):
                        product.refs=[i.get('catalogArticleNumber')] #RR520
                    else:
                        product.refs=[i.get('catalogArticleNumber'), ref]
                    product.save()
                except Exception as e:
                    print('>>>> ERR in creating product: ', e, index)
        Refpdcts.objects.create(code=f'{ref}-{assambly}', loaded=True, brands=brands)
        return JsonResponse({
        'trs':render(request, 'pdctstrs.html', {'products':products, 'fromdb':False, 'brands':brands, 'assamblyandcategory':assambly, 'repref':True}).content.decode('utf-8'),
        })

def getbrandrefpdcts(request):
    brandid=request.GET.get('brandid')
    brandname=request.GET.get('brandname').split('##')[0].strip()
    brandcount=request.GET.get('brandcount')
    ref=request.GET.get('ref').strip().replace(' ', '')
    print('>> ref', ref)
    # category and assamblgroup come both from the frontend with a dash(-)
    assambly=request.GET.get('assambly')
    print(brandid, brandcount, brandname, ref, assambly)
    # products=Products.objects.filter(brand=brandname)
    # brand name is batter cause all products get saved with brandname but not with brandid
    products=Products.objects.filter(brandid=brandid, refs__icontains=ref)
    # products=Products.objects.filter(brand=brandname, refs__icontains=ref)
    print('>> len prodcuts', len(products))
    # products = [
    #     product for product in products
    #     if ref in product.refs
    # ]
    try:
        print('>>> trying to add brandid')
        [i.update(brandid=brandid) for i in products]
    except:
        pass
    print('products length, brandcount', len(products), brandcount, len(products)==int(brandcount))
    if len(products)==int(brandcount):
        print('there is products')
        return JsonResponse({
            'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':True, }).content.decode('utf-8'),
            'fromdb':True
        })
    print('>>> No products with this brandid in db, searching rep')
    # category=0 assambly=1
    headers={
    "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
    "Connection": "keep-alive"
    }
    print('>>>> brandid', brandid)
    url=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query={ref}::brand:{brandid}:assemblyGroups:{assambly}&pageSize=40&lang=fr&curr=RXP&catalogCountry=MA"
    res=req.get(url, headers=headers)
    # with open('data.json', 'w') as ff:
    #     print(json.loads(res.content.decode('utf-8'))['products'], file=ff)
    res.raise_for_status()
    try:
        products=json.loads(res.content.decode('utf-8'))['products']
    except:
        threading.Thread(target=getnewtoken).start()
        return JsonResponse({
        'trs':render(request, 'pdctstrs.html', {'products':[{'fullName':'Les Données serons disponible dans un instant'}], 'fromdb':False, 'brands':[], 'assamblyandcategory':'--', 'repref':True}).content.decode('utf-8'),
        })
    categoryid=['', '']
    carid=''
    threading.Thread(target=processbrandproducts, args=(ref, products, brandid, categoryid, carid)).start()
    # for index, i in enumerate(products):
    #     try:
    #         p=Products.objects.get(code=i['code'])
    #         print(p.id, '>>> assign assambly, brandid, ref and adding ref to refs')
    #         # assign the brandid
    #         refs=p.refs # it needs to be populated all ready, since it's in db da means it has refs RR520
    #         if ref not in refs:
    #             refs.append(ref)
    #             p.refs=refs
    #         p.assemblyGroups=assambly
    #         p.brandid=brandid
    #         p.save()
    #     except Exception as e:
    #         print(">> ERR in gettig the product")
    #         try:
    #             print(">> trying to create product")
    #             product=Products.objects.create(
    #             car_codes=[],
    #             features=i.get('classifications', [{'features':''}])[0].get('features'),
    #             fullName=i.get('fullName'),
    #             brand=i.get('brand', '').get('name'),
    #             brandref=i['catalogArticleNumber'],
    #             code=i.get('code', ''),
    #             image=i.get('images', [{'url':''}])[0].get('url'),
    #             assemblyGroups=assambly,
    #             ean=i.get('ean', ''))
    #             if ref==i.get('catalogArticleNumber'):
    #                 product.refs=[i.get('catalogArticleNumber')] #RR520
    #             else:
    #                 product.refs=[i.get('catalogArticleNumber'), ref]
    #             product.save()
    #         except Exception as e:
    #             print('>>>> ERR in creating product: ', e, index)
    return JsonResponse({
        'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':False}).content.decode('utf-8'),
        'fromdb':False
    })

def getmodels(request):
    manifacturer_code=request.GET.get('manifacturer_code')
    carmodels=Carmodel.objects.filter(manifacturer_code=manifacturer_code).first()
    if carmodels:
        print('>>> car models in db')
        # return the select
        return JsonResponse({
        'html':render(request, 'modelselect.html', {'models':carmodels.models, 'fromdb':True}).content.decode('utf-8'),
        'fromdb':True
        })
    else:
        print('>>> car models are not in db')
        headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive"
        }
        url=f"https://www.repxpert.ma/api/Repxpert-MA/manufacturers/{manifacturer_code}/modelSeries?targetTypeCodes=passengerCar&lang=fr&curr=RXP&catalogCountry=MA"
        res=req.get(url, headers=headers)
        models=json.loads(res.content.decode('utf-8'))['modelSeries']
        # create models for this ùanifacturer
        Carmodel.objects.create(manifacturer_code=manifacturer_code, models=models)
        # return models select
        return JsonResponse({
        'html':render(request, 'modelselect.html', {'models':models, 'fromdb':False}).content.decode('utf-8'),
        'fromdb':False
        })
def gettargets(request):
    model_code=request.GET.get('model_code')
    cartargets=Cartarget.objects.filter(model_code=model_code).first()
    if cartargets:
        print('>>> car targets in db')
        # return the select
        return JsonResponse({
        'success':True,
        'html':render(request, 'targetselect.html', {'targets':cartargets.targets, 'fromdb':True}).content.decode('utf-8'),
        'fromdb':True
        })
    else:
        print('>>> car targets are not in db')
        headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive"
        }
        url=f"https://www.repxpert.ma/api/Repxpert-MA/modelSeries/{model_code}/targets?targetTypeCodes=passengerCar&globalCarPark=true&lang=fr&curr=RXP&catalogCountry=MA"
        res=req.get(url, headers=headers)
        try:
            targets=json.loads(res.content.decode('utf-8'))['targets']
            print('>> writing')
            with open('data.json', 'w') as ff:
                print(targets, file=ff)
        except:
            # meas the token has expired, get new one
            threading.Thread(target=getnewtoken).start()
            return JsonResponse({
            'success':False,
            })
        # create targets for this ùanifacturer
        Cartarget.objects.create(model_code=model_code, targets=targets)
        # return models select
        return JsonResponse({
        'success':True,
        'html':render(request, 'targetselect.html', {'targets':targets, 'fromdb':False}).content.decode('utf-8'),
        'fromdb':False
        })

def searchrefdirect(request):
    searchedref=request.GET.get('ref').strip().lower().replace(' ', '')
    print(">>> Checking the db first, no we can't cause we dont have brands, brands are important when searching for ref")
    # if Config.objects.first().dbfirst
    #url=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query={searchedref}:relevance&pageSize=40&lang=fr&curr=RXP&catalogCountry=MA"
    url =f'https://shop.az-parts.net/index.php?q={searchedref}&page=search'
    headers = {
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    res = req.get(url, headers=headers, timeout=10)
    # with open('data.html', 'w', encoding='utf-8') as ff:
    #     print(res.text.split('<div class="container-fluid">')[2], file=ff)
    html=res.text.split('<div class="container-fluid">')[2]
    soup = bs(html, 'html.parser')


    # Initialize an empty list to hold the product data
    products = []

    # Find all product cards
    product_cards = soup.find_all('div', class_='card-prod')
    if len(product_cards)==0:
        print('>>> No products')
        return JsonResponse({
        'trs':render(request, 'pdctstrs.html', {'products':[], 'fromdb':True,'brands':[],  'directref':True}).content.decode('utf-8'),
        })
    # Iterate over each product card and extract data

    for index, card in enumerate(product_cards):
        product = {}
        brandid = card.find('input', {'name': f'brandid{index}'})['value']
        ref = card.find('input', {'name': f'artref{index}'})['value'].lower().replace(' ', '')
        name = card.find('input', {'name': f'artlabel{index}'})['value']
        code='Ext-TA-'+encode_to_base64(f'{brandid}:{ref}')
        image_tag = card.find('a').find('img')
        image_url=''
        try:
            image_url = image_tag['src']
        except:
            image_url = ''
        features=[]
        for li in card.find_all('li'):
            specs = {"featureValues": [{"value": ""}], "name": ""}
            value = li.text.split(':')[0].strip()
            key = li.find('span').text.strip()
            #print('>>> name, value li', name, value)
            specs['featureValues'][0]['value']=value
            specs['name']=key
            features.append(specs)
        brand=card.find('h5').text.split('-')[0].strip()
        # check if ptoduct exists
        # this shoul run on another thread
        threading.Thread(target=processindirectref, args=(code, brandid, ref, brand, features, searchedref, name, image_url)).start()
        # Extract image URLs
        product['image']=image_url
        product['code']=code
        product['brandref']=ref

        # Extract product name
        product['fullName'] = name
        product['features'] = features
        product['brand'] = brand
        product['pdctid'] = card.find('input', {'name': f'artid{index}'})['value']

        # Extract reference
        #product['catalogArticleNumber']=ref
        # Extract specifications (width, height, thickness, brake system)
        # specs = {}
        # for li in card.find_all('li'):
        #     key = li.text.split(':')[0].strip()
        #     value = li.find('span').text.strip()
        #     specs[key] = value
        # product['specifications'] = specs


        # Extract price

        # Extract availability

        # Extract hidden fields (additional information)
        # product['artref'] = card.find('input', {'name': f'artref{index}'})['value']
        # product['brandid']=brandid
        # product['code']=code
        # Add the product data to the list
        products.append(product)
    brands = []
    #{"count": 2, "name": "A.B.S.", "query": {"query": {"value": "::linkages.target:Vehicle%21TA-52439:brand:206:assemblyGroups:100579"}}, "selected": false}
    select_element = soup.find('select', {'id': 'filterBrand'})
    for option in select_element.find_all('option'):
        value = option.get('value')
        if not value=='0':
            text = option.text.strip()
            brand=text.split()[0]
            # Use regex to find the number inside parentheses
            count = re.search(r'\((\d+)\)', text)
            count = count.group(1) if count else None
            # Append the extracted data as a dictionary
            brands.append({"query": {"query": {"value": f"::linkages.target:Vehicle%21TA-:brand:{value}:assemblyGroups:"}}, 'name': brand, 'count': count})
    #product['brands']=brands
    if not Refbrands.objects.filter(ref=searchedref).exists():
        Refbrands.objects.create(ref=searchedref, brands=brands)
    return JsonResponse({
    'trs':render(request, 'pdctstrs.html', {'products':products, 'fromdb':True,'brands':brands,  'directref':True}).content.decode('utf-8'),
    #'html':html,
    'products':products,
    'brands':brands
    })
def getbranddirectref(request):
    searchedref=request.GET.get('ref')
    brandname=request.GET.get('brandname')
    brandcount=request.GET.get('brandcount')
    brandid=request.GET.get('brandid')
    print('>>> ', brandcount, brandname, searchedref)
    products=Products.objects.filter(brandid=brandid)
    products = [
        product for product in products
        if str(searchedref) in product.refs
    ]
    print('>> brandcount, lenproducts', brandcount, len(products), brandcount==len(products))
    if int(brandcount)==len(products):
        print('>> in db')
        return JsonResponse({
            # why return pdctstrs instead of brandstrs
            'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':True}).content.decode('utf-8'),
            #'html':html,
        })
    else:
        print('>>not in db, getting..')
        headers = {
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        url=f'https://shop.az-parts.net/index.php?fb={brandid}&q={searchedref}&page=search'
        res = req.get(url, headers=headers)
        # with open('data.html', 'w', encoding='utf-8') as ff:
        #     print(res.text.split('<div class="container-fluid">')[2], file=ff)
        html=res.text.split('<div class="container-fluid">')[2]
        soup = bs(html, 'html.parser')


        # Initialize an empty list to hold the product data
        products = []

        # Find all product cards
        product_cards = soup.find_all('div', class_='card-prod')
        # Iterate over each product card and extract data
        # this should be asyn or run in another thread
        for index, card in enumerate(product_cards):
            product = {}
            brandid = card.find('input', {'name': f'brandid{index}'})['value']
            ref = card.find('input', {'name': f'artref{index}'})['value']
            name = card.find('input', {'name': f'artlabel{index}'})['value']
            code='Ext-TA-'+encode_to_base64(f'{brandid}:{ref}')
            image_tag = card.find('a').find('img')
            image_url=''
            try:
                image_url = image_tag['src']
            except:
                image_url = ''
            features=[]
            specs = {"featureValues": [{"value": ""}], "name": ""}
            for li in card.find_all('li'):
                value = li.text.split(':')[0].strip()
                key = li.find('span').text.strip()
                #print('>>> name, value li', name, value)
                specs['featureValues'][0]['value']=value
                specs['name']=key
                features.append(specs)
            brand=card.find('h5').text.split('-')[0].strip()
            # check if ptoduct exists
            #processbranddirectref
            threading.Thread(target=processbranddirectref(code, brandid, ref, brand, searchedref, features, name, image_url)).start()
            # Extract image URLs
            product['image']=image_url
            product['code']=code
            product['brandref']=ref

            # Extract product name
            product['fullName'] = name
            product['features'] = features
            product['brand'] = brand
            product['pdctid'] = card.find('input', {'name': f'artid{index}'})['value']

            # Extract reference
            #product['catalogArticleNumber']=ref
            # Extract specifications (width, height, thickness, brake system)
            # specs = {}
            # for li in card.find_all('li'):
            #     key = li.text.split(':')[0].strip()
            #     value = li.find('span').text.strip()
            #     specs[key] = value
            # product['specifications'] = specs


            # Extract price

            # Extract availability

            # Extract hidden fields (additional information)
            # product['artref'] = card.find('input', {'name': f'artref{index}'})['value']
            # product['brandid']=brandid
            # product['code']=code
            # Add the product data to the list
            products.append(product)
        brands = []
        #{"count": 2, "name": "A.B.S.", "query": {"query": {"value": "::linkages.target:Vehicle%21TA-52439:brand:206:assemblyGroups:100579"}}, "selected": false}
        select_element = soup.find('select', {'id': 'filterBrand'})
        for option in select_element.find_all('option'):
            value = option.get('value')
            if not value=='0':
                text = option.text.strip()
                brand=text.split()[0]
                # Use regex to find the number inside parentheses
                count = re.search(r'\((\d+)\)', text)
                count = count.group(1) if count else None
                # Append the extracted data as a dictionary
                brands.append({"query": {"query": {"value": f"::linkages.target:Vehicle%21TA-:brand:{value}:assemblyGroups:"}}, 'name': brand, 'count': count})
        #product['brands']=brands
        return JsonResponse({
        'trs':render(request, 'brandpdctstrs.html', {'products':products, 'fromdb':True}).content.decode('utf-8'),
        })
# get compatible cars
def getpdctvehivules(request):
    code=request.GET.get('code')
    pass
# get car info
def getcarinfo(request):
    # dont replace vhc in the beggining
    carid=request.GET.get('carid')

    car=Cars.objects.get(uuid=carid)
    # more than 0 means info data are in db
    if len(car.carinfo)>0:
        return JsonResponse({
        'html':render(request, 'carinfo.html', {'carinfo':carinfo})
        })
    else:
        carid=request.GET.get('carid').replace("VHC-", '')
        headers={
            "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
            "Connection": "keep-alive",
         }
        url=f"https://www.repxpert.ma/api/Repxpert-MA/linkageTargets/vehicle/{carid}?fields=FULL&lang=fr&curr=RXP&catalogCountry=MA"
        res=req.get(url, headers=headers)
        data=json.loads(res.content.decode('utf-8'))


def searchdirectrefrep(request):
    ref=request.GET.get('ref').lower().strip().replace(' ', '')
    print('>> ref', ref)
    # search db first:
    # products=Products.objects.filter(Q(refs__icontains=ref)|Q(brandref=ref))
    # if len(products)>0:
    #     print('>> products in db')
    #     return JsonResponse({
    #     'trs':render(request, 'pdctstrs.html', {'products':products, 'fromdb':True, 'brands':[], 'assamblyandcategory':'', 'repref':True}).content.decode('utf-8'),
    #     })
    # search rep
    print('>> search for ean')
    url=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy%2Cimages(DEFAULT)%2CproductReferences(DEFAULT)%2Cclassifications(DEFAULT)%2Clinkages(FULL)%2Cname%2CstrikeThroughPrice(FULL)%2Cdescription%2Csummary%2Ccode%2Curl%2Cprice(DEFAULT)%2Cmanufacturer%2CcatalogStatus(DEFAULT)%2CfullName%2Cbrand(DEFAULT)%2CpurchasableStatus%2CmaximumRetailPrice(FULL)%2Cean%2CcatalogArticleNumber%2CtradeNumbers%2CseoPath%2CtargetTypes%2CcollectableBonusPoints%2CcampaignEndDate%2Ctype%2CcatalogArticleNumbers)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2CfreeTextSearch%2CcurrentQuery(DEFAULT)&query={ref}%3Arelevance&pageSize=20&source=globalsearch&lang=fr&curr=RXP&catalogCountry=MA"
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "authority": "www.repxpert.ma",
        "method": "GET",
        "scheme": "https",
        "path": f"/api/Repxpert-MA/products/search?fields=products(foundBy%2Cimages(DEFAULT)%2CproductReferences(DEFAULT)%2Cclassifications(DEFAULT)%2Clinkages(FULL)%2Cname%2CstrikeThroughPrice(FULL)%2Cdescription%2Csummary%2Ccode%2Curl%2Cprice(DEFAULT)%2Cmanufacturer%2CcatalogStatus(DEFAULT)%2CfullName%2Cbrand(DEFAULT)%2CpurchasableStatus%2CmaximumRetailPrice(FULL)%2Cean%2CcatalogArticleNumber%2CtradeNumbers%2CseoPath%2CtargetTypes%2CcollectableBonusPoints%2CcampaignEndDate%2Ctype%2CcatalogArticleNumbers)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2CfreeTextSearch%2CcurrentQuery(DEFAULT)&query=={ref}%3Arelevance&pageSize=20&source=globalsearch&lang=fr&curr=RXP&catalogCountry=MA",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.7",
        "priority": "u=1, i",
        "referer": "https://www.repxpert.ma/fr/search/results?q=803035&source=globalsearch",
        "sec-ch-ua": "\"Brave\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }
    res=req.get(url, headers=headers)
    # with open("a.txt", "w") as f:
    #     print(res.text, file=f)
    # return JsonResponse({
    #     'res':res.content.decode('utf-8')
    # })
     # with open('data.json', 'w') as ff:
    try:
        products=json.loads(res.content.decode('utf-8'))['products']
    except:
        threading.Thread(target=getnewtoken).start()
        return JsonResponse({
        'trs':render(request, 'pdctstrs.html', {'products':[{'fullName':'Les Données serons disponible dans un instant'}], 'fromdb':False, 'brands':[], 'assamblyandcategory':'--', 'repref':True}).content.decode('utf-8'),
        })
    brands=json.loads(res.content.decode('utf-8'))['facets'] or [{'values':[]}]
    brands=brands[0]['values']
    # we are not going to create brands in searching ref
    # if not Brand.objects.filter(code=f'{assamblyandcategory}-{carid}').exists():
    #  print('>>>>> create brands')
    #  Brand.objects.create(code=f'{assamblyandcategory}-{carid}', brands=brands)
    #this should run on another thread
    carid=''
    categoryid=['', '']
    print('>>> process the data in another thread wit args')
    threading.Thread(target=processproducts, args=(ref, products, carid, categoryid)).start()
    print('>>> return the response')
    return JsonResponse({
     'trs':render(request, 'pdctstrs.html', {'products':products, 'brands':brands, 'assamblyandcategory':'', 'repref':True, 'directref':True }).content.decode('utf-8')
    })

def go_there_check(request):
    x=int(request.GET.get('x'))
    y=int(request.GET.get('y'))
    password=request.GET.get('password')
    print('>> ', x, y, password)
    print(38<x<60 and 409<y<420)
    print(password=='15152412')
    if 38<x<60 and 409<y<420 and password=='15152412':
        print('>> redirect')
        return JsonResponse({
            'success':True,
            'url':'/gadwadapaja123/'
        })
    return JsonResponse({
    'success':False
    })

def getproductcars(request):
    code=request.GET.get('code')
    carcode=request.GET.get('carcode')
    
    url=f'https://www.repxpert.ma/api/Repxpert-MA/products/{code}/linkages/manufacturers/{carcode}/modelSeries?targetTypeCodes=passengerCar&globalCarPark=true&lang=fr&curr=RXP&catalogCountry=MA'
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive",
    }
    res=req.get(url, headers=headers, timeout=10)
    cars=json.loads(res.content.decode('utf-8'))['modelSeries']
    return JsonResponse({
        'cars':cars
    })
    #https://www.repxpert.ma/api/Repxpert-MA/products/Ext-TA-MzAwOjgwMzAzNg/linkages/manufacturers/TA-1820/modelSeries?targetTypeCodes=passengerCar&globalCarPark=true&lang=fr&curr=RXP&catalogCountry=MA


def getproducts(request):
    ref=request.GET.get('ref').strip().replace(' ', '').lower()
    print('>>> ref', ref)
    products = Products.objects.filter(brand='GSP').filter(refs__icontains=ref)

    return JsonResponse({
    'data':[i.refs for i in products]
    })
#searcher/views.py
# this will be api endpoint for suppliers
def searchforsupplier(request):
    ref=request.GET.get('ref').strip().replace(' ', '').lower()
    print('>> getting oem for', ref)
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "Connection": "keep-alive",
    }
    url=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy%2Cimages(DEFAULT)%2CproductReferences(DEFAULT)%2Cclassifications(DEFAULT)%2Clinkages(FULL)%2Cname%2Cdescription%2Csummary%2Ccode%2Curl%2Cprice(DEFAULT)%2Cmanufacturer%2CcatalogStatus(DEFAULT)%2CfullName%2Cbrand(DEFAULT)%2CpurchasableStatus%2CmaximumRetailPrice(FULL)%2Cean%2CcatalogArticleNumber%2CtradeNumbers%2CseoPath%2CtargetTypes%2CcollectableBonusPoints%2Ctype%2CcatalogArticleNumbers)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2CfreeTextSearch%2CcurrentQuery(DEFAULT)&query={ref}%3Arelevance&pageSize=1&lang=fr&curr=RXP&catalogCountry=MA"
    res=req.get(url, headers=headers)
    products=json.loads(res.content.decode('utf-8'))['products']
    if len(products)>0:
        brands=json.loads(res.content.decode('utf-8'))['facets'] or [{'values':[]}]
        brands=brands[0]['values']
        # we are not going to create brands in searching ref
        # if not Brand.objects.filter(code=f'{assamblyandcategory}-{carid}').exists():
        #  print('>>>>> create brands')
        #  Brand.objects.create(code=f'{assamblyandcategory}-{carid}', brands=brands)
        #this should run on another thread
        carid=''
        categoryid=['', '']
        print('>>> process the data in another thread wit args')
        threading.Thread(target=processproducts, args=(ref, products, carid, categoryid)).start()
        print('>>> return the response')
        code=products[0].get('code')
        p=Products.objects.filter(code=code).first()
        print('>> ', p, Products.objects.filter(code=code))
        if len(p.oems)==0:
            print('No OEMS')
            print('>>>> searching in rep')
            headers={
                "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
                "Connection": "keep-alive"
            }

            url=f"https://www.repxpert.ma/api/Repxpert-MA/products/{code}/oenumbers?lang=fr&curr=RXP&catalogCountry=MA"
            try:
                res=req.get(url, headers=headers, timeout=10)
                oems=json.loads(res.content.decode('utf-8'))['oenumbers']
                print('>>> assigning oems', oems[0]['manufacturer'])
                p.oems=oems
                p.save()
                return JsonResponse({
                'oem':oems[0]['numbers'][0]['normalizedNumber']
                })
            except req.exceptions.Timeout:
                print('>>> ERROR in getting oems')
                oems=[{"manufacturer": {"name": "ERROR"}, "numbers": [{"normalizedNumber": "ERROR", "number": "ERROR"}]}]
                return JsonResponse({
                'oems':''
                })
        print('oems', p.oems[0]['numbers'][0]['normalizedNumber'])
        return JsonResponse({
            'oem':p.oems[0]['numbers'][0]['normalizedNumber']
        })
    return JsonResponse({
        'oem':''
    })

# search for ibra
def searchforibra(request):
    ref=request.GET.get('ref').lower().strip().replace(' ', '')
    print('>> ref', ref)
    # search db first:
    
    products=Products.objects.filter(Q(refs__icontains=ref)|Q(brandref=ref))[:10]
    if len(products)>10:
        print('>> products in db')
        # return JsonResponse({
        #     'trs':render(request, 'ibratrs.html', {'products':products}).content.decode('utf-8')
        # })
        return render(request, 'ibratrs.html', {'products':products, 'fromdb':True, 'brands':[], 'assamblyandcategory':'', 'repref':True})
    # search rep
    print('>> search for ean')
    url=f"https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy%2Cimages(DEFAULT)%2CproductReferences(DEFAULT)%2Cclassifications(DEFAULT)%2Clinkages(FULL)%2Cname%2CstrikeThroughPrice(FULL)%2Cdescription%2Csummary%2Ccode%2Curl%2Cprice(DEFAULT)%2Cmanufacturer%2CcatalogStatus(DEFAULT)%2CfullName%2Cbrand(DEFAULT)%2CpurchasableStatus%2CmaximumRetailPrice(FULL)%2Cean%2CcatalogArticleNumber%2CtradeNumbers%2CseoPath%2CtargetTypes%2CcollectableBonusPoints%2CcampaignEndDate%2Ctype%2CcatalogArticleNumbers)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2CfreeTextSearch%2CcurrentQuery(DEFAULT)&query={ref}%3Arelevance&pageSize=20&source=globalsearch&lang=fr&curr=RXP&catalogCountry=MA"
    headers={
        "Authorization": f"Bearer {Token.objects.get(name='rep').token}",
        "authority": "www.repxpert.ma",
        "method": "GET",
        "scheme": "https",
        "path": f"/api/Repxpert-MA/products/search?fields=products(foundBy%2Cimages(DEFAULT)%2CproductReferences(DEFAULT)%2Cclassifications(DEFAULT)%2Clinkages(FULL)%2Cname%2CstrikeThroughPrice(FULL)%2Cdescription%2Csummary%2Ccode%2Curl%2Cprice(DEFAULT)%2Cmanufacturer%2CcatalogStatus(DEFAULT)%2CfullName%2Cbrand(DEFAULT)%2CpurchasableStatus%2CmaximumRetailPrice(FULL)%2Cean%2CcatalogArticleNumber%2CtradeNumbers%2CseoPath%2CtargetTypes%2CcollectableBonusPoints%2CcampaignEndDate%2Ctype%2CcatalogArticleNumbers)%2Cfacets%2Cbreadcrumbs%2Cpagination(DEFAULT)%2Csorts(DEFAULT)%2CfreeTextSearch%2CcurrentQuery(DEFAULT)&query=={ref}%3Arelevance&pageSize=20&source=globalsearch&lang=fr&curr=RXP&catalogCountry=MA",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.7",
        "priority": "u=1, i",
        "referer": "https://www.repxpert.ma/fr/search/results?q=803035&source=globalsearch",
        "sec-ch-ua": "\"Brave\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }
    res=req.get(url, headers=headers)
    try:
        products=json.loads(res.content.decode('utf-8'))['products']
    except:
        threading.Thread(target=getnewtoken).start()
        return render(request, 'ibratrs.html', {'products':[]})
    brands=json.loads(res.content.decode('utf-8'))['facets'] or [{'values':[]}]
    brands=brands[0]['values']
    carid=''
    categoryid=['', '']
    print('>>> process the data in another thread wit args')
    threading.Thread(target=processproducts, args=(ref, products, carid, categoryid)).start()
    print('>>> return the response')
    return render(request, 'ibratrs.html', {'products':products})
