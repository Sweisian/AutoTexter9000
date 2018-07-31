import pymongo

myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")

mydb = myclient["pioneers_of_interactive_entertainment_nu"]

#print(myclient.databases_names())
print(mydb.collection_names())

mycol = mydb["users"]





# mydict = { "name": "Ryan", "address": "Apple st 652"}
#
# #x = mycol.insert_one(mydict)
#
#
# mylist = [
#   {"name": "John", "address": "Highway 37"},
#   {"name": "Peter", "address": "Lowstreet 27"},
#   {"name": "Amy", "address": "Apple st 652"},
#   {"name": "Hannah", "address": "Mountain 21"},
#   {"name": "Michael", "address": "Valley 345"},
#   {"name": "Sandy", "address": "Ocean blvd 2"},
#   {"name": "Betty", "address": "Green Grass 1"},
#   {"name": "Richard", "address": "Sky st 331"},
#   {"name": "Susan", "address": "One way 98"},
#   { "name": "Vicky", "address": "Yellow Garden 2"},
#   { "name": "Ben", "address": "Park Lane 38"},
#   { "name": "William", "address": "Central st 954"},
#   { "name": "Chuck", "address": "Main Road 989"},
#   { "name": "Viola", "address": "Sideway 1633"}
# ]
#
# #x = mycol.insert_many(mylist)
#
# # for x in mycol.find():
# #   print(x)
#
# for x in mycol.find({},{ "name": 1 }):
#   print(x)
