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
    from sqlalchemy import create_engine, Column, Integer, String, Table
    from sqlalchemy.orm import declarative_base, sessionmaker

    engine = create_engine(config["database"]["sqlalchemy"]["url"])

    Base = declarative_base()

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True)
        name = Column(String(50), Unique=True, nullable=False)
        description = Column(String(255), nullable=False)
        price = Column(Integer, nullable=False)
        attachments = Column(Table)

        def __repr__(self) -> str:
            return f"Product(id={self.id}, name={self.name}, description={self.description}, price={self.price}, attachments={self.attachments})"

    class User:
        __table__ = "users"

        id = Column(Integer, primary_key=True)
        discordid = Column(Integer, nullable=False)
        username = Column(String(20), nullable=False)
        purchases = Column(Table)

        def __repr__(self) -> str:
            return f"User(id={self.id}, discordid={self.discordid}, username={self.username}, purchases={self.purchases})"

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    db = Session()

    def get_filter_by_args(model_class, dic_args: dict):
        filters = []
        for key, value in dic_args.items():  # type: str, any
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
            product = Product(
                name=info["name"],
                description=info["description"],
                price=info["price"],
                attachments=info["attachments"],
            )
            db.add(product)
            db.commit()
            return product
        elif data == "users":
            user = User(
                id=info["_id"],
                discordid=info["discordid"],
                username=info["username"],
                purchases=info["purchases"],
            )
            db.add(user)
            db.commit()
            return user

    def insertmany(data, info):
        pass

    def update(data, query, info):
        pass

    def updatemany(data, query, info):
        pass

    def delete(data, query):
        pass

    def deletemany(data, query):
        pass

    def find(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            return db.query(Product).filter(*filters)
        elif data == "users":
            filters = get_filter_by_args(User, query)
            return db.query(User).filter(*filters)

    def find_one(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            return db.query(Product).filter(*filters).first()
        elif data == "users":
            filters = get_filter_by_args(User, query)
            return db.query(User).filter(*filters).first()


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
