import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

###############################################################
# Sqlalchemy orm model file
# this is the model file
# Hai Vo 2017/08/09
###############################################################

Base = declarative_base()


# the category table
# name String(80)
# id Integer
class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


# the user table
# name String
# email String
# id Integer
class User(Base):
    __tablename__ = 'user'
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


# the item table
# id Integer
# name String
# description String
# category_id (id -> category table)
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id
        }


engine = create_engine('sqlite:///categoryProject.db')

Base.metadata.create_all(engine)
