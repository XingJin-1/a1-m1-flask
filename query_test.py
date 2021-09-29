import requests

BASE = "http://131.130.37.62:9211/"
#BASE =  "http://127.0.0.1:9211/"
#response = requests.get(BASE + "asnyc_test")

# response = requests.get(BASE + "cpee/0")
# print(response.json())


#response = requests.delete(BASE + "cpee/1")
#print(response)
#input()
"""
data = [{"url": "https://cpee.org/flow/engine/57161/callbacks/111/", 'processed':1},
        {"url": "https://cpee.org/flow/engine/57184/callbacks/222/", 'processed':1},
        {"url": "https://cpee.org/flow/engine/57161/callbacks/cf19a0f7628b335a81b75d571171babd/", 'processed':0},
        {"url": "https://cpee.org/flow/engine/57184/callbacks/6adec1334d5de1b3d81b8506b1c795e0/", 'processed':0}
]

for i in range(len(data)):
    response = requests.put(BASE + "cpee/" + str(i), data[i])
    print(response.json())

input()


response = requests.post(BASE + "cpee/3", {"processed": 150})
"""
#response = requests.get(BASE + "asnyc_return")
#print(response.json())

for i in range(4, 7):   
    response = requests.delete(BASE + "cpee/" + str(i))