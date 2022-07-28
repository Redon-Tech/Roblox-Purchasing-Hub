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
import codecs

with codecs.open(
    "./BOT/lib/bot/config.json", mode="r", encoding="UTF-8"
) as config_file:
    config = json.load(config_file)

if config["database"]["type"].lower() == "sqlalchemy":
    from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        String,
        BigInteger,
        DateTime,
        Text,
    )
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

    class Tag(Base):
        __tablename__ = "tags"

        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        color = Column(Text)
        textcolor = Column(Text)

        def __str__(self) -> str:
            return f"Tag(id={self.id}, name={self.name}, color={self.color})"

    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True)
        name = Column(String(50), nullable=False)
        description = Column(Text, nullable=False)
        price = Column(Integer, nullable=False)
        productid = Column(BigInteger, nullable=True)
        attachments = Column(Text)
        tags = Column(Text)
        purchases = Column(BigInteger, nullable=False, default=0)
        created = Column(DateTime, nullable=False)

        def __repr__(self) -> str:
            return f"Product(id={self.id}, name={self.name}, description={self.description}, price={self.price}, productid={self.productid}, attachments={self.attachments})"

    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True)
        discordid = Column(BigInteger)
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
            tags = json.dumps(info["tags"])
            product = Product(
                name=info["name"],
                description=info["description"],
                price=info["price"],
                productid=info["productid"],
                attachments=attachments,
                tags=tags,
                purchases=info["purchases"],
                created=info["created"],
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
        elif data == "tags":
            color = json.dumps(info["color"])
            textcolor = json.dumps(info["textcolor"])
            tag = Tag(
                name=info["name"],
                color=color,
                textcolor=textcolor,
            )
            db.add(tag)
            db.commit()
            return info

    def insertmany(data, info):
        if data == "products":
            additions = []
            for product in info:
                attachments = json.dumps(info["attachments"])
                tags = json.dumps(info["tags"])
                product = Product(
                    name=info["name"],
                    description=info["description"],
                    price=info["price"],
                    productid=info["productid"],
                    attachments=attachments,
                    tags=tags,
                    purchases=info["purchases"],
                    created=info["created"],
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
        elif data == "tags":
            additions = []
            for tag in info:
                color = json.dumps(info["color"])
                textcolor = json.dumps(info["textcolor"])
                tag = Tag(
                    name=info["name"],
                    color=color,
                    textcolor=textcolor,
                )
                additions.append(tag)

            db.add_all(additions)
            db.commit()
            return info

    def update(data, query, info):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            product = db.query(Product).filter(*filters).first()
            new_info = info["$set"]
            product.name = new_info["name"]
            product.description = new_info["description"]
            product.price = new_info["price"]
            product.productid = new_info["productid"]
            product.attachments = json.dumps(new_info["attachments"])
            product.tags = json.dumps(new_info["tags"])
            product.purchases = new_info["purchases"]
            db.commit()
            return info
        elif data == "users":
            filters = get_filter_by_args(User, query)
            user = db.query(User).filter(*filters).first()
            new_info = info["$set"]
            if "discordid" in new_info:
                user.discordid = new_info["discordid"]
            elif "purchases" in new_info:
                user.purchases = json.dumps(new_info["purchases"])
            db.commit()
            return info
        elif data == "tags":
            filters = get_filter_by_args(Tag, query)
            tag = db.query(Tag).filter(*filters).first()
            new_info = info["$set"]
            tag.name = new_info["name"]
            tag.color = json.dumps(new_info["color"])
            tag.textcolor = json.dumps(new_info["textcolor"])
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
                product.productid = new_info["productid"]
                product.attachments = json.dumps(new_info["attachments"])
                product.tags = json.dumps(new_info["tags"])
                product.purchases = new_info["purchases"]

            db.commit()
            return info
        elif data == "users":
            for user in info:
                user = db.query(User).filter(*filters).first()
                new_info = user["$set"]
            if "discordid" in new_info:
                user.discordid = new_info["discordid"]
            elif "purchases" in new_info:
                user.purchases = new_info["purchases"]

            db.commit()
            return info
        elif data == "tags":
            for tag in info:
                tag = db.query(Tag).filter(*filters).first()
                new_info = tag["$set"]
                tag.name = new_info["name"]
                tag.color = json.dumps(new_info["color"])
                tag.textcolor = json.dumps(new_info["textcolor"])

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
        elif data == "tags":
            filters = get_filter_by_args(Tag, query)
            tag = db.query(Tag).filter(*filters).first()
            db.delete(tag)
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
        elif data == "tags":
            filters = get_filter_by_args(Tag, query)
            tags = db.query(Tag).filter(*filters).all()
            for tag in tags:
                db.delete(tag)
            db.commit()
            return True

    def find(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            data = db.query(Product).filter(*filters).all()
            send = []
            for data in data:
                attachments = None
                tags = None
                if data.attachments:
                    attachments = json.loads(data.attachments)
                if data.tags:
                    tags = json.loads(data.tags)
                new_data = {
                    "_id": data.id,
                    "name": data.name,
                    "description": data.description,
                    "price": data.price,
                    "productid": data.productid,
                    "attachments": attachments or [],
                    "tags": tags or [],
                    "purchases": data.purchases,
                    "created": data.created,
                }
                send.append(new_data)
            return send
        elif data == "users":
            filters = get_filter_by_args(User, query)
            data = db.query(User).filter(*filters).all()
            send = []
            for data in data:
                try:
                    discordid = int(data.discordid)
                except Exception:
                    discordid = None
                purchases = None
                if data.purchases:
                    purchases = json.loads(data.purchases)
                new_data = {
                    "_id": data.id,
                    "discordid": discordid,
                    "username": data.username,
                    "purchases": purchases or [],
                }
                send.append(new_data)
            return send
        elif data == "tags":
            filters = get_filter_by_args(Tag, query)
            data = db.query(Tag).filter(*filters).all()
            send = []
            for data in data:
                color = None
                textcolor = None
                if data.color:
                    color = json.loads(data.color)
                if data.textcolor:
                    textcolor = json.loads(data.textcolor)
                new_data = {
                    "_id": data.id,
                    "name": data.name,
                    "color": color or [255, 255, 255],
                    "textcolor": textcolor or [0, 0, 0],
                }
                send.append(new_data)
            return send

    def find_one(data, query):
        if data == "products":
            filters = get_filter_by_args(Product, query)
            data = db.query(Product).filter(*filters).first()
            if data:
                attachments = None
                tags = None
                if data.attachments:
                    attachments = json.loads(data.attachments)
                if data.tags:
                    tags = json.loads(data.tags)
                send = {
                    "_id": data.id,
                    "name": data.name,
                    "description": data.description,
                    "price": data.price,
                    "productid": data.productid,
                    "attachments": attachments or [],
                    "tags": tags or [],
                    "purchases": data.purchases,
                    "created": data.created,
                }
            else:
                send = None
            return send
        elif data == "users":
            filters = get_filter_by_args(User, query)
            data = db.query(User).filter(*filters).first()
            if data:
                try:
                    discordid = int(data.discordid)
                except Exception:
                    discordid = None
                purchases = None
                if data.purchases:
                    purchases = json.loads(data.purchases)
                send = {
                    "_id": data.id,
                    "discordid": discordid,
                    "username": data.username,
                    "purchases": purchases or [],
                }
            else:
                send = None
            return send
        elif data == "tags":
            filters = get_filter_by_args(Tag, query)
            data = db.query(Tag).filter(*filters).first()
            if data:
                color = None
                textcolor = None
                if data.color:
                    color = json.loads(data.color)
                if data.textcolor:
                    textcolor = json.loads(data.textcolor)
                send = {
                    "_id": data.id,
                    "name": data.name,
                    "color": color or [255, 255, 255],
                    "textcolor": textcolor or [0, 0, 0],
                }
            else:
                send = None
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
