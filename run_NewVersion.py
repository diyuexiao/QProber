from APITest import request_bing_result

siteInput = "yahoo.com"
queryInput = "avi file"

a = request_bing_result(siteInput, queryInput)
b = request_bing_result(siteInput, "avi")

print a.web_count
print a.url_set
print b.web_count
print b.url_set
