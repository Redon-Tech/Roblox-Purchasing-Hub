"""
    File: /lib/utils/database.py
    Usage: Used to do anything to databasses
    Info: The only reason this exists is so if you want to change databases you can.
    Note: MongoDB is diffrent then most other databases so make sure to update everythin in here and in the cogs.
    Documentation: MongoDB: https://pymongo.readthedocs.io/en/stable/index.html / https://www.w3schools.com/python/python_mongodb_getstarted.asp
"""
from pprint import pprint
import json
import certifi

with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

if config["database"]["type"].lower() == "sqlalchemy":
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.engine import URL
    from sqlalchemy.orm import declarative_base, sessionmaker
    from urllib.parse import quote_plus

    connection_url = URL.create(
        drivername=config["database"]["sqlalchemy"]["connector"],
        username=config["database"]["sqlalchemy"]["username"],
        password=quote_plus(config["database"]["sqlalchemy"]["password"]),
        host=config["database"]["sqlalchemy"]["host"],
        port=config["database"]["sqlalchemy"]["port"],
        database=config["database"]["sqlalchemy"]["database"],
    )

    engine = create_engine(connection_url)

    Base = declarative_base()

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)
        description = Column(String(255), nullable=False)
        price = Column(Integer, nullable=False)
        attachments = Column(String(10000))

        def __repr__(self) -> str:
            return f"Product(id={self.id}, name={self.name}, description={self.description}, price={self.price}, attachments={self.attachments})"

    class User:
        __table__ = "users"

        id = Column(Integer, primary_key=True)
        discordid = Column(Integer, nullable=False)
        username = Column(String(20), nullable=False)
        purchases = Column(String(10000))

        def __repr__(self) -> str:
            return f"User(id={self.id}, discordid={self.discordid}, username={self.username}, purchases={self.purchases})"

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    db = Session()

    def get_filter_by_args(model_class, dic_args: dict):
        filters = []
        for key, value in dic_args.items():  # type: str, any
            if key == "_id":
                key = "id"
            if key.endswith("___min"):
                key = key[:-6]
                filters.append(getattr(model_class, key) > value)
            elif key.endswith("___max"):
                key = key[:-6]
                filters.append(getattr(model_class, key) < value)
            elif key.endswith("__min"):
                key = key[:-5]
                filters.append(getattr(model_class, key) >= value)
            elif key.endswith("__max"):
                key = key[:-5]
                filters.append(getattr(model_class, key) <= value)
            else:
                filters.append(getattr(model_class, key) == value)
        return filters

    def insert(data, info):
        if data == "products":
            attachments = json.dumps(info["attachments"])
            product = Product(
                name=info["name"],
                description=info["description"],
                price=info["price"],
                attachments=attachments,
            )
            db.add(product)
            db.commit()
            return info
        elif data == "users":
            purchases = json.dumps(info["purchases"])
            user = User(
                id=info["_id"],
                discordid=info["discordid"],
                username=info["username"],
                purchases=purchases,
            )
            db.add(user)
            db.commit()
            return info

    def insertmany(data, info):
        if data == "products":
            additions = []
            for product in info:
                attachments = json.dumps(product["attachments"])
                product = Product(
                    name=product["name"],
                    description=product["description"],
                    price=product["price"],
                    attachments=attachments,
                )
                additions.append(product)

            db.add_all(additions)
            db.commit()
            return info
        elif data == "users":
            additions = []
            for user in info:
                purchases = json.dumps(user["purchases"])
                user = User(
                    id=user["_id"],
                    discordid=user["discordid"],
                    username=user["username"],
                    purchases=purchases,
                )
                additions.append(user)

            db.add_all(additions)
            db.commit()
            return info

    def update(data, query, info):
        filters = get_filter_by_args(Product, query)
        if data == "products":
            product = db.query(Product).filter(*filters).first()
            new_info = info["$set"]
            product.name = new_info["name"]
            product.description = new_info["description"]
            product.price = new_info["price"]
            product.attachments = json.dumps(new_info["attachments"])
            db.commit()
            return info
        elif data == "users":
            user = db.query(User).filter(*filters).first()
            new_info = info["$set"]
            if new_info["discordid"]:
                user.discordid = new_info["discordid"]
            elif new_info["purchases"]:
                user.username = new_info["purchases"]
            db.commit()
            return info

    def updatemany(data, query, info):
        filters = get_filter_by_args(Product, query)
        if data == "products":
            for product in info:
                product = db.query(Product).filter(*filters).first()
                new_info = product["$set"]
                product.name = new_info["name"]
                product.description = new_info["description"]
                product.price = new_info["price"]
                product.attachments = json.dumps(new_info["attachments"])

            db.commit()
            return info
        elif data == "users":
            for user in info:
                user = db.query(User).filter(*filters).first()
                new_info = user["$set"]
                if new_info["discordid"]:
                    user.discordid = new_info["discordid"]
                elif new_info["purchases"]:
                    user.username = new_info["purchases"]

            db.commit()
            return info

    def delete(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            product = db.query(Product).filter(*filters).first()
            db.delete(product)
            db.commit()
            return True
        elif data == "users":
            filters = get_filter_by_args(User, query)
            user = db.query(User).filter(*filters).first()
            db.delete(user)
            db.commit()
            return True

    def deletemany(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            products = db.query(Product).filter(*filters).all()
            for product in products:
                db.delete(product)
            db.commit()
            return True
        elif data == "users":
            filters = get_filter_by_args(User, query)
            users = db.query(User).filter(*filters).all()
            for user in users:
                db.delete(user)
            db.commit()
            return True

    def find(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            data = db.query(Product).filter(*filters).all()
            send = []
            for data in data:
                new_data = {
                    "_id": data.id,
                    "name": data.name,
                    "description": data.description,
                    "price": data.price,
                    "attachments": json.loads(data.attachments),
                }
                send.append(new_data)
            return send
        elif data == "users":
            filters = get_filter_by_args(User, query)
            data = db.query(User).filter(*filters).all()
            send = []
            for data in data:
                new_data = {
                    "_id": data.id,
                    "discordid": data.discordid,
                    "username": data.username,
                    "purchases": json.loads(data.purchases),
                }
                send.append(new_data)
            return send

    def find_one(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            data = db.query(Product).filter(*filters).first()
            send = {
                "_id": data.id,
                "name": data.name,
                "description": data.description,
                "price": data.price,
                "attachments": json.loads(data.attachments),
            }
            print(send, data, filters)
            return send
        elif data == "users":
            filters = get_filter_by_args(User, query)
            data = db.query(User).filter(*filters).first()
            send = {
                "_id": data.id,
                "discordid": data.discordid,
                "username": data.username,
                "purchases": json.loads(data.purchases),
            }
            print(send, data, filters)
            return send


if config["database"]["type"].lower() == "mongodb":
    from pymongo import MongoClient

    client = MongoClient(
        config["database"]["mongodb"]["url"], tlsCAFile=certifi.where()
    )  # Some systems may not require "tlsCAFile"
    db = client.data

    def insert(data, info):
        col = db[data]
        result = col.insert_one(info)
        return result

    def insertmany(data, info):
        col = db[data]
        results = col.insert_many(info)
        return results

    def update(data, query, info):
        col = db[data]
        result = col.update_one(query, info)
        return result

    def updatemany(data, query, info):
        col = db[data]
        results = col.update_many(query, info)
        return results

    def delete(data, query):
        col = db[data]
        result = col.delete_one(query)
        return result

    def deletemany(data, query):
        col = db[data]
        results = col.delete_many(query)
        return results

    def find(data, query):
        col = db[data]
        results = col.find(query)
        return results

    def find_one(data, query):
        col = db[data]
        results = col.find_one(query)
        return results


database = db  # For any other functions not here use this
