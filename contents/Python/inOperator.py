import time

str1 = "test"
str2 = "automationandtesting"

if str1 in str2:
    # do something here
    print("str1 is in str2")
else:
    print("str1 is NOT in str2")

if str2.find(str1) != -1:
    print("str1 is in str2 using find()")
else:
    print("str1 is NOT in str2 using find()")

if str2.__contains__(str1):
    print("str1 is in str2 using __contains__()")
else:
    print("str1 is NOT in str2 using __contains__()")

# requests example

def handleRequest(data: dict) -> str:
    requests = {} # key: user, value: requests

    # count = requests[data['auth']] # returns the number of requests in the last hour
    # if count >= 100:
    #     return "Rate limit exceeded"
    # else:
    #     # process the request
    #     print("Processing request since user is under the 100 rate limit")
    #     count += 1
    #     requests[data['auth']] = count
    #     return "Request processed successfully"

    now = time.time()
    oneHourAgo = now - 3600

    if data['auth']['api_key'] not in requests:
        requests[data['auth']['api_key']] = []
    
    recent_requests = [t for t in requests[data['auth']['api_key']] if t > oneHourAgo]
    requests[data['auth']['api_key']] = recent_requests

    if len(requests[data['auth']['api_key']]) >= 100:
        return "Rate limit exceeded"
    else:
        print("Processing request since user is under the 100 rate limit")
        requests[data['auth']['api_key']].append(now)
        return "Request processed successfully"

data = {
    'auth': {
        'api_key': '12345'
    },
    'request': {
        'data': 'some_data'
    }
}