from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from auth.auth import encrypt_password, verify_password
from auth.jwt_handler import sign_jwt

ENGINE = None

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    email = Column(String(100), primary_key=True)
    password = Column(String(100))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    @staticmethod
    def get_all_data():

        session = get_session()
        sql_query_data = session.query(User)

        all_data = [[row.email, row.password] for row in sql_query_data]

        return all_data

    def get_object(self):
        return {'email': self.email}

    def create_user(self):
        self.password = encrypt_password(self.password)
        try:
            insert_data(self)
        except IntegrityError:
            raise Exception('User with this email already registered')

    @staticmethod
    def get_user(email):
        session = get_session()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        return user

    def login_user(self):
        session = get_session()
        user = session.query(User).filter_by(email=self.email).first()
        session.close()
        if user is None:
            raise Exception('Invalid email or password')

        is_password_valid = verify_password(self.password, user.password)
        if is_password_valid:
            token = sign_jwt(user.email)
            return token['access_token']

        raise Exception('Invalid email or password')


class Actor(Base):
    __tablename__ = 'actor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    photo = Column(String(500))
    shows = relationship('Show', secondary='link')

    def __init__(self, name, photo):
        self.name = name
        self.photo = photo

    def get_object(self):
        return {'id': self.id, 'name': self.name, 'photo': self.photo}

    @staticmethod
    def get_actors(actors):

        actor_list = []
        for actor in actors:
            actor_list.append(actor.get_object())

        return actor_list

    @staticmethod
    def get_actor(id):
        session = get_session()
        actor = session.query(Actor).filter_by(id=id).first()
        session.close()
        if actor is None:
            return {}
        return actor

    @staticmethod
    def delete_actor(id):
        session = get_session()
        session.query(Actor).filter_by(id=id).delete()
        session.commit()
        session.close()

    @staticmethod
    def get_all_data():
        session = get_session()
        sql_query_data = session.query(Actor)

        all_data = [{'id': row.id, 'name': row.name, 'photo': row.photo} for row in sql_query_data]

        return all_data

    def create_actor(self):
        try:
            insert_data(self)
        except IntegrityError:
            raise Exception('Database Integrity Error')


class Show(Base):
    __tablename__ = 'show'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50))
    release_year = Column(String(50))
    episode_numbers = Column(String(50))
    image = Column(String(200))
    description = Column(String(1000))
    director = Column(String(50))
    writer = Column(String(50))
    genre = Column(String(100))
    streaming_platform = Column(String(100))
    actors = relationship('Actor', secondary='link')

    def __init__(self, title, release_year, episode_numbers, image, description, director, writer, genre, streaming_platform):
        self.title = title
        self.release_year = release_year
        self.episode_numbers = episode_numbers
        self.image = image
        self.description = description
        self.director = director
        self.writer = writer
        self.genre = genre
        self.streaming_platform = streaming_platform

    @staticmethod
    def get_all_data():
        session = get_session()
        sql_query_data = session.query(Show)

        all_data = [[{'id': row.id, 'title': row.title, 'release_year': row.release_year, 'director': row.director,
                      'episode_numbers': row.episode_numbers, 'image': row.image, 'description': row.description,
                      'writer': row.writer, 'genre': row.genre, 'streaming_platform': row.streaming_platform,
                      'actors': Actor.get_actors(row.actors)}] for row in sql_query_data]

        return all_data

    def create_show(self):
        try:
            insert_data(self)
        except IntegrityError:
            raise Exception('Database Integrity Error')

    @staticmethod
    def delete_show(id):
        session = get_session()
        session.query(Show).filter_by(id=id).delete()
        session.commit()
        session.close()


class Link(Base):
    __tablename__ = 'link'
    actor_id = Column(
        Integer,
        ForeignKey('actor.id'),
        primary_key=True)

    show_id = Column(
        Integer,
        ForeignKey('show.id'),
        primary_key=True)


def get_connection_string():
    return f'sqlite:///database.db'


def get_engine():
    global ENGINE

    if ENGINE is None:
        ENGINE = create_engine(get_connection_string(), echo=True)

    return ENGINE


def get_session() -> sessionmaker():
    session_maker = sessionmaker(bind=get_engine())
    session = scoped_session(session_maker)
    return session()


def insert_bulk_data(objects: list):
    session = get_session()

    session.bulk_save_objects(objects)
    session.commit()
    session.close()


def insert_data(data):
    session = get_session()
    session.add(data)
    session.commit()
    session.close()


try:
    Base.metadata.create_all(get_engine())
except exc.SQLAlchemyError as sql_error:
    print(str(sql_error))
