import requests

#BASE = "http://131.130.37.62:9211/"
BASE =  "http://127.0.0.1:9211/"
#response = requests.get(BASE + "asnyc_test")

# response = requests.get(BASE + "cpee/0")
# print(response.json())


#data = [{"url": "http://127.0.0.1:9211/"}
#]

#response = requests.put(BASE + "cpee/0" , data[0])
#print(response.json())

response = requests.get(BASE + "asnyc_return")
print(response.json())
