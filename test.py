import requests as req
import json
# tecaliance='https://webservice.tecalliance.services/pegasus-3-0/services/TecdocToCatDLB.jsonEndpoint?articleCountry= ""&dataSupplierIds= []&filterQueries= ["(dataSupplierId NOT IN (4978,4982))"]&genericArticleIds= []&includeAccessoryArticles= false&includeAll= false&includeArticleCriteria= true&includeArticleLogisticsCriteria= false&includeArticleText= true&includeComparableNumbers= true&includeCriteriaFacets= false&includeDataSupplierFacets=false&includeGTINs=true&includeGenericArticleFacets=true&includeGenericArticles=true&includeImages=true&includeLinkages=true&includeLinks=false&includeMisc=true&includeOEMNumbers=false&includePDFs=false&includePartsListArticles=false&includePrices=false&includeReplacedByArticles=true&includeReplacesArticles=true&includeTradeNumbers=true&lang="qa"&linkagesPerPage=100&page=1&perPage=0&provider=2080&searchMatchType="prefix_or_suffix"&searchQuery="GDP400"&searchType=10'
# url="https://api-aftermarket.schaeffler.de/authorizationserver/oauth/token?catalogCountry=MA"
# payload={
#     'grant_type':'password',
#     'scope':'',
#     'client_id':'repxpert-spa',
#     'client_secret':'cSsWzdAmRCTa5LXmfSwsJc3hJbfFWhAKhpDGp1VN',
#     'username':'brahimcatalog7@gmail.com',
#     'password':'Catalog7+'
# }
# res=req.post(url, data=payload)
# print(json.loads(res.text)['access_token'])

code="Ext-TA-MjczOjMzNDU4Nw"
headers={
"Authorization": f"Bearer N0y6UC2l52KMm_y-e7w0RRlfdJg",
"Connection": "keep-alive",
}
url=f'https://www.repxpert.ma/api/Repxpert-MA/products/{code}/linkages/manufacturers?targetTypeCodes=passengerCar&globalCarPark=true&fields=FULL&lang=fr&curr=RXP&catalogCountry=MA'
print('>> start req')
res=req.post(url, headers=headers)
print('>> end req')
with open('res.txt', 'w') as f:
    f.write(res.text)
print(res)
    

