import database

db = database.DatabaseLITE("API/app/shop.db")
db.insert_product("Vaporesso xros 4 mini", "vaporesso4mini", 1899.00, True)
db.insert_product("Vaporesso xros 4", "vaporessoxros4", 2100.00, False)
db.close()