from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_manager import Category, Base, Item

# This is a sample setup file is fill the db with sample data
#
# Hai Vo 2017/08/09

engine = create_engine('sqlite:///categoryProject.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

category1 = Category(name="Soccer")

session.add(category1)
session.commit()

category2 = Category(name="Basketball")

session.add(category2)
session.commit()

category3 = Category(name="Baseball")

session.add(category3)
session.commit()

category4 = Category(name="Frisbee")

session.add(category4)
session.commit()

category5 = Category(name="Snowboarding")

session.add(category5)
session.commit()

category6 = Category(name="Rock Climbing")

session.add(category6)
session.commit()

category7 = Category(name="Foosball")

session.add(category7)
session.commit()

category8 = Category(name="Skating")

session.add(category8)
session.commit()

category9 = Category(name="Hockey")

session.add(category9)
session.commit()

description1 = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Aenean sit amet justo quis velit maximus auctor nec vitae nisi. Integer
eros nulla, elementum a nunc at, efficitur dapibus mauris. Phasellus
porttitor lobortis lacus, viverra sollicitudin urna venenatis vitae. Cras
cursus nulla id metus elementum, non aliquet tellus dignissim. Donec
dictum urna leo, dignissim"""
item1 = Item(name="Stick", description=description1, category_id=category9.id)

session.add(item1)
session.commit()

item2 = Item(name="Google", description=description1, category_id=category5.id)

session.add(item2)
session.commit()

item3 = Item(name="Snowboard",
             description=description1,
             category_id=category5.id)

session.add(item3)
session.commit()

item4 = Item(name="Two shinguards",
             description=description1,
             category_id=category1.id)

session.add(item4)
session.commit()

item5 = Item(name="Shinguards",
             description=description1,
             category_id=category1.id)

session.add(item5)
session.commit()

item6 = Item(name="Frisbee",
             description=description1,
             category_id=category4.id)

session.add(item6)
session.commit()

item7 = Item(name="Bat", description=description1, category_id=category3.id)

session.add(item7)
session.commit()

item8 = Item(name="Jersey", description=description1, category_id=category1.id)

session.add(item8)
session.commit()

item9 = Item(name="Soccer Cleats",
             description=description1,
             category_id=category1.id)

session.add(item9)
session.commit()
