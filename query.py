import requests

BASE = "http://127.0.0.1:5000/"

# data = [{"likes":78, "name": 'Xing', "views":100000},
#         {"likes":10000, "name": 'Joe', "views":80000},
#         {"likes":35, "name": 'Tim', "views":2000}
# ]

# for i in range(len(data)):
#     response = requests.put(BASE + "video/" + str(i), data[i])
#     print(response.json())


# # input()
# # response = requests.delete(BASE + "video/0")
# # print(response)

# input()
# response = requests.get(BASE + "video/2")
# print(response.json())

# input()
# response = requests.patch(BASE + "video/2", {"views":99})
# print(response.json())

# input()
# response = requests.get(BASE + "video/2")
# print(response.json())

data = [{"name": 'Xing', "balance":100000.045},
        {"name": 'Joe', "balance":80000.05},
        {"name": 'Tim', "balance":2000.0}
]

for i in range(len(data)):
    response = requests.put(BASE + "customer/" + str(i), data[i])
    print(response.json())


# input()
# response = requests.delete(BASE + "video/0")
# print(response)

input()
response = requests.get(BASE + "customer/2")
print(response.json())

input()
response = requests.patch(BASE + "customer/2", {"balance":99})
print(response.json())

input()
response = requests.get(BASE + "customer/2")
print(response.json())