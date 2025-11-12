from .models import Products, Token
import uuid
import requests as req
import json
from random import choice
bot_token='7468917121:AAESp5hLp1wFX6gURO8vEMRQwApooniFP1I'
chat_id='-4527459647'
# send telegram message
def sendtelegram(message):
    send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = req.get(send_message_url, params=params)
    # Check if the message was sent successfully
    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print('Failed to send message:', response.text)

def processproducts(ref, products, carid, categoryid):
    unicode = str(uuid.uuid4())
    for index, i in enumerate(products):
        
        try:
            p=Products.objects.get(code=i['code'])
            print('>>> product exists')
            
            cars=p.car_codes or []
            if not carid=='' and not carid in cars:
                print("adding carid in processpdcts")

                cars.append(carid)
            p.car_codes=cars
            refs=p.refs or []
            if not ref=='' and not ref in refs:
                print("adding refd in processpdcts")
                print('>> add ref ', ref)
                refs.append(ref)
            p.refs=refs
            if len(p.commoncode)==0:
                p.commoncode.append(unicode)
            if not categoryid[1]=="":
                print("adding assambly and ctg in processpdcts")
                p.assemblyGroups=categoryid[1]
                p.categoryid=categoryid[0]
            p.save()
        except Exception as e:
            print(">> ERR in gettig the product", e, '>> creating..')
            try:
                thisref=i.get('catalogArticleNumber').lower().replace(' ', '')
                pr=Products.objects.create(
                #commoncode=[unicode],
                car_codes=[carid],
                features=i.get('classifications', [{'features':''}])[0].get('features'),
                fullName=i.get('fullName'),
                brand=i.get('brand', '').get('name').strip(),
                brandref=thisref,
                #refs=[i.get('catalogArticleNumber', '')], #RR520
                code=i.get('code', ''),
                image=i.get('images', [{'url':''}])[0].get('url'),
                categoryid=categoryid[0],
                assemblyGroups=categoryid[1],
                ean=i.get('ean', ''))
                if not ref=="":
                    if ref==thisref:
                        pr.refs=[thisref]
                    else:
                        pr.refs=[thisref, ref]
                else:
                    pr.refs=[thisref]
                pr.save()
            except Exception as e:
                print('>>>> ERR in creating product: ', e, index)

def processbrandproducts(ref, products, brandid, categoryid, carid):
    unicode = str(uuid.uuid4())
    for index, i in enumerate(products):
        try:
            p=Products.objects.get(code=i['code'])

            # assign the brandid
            p.brandid=brandid
            # if not ref=="":
            #     print('>> assign ref in processbrandpdcts')
            #     p.brandref=ref
            if not categoryid[1]=="":
                print('>> assign assambly and cyg in processbrandpdcts')
                p.assemblyGroups=categoryid[1]
                p.categoryid=categoryid[0]
            cars=p.car_codes or []
            if not carid in cars:
                print('>> adding carid in processbrandpdcts')
                cars.append(carid)
            p.car_codes=cars
            refs=p.refs or []
            if not ref in refs:
                if not ref=="":
                    print('>> add ref to product id', ref, p.id)
                    refs.append(ref)
            p.refs=refs
            if len(p.commoncode)==0:
                p.commoncode.append(unicode)
            p.save()
        except Exception as e:
            print(">> ERR in gettig the product")
            try:
                print(">> trying to create product")
                thisref=i['catalogArticleNumber'].lower().replace(' ', '')
                pr=Products.objects.create(
                commoncode=[unicode],
                car_codes=[carid],
                features=i.get('classifications', [{'features':''}])[0].get('features'),
                fullName=i.get('fullName'),
                brand=i.get('brand', '').get('name').strip(),
                brandref=thisref,
                brandid=brandid,

                code=i.get('code', ''),
                image=i.get('images', [{'url':''}])[0].get('url'),
                categoryid=categoryid[0],
                assemblyGroups=categoryid[1],
                ean=i.get('ean', ''))
                if ref==thisref:
                    pr.refs=[thisref],
                else:
                    pr.refs=[thisref, ref]
                pr.save()
            except Exception as e:
                print('>>>> ERR in creating product: ', e, index)

def processindirectref(code, brandid, ref, brand, features, searchedref, name, image_url):
    try:
        p=Products.objects.get(code=code)
        print('>>> product exists')
        p.brandid=brandid
        #p.brandref=ref
        p.brand=brand
        p.features=features
        refs=p.refs # it needs to be populated all ready, since it's in db da means it has refs RR520
        print('>> refs before',refs)
        if searchedref not in refs:
            refs.append(searchedref)
            print('>> refs after',refs)
        p.refs=refs
        p.save()
    except Exception as e:

        t=Products.objects.filter(code=code)
        for i in t:
            if i.brandid==None:
                i.delete()
        print('>>> product not exists, creating...',e, code)
        pr = Products.objects.create(
            car_codes=[],
            features=features,
            fullName=name,
            brand=brand,
            brandref=ref,
            brandid=brandid,
            code=code,
            image=image_url,
            assemblyGroups='',
            ean='',
        )
        if searchedref==ref:
            pr.refs=[ref]
        else:
            pr.refs=[ref, searchedref]
        pr.save()

def processbranddirectref(code, brandid, ref, brand, searchedref, features, name, image_url):
    try:
        p=Products.objects.get(code=code)
        print('>>> product exists')
        p.brandid=brandid
        p.brandref=ref
        p.brand=brand
        refs=p.refs # it needs to be populated all ready, since it's in db da means it has refs RR520
        if searchedref not in refs:
            refs.append(searchedref)
        p.refs=refs
        p.save()
    except Exception as e:


        print('>>> product not exists, creating..., ', e)
        pr = Products.objects.create(
            car_codes=[],
            features=features,
            fullName=name,
            brand=brand,
            brandref=ref,

            code=code,
            image=image_url,
            assemblyGroups='',
            ean='',
        )
        if searchedref == refs:
            refs=[searchedref]
        else:
            refs=[searchedref, ref]
        pr.refs=refs
        pr.save()

def getnewtoken():
    mails=['nourpiecesauto@gmail.com:nOUR2025+', 'abde.lwahed@outlook.com:Gadwad123.']
    url="https://www.repxpert.ma/authorizationserver/oauth/token?catalogCountry=MA"
    credentials=choice(mails).split(':')
    print('>>>> ', credentials)
    payload={
        'grant_type':'password',
        'scope':'',
        'client_id':'repxpert-spa',
        'client_secret':'cSsWzdAmRCTa5LXmfSwsJc3hJbfFWhAKhpDGp1VN',
        'username':credentials[0],
        'password':credentials[1]
    }
    print('>>> getting token')
    headers = {
        "authority": "www.repxpert.ma",
        "method": "POST",
        "path": "/authorizationserver/oauth/token?catalogCountry=MA",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6",
        "content-length": "162",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "cookiesession1=678A3E10511CE2F7851E341FD84C491A; OptanonAlertBoxClosed=2025-06-11T12:13:45.968Z; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Nov+06+2025+11%3A39%3A30+GMT%2B0100+(UTC%2B01%3A00)&version=202403.1.0&isIABGlobal=false&hosts=&consentId=82c80ad4-f37b-49a6-9e96-647c6ee47116&interactionCount=3&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0&geolocation=MA%3B09&AwaitingReconsent=false&browserGpcFlag=0&isAnonUser=1",
        "origin": "https://www.repxpert.ma",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }
    res=req.post(url, data=payload, headers=headers)
    token=json.loads(res.text)['access_token']
    reptoken=Token.objects.get(name='rep')
    reptoken.token=token
    reptoken.save()
