import http.client

conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "0044eead19mshb6e1c674366b8c7p1d8de1jsn18af8a6884ef",
    'x-rapidapi-host': "twitter241.p.rapidapi.com"
}

conn.request("GET", "/user-tweets?user=330262748&count=1", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

# ------------------------------------------------------

# print(data.decode("utf-8"))
# "id":"VXNlcjozMzAyNjI3NDg="
# rest ID; 330262748

# import http.client

# conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

# headers = {
#     'x-rapidapi-key': "0044eead19mshb6e1c674366b8c7p1d8de1jsn18af8a6884ef",
#     'x-rapidapi-host': "twitter241.p.rapidapi.com"
# }

# conn.request("GET", "/user?username=FabrizioRomano", headers=headers)

# res = conn.getresponse()
# data = res.read()

# print(data.decode("utf-8"))