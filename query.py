import requests

# scp /Users/jxxxxx/Desktop/askUser/askuser_interface.php lin.xing@lehre.bpm.in.tum.de:public_html
#scp /Users/jxxxxx/Desktop/askUser/askuser_interface.php lin.xing@lehre.bpm.in.tum.de:public_html
#scp /Users/jxxxxx/Desktop/BPM/model/xing-a1-m1-subprocess-upload.xml lin.xing@lehre.bpm.in.tum.de:public_html
#scp /Users/jxxxxx/PyProject/a1-m1-flask/sendsomething.php lin.xing@lehre.bpm.in.tum.de:public_html:async
#scp -r /Users/jxxxxx/PyProject/a1-m1-flask ghibli@toydaria.wst.univie.ac.at:m1-2509
#BASE = "http://127.0.0.1:5000/"
#BASE = "http://131.130.37.62:9211/"
BASE = "http://127.0.0.1:9211/"

#data = [{"name": 'Xing', "balance": 100000.045},
#        {"name": 'Joe', "balance": 80000.05},
#        {"name": 'Tim', "balance": 2000.0}
#]
#for i in range(len(data)):
#        response = requests.put(BASE + "customer/" + str(i), data[i])
#        print(response.json())


#data = [{"id": 0, "url": "http://127.0.0.1:9211/"}
#]

#response = requests.put(BASE + "cpee/0" , data[0])
#print(response.json())


# input()
# response = requests.delete(BASE + "customers/0")
# print(response)

# input()
# response = requests.get(BASE + "customers/2")
# print(response.json())

# input()
# response = requests.post(BASE + "customers/0", {"balance": 200.0})
# print(response.json())

# input()
# response = requests.get(BASE + "customers/0")
# print(response.json())

data = [{"name": 'Bike', "price":100.05, "description": 'a bike', "stock":10},
         {"name": 'Keyboard', "price":3.0, "description": 'an Keyboard', "stock":15},
         {"name": 'Basketball', "price":80.50, "description":"a basketball", "stock":30},
 ]
for i in range(len(data)):
        response = requests.put(BASE + "item/" + str(i), data[i])
        print(response.json())


#data = [{"id_customer": 0, "id_item": 1, "price": 150.05},
#        {"id_customer": 0, "id_item": 2, "price": 180.50},
#]

#for i in range(len(data)):
#    var1 = str(data[i]['id_customer'])
#    var2 = str(data[i]['id_item'])
#    url_t = BASE + "transaction/" + var1 + "/" + var2
    #response = requests.put(BASE + "transaction/" + str(data[i]['id_customer']) + "/" + str(data[i]['id_item']), data[i])
#    response = requests.post(url_t, data[i])
#    print(response.json())

# response = requests.delete(BASE + "transactions/0/2")
# response = requests.delete(BASE + "transactions/0/0")
# response = requests.delete(BASE + "transaction/1/0")
# response = requests.delete(BASE + "transaction/1/1")
#print(response)


#curl -d '{"balance": 100}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/customer/0
