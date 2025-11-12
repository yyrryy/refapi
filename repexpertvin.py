import requests as req
import json
from bs4 import BeautifulSoup
from html_to_json import convert
# vin url
import base64
# Create your views here.
#repref: ref results from rep
#directref: ref result from azshp
def encode_to_base64(input_string):
    # Encode the input string to Base64
    encoded_bytes = base64.b64encode(input_string.encode('utf-8'))
    # Convert bytes to a string and remove padding characters ('=')
    encoded_str = encoded_bytes.decode('utf-8').rstrip('=')
    return encoded_str
headers={
    "Authorization": "Bearer 3FigWMQB19C9NiosC66fc5hc1ss",
    "Connection": "keep-alive",
  }

url1="https://www.repxpert.ma/api/Repxpert-MA/vehicleKeySystems/vin/vehicles/WDF63970313182801?globalCarPark=true&fields=DEFAULT,modelSeries(DEFAULT)&vehicleType=passengerCar&lang=fr&curr=RXP&catalogCountry=MA"

#car parts url
url="https://www.repxpert.ma/fr/catalog?linkageTarget=TA-23465&targetType=vehicle&category=100012"

url3="https://www.repxpert.ma/api/Repxpert-MA/products/search?fields=products(foundBy,images(DEFAULT),productReferences(DEFAULT),classifications(DEFAULT),linkages(FULL),name,description,summary,code,url,price(DEFAULT),manufacturer,catalogStatus(DEFAULT),fullName,brand(DEFAULT),purchasableStatus,maximumRetailPrice(FULL),ean,catalogArticleNumber,tradeNumbers,seoPath,targetTypes,collectableBonusPoints,type,catalogArticleNumbers),facets,breadcrumbs,pagination(DEFAULT),sorts(DEFAULT),freeTextSearch,currentQuery(DEFAULT)&query=::linkages.target:Vehicle%21TA-684:assemblyGroups:100340&categoryCode=100011&lang=fr&curr=RXP&catalogCountry=MA"
#res=req.get(url3, headers=headers)
# print(len(json.loads(res.content.decode('utf-8'))['products']))
headers={
"authorization":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MjMwMjcwNDcsImhvc3QiOiJhci1kZW1vLnRyYWRlc29mdC5wcm8iLCJhcGlLZXkiOiJUV1MtMUExQjFENTktRkE0NS00OTVFLTk4RjYtOURGRkI2MDI4ODhBIiwiYXBpUGF0aCI6Imh0dHBzOi8vYXBpLnBhcnRzLWNhdGFsb2dzLmNvbS92MSIsImlwIjoiMTU0LjE0NC4yNTMuNSIsImgiOiJiOWNiZDhkYzEzZjE5ZjllN2ViODU0ZjQ3MmJmYTI3NCJ9.dBJT73XuYJdARpGB2ONWmXcffRoGQUpOZe-3DIQG__I"
}

vin2="https://api.parts-catalogs.com/v1/car/info?q=WDF63970313182801"

url="https://www.trodo.fr/rest/V1/catalogsearch/result/0?q=32-N94-A&searchby=number&is_ajax=true&customer_group_id=undefined&currency=EUR&list-type=list&country=MA"

headers = {
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

cookies = {
    '__zlcmid': '1JlmPgpFfLui7PR',
    'amcookie_allowed': '1',
    'amcookie_disallowed': 'recently_viewed_product%2Crecently_viewed_product_previous%2Crecently_compared_product%2Crecently_compared_product_previous%2C_ga%2C_gid%2C_gat',
    'form_key': 'Ut0As6gvOf9jx2Qj',
    'private_content_version': '5d0f414e8f6238883c83f6e9ac5306a9',
    'partfinder_1': 'null',
    'partfinder_url_1': 'null',
    'PHPSESSID': 'hukictjktpmop88bqgaeops79u',
    'X-Magento-Vary': 'b629c646a54e82e1601c6692de4907b9e673d5e9ebfaab738d774e6e2838c233',
    'cf_clearance': 'UEkA8sGbZSfczvZb1aUcslRYCYfqtWsNeY_oM55Cfnk-1723639959-1.0.1.1-sbu7FzSfIlkNCpfQ4e5IepnIgwA7dSTzyRx7.4Rmofm3j9TiCbupBNGzDDaxoiQy6Em0pqucFR2cymOnDfCvlA',
    '__kla_id': 'eyJjaWQiOiJZMkpsWVdaaVlqWXRNRFV6TmkwMFpETXdMV0ZrTnpRdFpHVTBZakUzTVRRMllXSTMiLCIkcmVmZXJyZXIiOnsidHMiOjE3MDQ5NzA5OTEsInZhbHVlIjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJmaXJzdF9wYWdlIjoiaHR0cHM6Ly93d3cudHJvZG8uZnIvIn0sIiRsYXN0X3JlZmVycmVyIjp7InRzIjoxNzIzNjM5NzQ2LCJ2YWx1ZSI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS8iLCJmaXJzdF9wYWdlIjoiaHR0cHM6Ly93d3cudHJvZG8uZnIvY3VzdG9tZXIvYWNjb3VudCJ9fQ=='
}


# Step 1: Create a session object
session = req.Session()
#
# session.headers.update({
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#     'Cookie': '__zlcmid=1JlmPgpFfLui7PR; amcookie_allowed=1; amcookie_disallowed=recently_viewed_product,recently_viewed_product_previous,recently_compared_product,recently_compared_product_previous,_ga,_gid,_gat; form_key=Ut0As6gvOf9jx2Qj; private_content_version=5d0f414e8f6238883c83f6e9ac5306a9; partfinder_1=null; partfinder_url_1=null; PHPSESSID=hukictjktpmop88bqgaeops79u; form_key=Ut0As6gvOf9jx2Qj; X-Magento-Vary=b629c646a54e82e1601c6692de4907b9e673d5e9ebfaab738d774e6e2838c233; cf_clearance=UEkA8sGbZSfczvZb1aUcslRYCYfqtWsNeY_oM55Cfnk-1723639959-1.0.1.1-sbu7FzSfIlkNCpfQ4e5IepnIgwA7dSTzyRx7.4Rmofm3j9TiCbupBNGzDDaxoiQy6Em0pqucFR2cymOnDfCvlA; __kla_id=eyJjaWQiOiJZMkpsWVdaaVlqWXRNRFV6TmkwMFpETXdMV0ZrTnpRdFpHVTBZakUzTVRRMllXSTMiLCIkcmVmZXJyZXIiOnsidHMiOjE3MDQ5NzA5OTEsInZhbHVlIjoiaHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8iLCJmaXJzdF9wYWdlIjoiaHR0cHM6Ly93d3cudHJvZG8uZnIvIn0sIiRsYXN0X3JlZmVycmVyIjp7InRzIjoxNzIzNjM5NzQ2LCJ2YWx1ZSI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS8iLCJmaXJzdF9wYWdlIjoiaHR0cHM6Ly93d3cudHJvZG8uZnIvY3VzdG9tZXIvYWNjb3VudCJ9fQ=='
# })
# Step 2: Go to the first URL
first_url = 'https://olejeobchod.cz/vyhledavani?search=803036'
#response = session.get(first_url)

# Optional: Check the response and capture parameters (if needed)
# For example, you might want to extract some data from the response:
# some_data = response.json().get('some_key')

# Step 3: Use the same session to go to another page within the same website
second_url = 'https://shop.az-parts.net/index.php?q=gdb400&page=search'
#https://olejeobchod.cz/vyhledavani?search=803036

print('>> getting')
#res = req.get(second_url, headers=headers)

#with open('data.html', 'w', encoding='utf-8') as ff:
#     print(res.text.split('<div class="container-fluid">')[2], file=ff)
#html_content=res.text.split('<div class="container-fluid">')[2]
# with open('data.html', 'w', encoding='utf-8') as ff:
#      print(res.text.split('<div class="sidebarLayout__main__content ">')[1], file=ff)
def element_to_json(element):
    if isinstance(element, str):
        return element.strip()

    tag_dict = {"tag": element.name}
    if element.attrs:
        tag_dict["attributes"] = element.attrs

    children = [element_to_json(child) for child in element.children if child.name or child.strip()]
    if children:
        tag_dict["children"] = children

    return tag_dict

soup = BeautifulSoup(open('data.html', 'r'), 'html.parser')


# Initialize an empty list to hold the product data
products = []

# Find all product cards
product_cards = soup.find_all('div', class_='card-prod')
# Iterate over each product card and extract data
print('>>> getting')
for index, card in enumerate(product_cards[:2]):
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
    for li in card.find_all('li'):
        specs = {"featureValues": [{"value": ""}], "name": ""}
        print('>>> li', li)
        value = li.text.split(':')[0].strip()
        key = li.find('span').text.strip()
        #print('>>> name, value li', name, value)
        specs['featureValues'][0]['value']=value
        specs['name']=key
        features.append(specs)
    brand=card.find('h5').text.split('-')[0]
    # check if ptoduct exists

    # Extract image URLs
    product['image']=image_url
    product['code']=code
    product['brandref']=ref

    # Extract product name
    product['fullName'] = name
    product['features'] = features
    product['brand'] = brand
    product['pdctid'] = card.find('input', {'name': f'artid{index}'})['value']
    products.append(product)
# Output the extracted data as JSON
print('>>> Saving')
with open('data.json', 'w') as ff:
    print(json.dumps(products, indent=2, ensure_ascii=False), file=ff)
print('>>> Saved')


# Correct the padding and decode
#decoded_strings_corrected = [base64.b64decode(add_padding(s)).decode('utf-8') for s in encoded_strings]
#print(decoded_strings_corrected)
