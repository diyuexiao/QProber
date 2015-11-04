import urllib2
import base64

bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3afifa.com%20premiership%27&$top=10&$format=Atom'
#Provide your account key here
accountKey = 'QXWZenjIChRK55ligQ1BjQEJBEEsHXvZ1b4E3PGUkJY='

accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}
req = urllib2.Request(bingUrl, headers = headers)
response = urllib2.urlopen(req)
content = response.read()
#content contains the xml/json response from Bing. 
return content