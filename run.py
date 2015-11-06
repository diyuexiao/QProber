from APITest import request_bing_result

siteInput = "yahoo.com"
queryInput = "avi file"

webTotal = request_bing_result(siteInput, queryInput)
import pdb; pdb.set_trace()
print webTotal
