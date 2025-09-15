from core.db.models.test import Product
from core.db.session import DB


config_db = DB("sqlite:///test.db")

db = config_db.init()

print(db.get(Product, 1).title)
#

db.close()
