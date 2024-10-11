from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Text, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
import os
import sys
from sqlalchemy.sql import func

# Use the new import location for declarative_base
Base = declarative_base()

# Association tables for many-to-many relationships
user_favorite_characters = Table('user_favorite_characters', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('character_id', Integer, ForeignKey('characters.id'))
)

user_favorite_planets = Table('user_favorite_planets', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('planet_id', Integer, ForeignKey('planets.id'))
)

user_favorite_vehicles = Table('user_favorite_vehicles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('vehicle_id', Integer, ForeignKey('vehicles.id'))
)

character_films = Table('character_films', Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id')),
    Column('film_id', Integer, ForeignKey('films.id'))
)

planet_films = Table('planet_films', Base.metadata,
    Column('planet_id', Integer, ForeignKey('planets.id')),
    Column('film_id', Integer, ForeignKey('films.id'))
)

vehicle_films = Table('vehicle_films', Base.metadata,
    Column('vehicle_id', Integer, ForeignKey('vehicles.id')),
    Column('film_id', Integer, ForeignKey('films.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    favorite_characters = relationship("Character", secondary=user_favorite_characters, back_populates="favorited_by")
    favorite_planets = relationship("Planet", secondary=user_favorite_planets, back_populates="favorited_by")
    favorite_vehicles = relationship("Vehicle", secondary=user_favorite_vehicles, back_populates="favorited_by")
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50))
    birth_year = Column(String(20))
    gender = Column(String(20))
    height = Column(Integer)
    mass = Column(Integer)
    home_planet_id = Column(Integer, ForeignKey('planets.id'))

    home_planet = relationship("Planet", back_populates="residents")
    favorited_by = relationship("User", secondary=user_favorite_characters, back_populates="favorite_characters")
    films = relationship("Film", secondary=character_films, back_populates="characters")

class Planet(Base):
    __tablename__ = 'planets'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    climate = Column(String(50))
    terrain = Column(String(50))
    population = Column(Integer)
    diameter = Column(Integer)

    residents = relationship("Character", back_populates="home_planet")
    favorited_by = relationship("User", secondary=user_favorite_planets, back_populates="favorite_planets")
    films = relationship("Film", secondary=planet_films, back_populates="planets")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    model = Column(String(100))
    manufacturer = Column(String(100))
    cost_in_credits = Column(Integer)
    length = Column(Float)
    max_atmosphering_speed = Column(Integer)
    crew = Column(Integer)
    passengers = Column(Integer)
    vehicle_class = Column(String(50))

    favorited_by = relationship("User", secondary=user_favorite_vehicles, back_populates="favorite_vehicles")
    films = relationship("Film", secondary=vehicle_films, back_populates="vehicles")

class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    episode_id = Column(Integer)
    opening_crawl = Column(Text)
    director = Column(String(100))
    producer = Column(String(100))
    release_date = Column(DateTime)

    characters = relationship("Character", secondary=character_films, back_populates="films")
    planets = relationship("Planet", secondary=planet_films, back_populates="films")
    vehicles = relationship("Vehicle", secondary=vehicle_films, back_populates="films")

class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    author_id = Column(Integer, ForeignKey('users.id'))
    category = Column(String(50))
    tags = Column(String(200))

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    author_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('blog_posts.id'))

    author = relationship("User", back_populates="comments")
    post = relationship("BlogPost", back_populates="comments")

# Update the diagram generation part
if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagram.png')
    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass
    
    try:
        from sqlalchemy_schemadisplay import create_schema_graph
        from sqlalchemy import MetaData
        
        # Create an engine (this won't actually connect to a database)
        engine = create_engine('sqlite:///:memory:')
        
        # Create the schema
        Base.metadata.create_all(engine)
        
        # Create the graph
        graph = create_schema_graph(metadata=Base.metadata,
                                    show_datatypes=False,
                                    show_indexes=False,
                                    rankdir='LR',
                                    concentrate=False,
                                    engine=engine)
        graph.write_png(output_path)
        print(f"diagram.png generated successfully at {output_path}!")
    except ImportError:
        print("Error: Could not import sqlalchemy_schemadisplay.")
        print("Please install it using: pip install sqlalchemy_schemadisplay")
        print("You may also need to install: pip install pydot")
        print("And on Ubuntu/Debian: sudo apt-get install graphviz")
        sys.exit(1)
