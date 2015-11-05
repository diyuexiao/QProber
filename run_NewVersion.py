from APITest import request_bing_result

siteInput = "yahoo.com"
queryInput = "avi file"

searched_info = {}
searched_info = request_bing_result(siteInput, queryInput)

print searched_info[queryInput].web_count
print searched_info[queryInput].url_set