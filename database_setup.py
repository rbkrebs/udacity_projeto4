#!/usr/bin/env python


import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class UserLogged(Base):
    """
    Registered user information is stored in db
    to easily manage permissions
    """
    __tablename__ = 'userlogged'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    """docstring for Category"""

    __tablename__ = 'category'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)

    # To send JSON objects in a serializable format
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'id': self.id,
            'Items': []
        }


class CategoryItem(Base):
    """docstring for CategoryItem"""

    __tablename__ = 'category_item'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref=backref(
        "CategoryItem", cascade="all,delete"))

    # To send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
            'title': self.title,
            'id': self.id,
            'description': self.description,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
