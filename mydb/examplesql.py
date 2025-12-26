from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, select
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine, func, update
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class tabl:
    __tablename__ = "name of table"
    #поля 
    id = Column(Integer)
    f"""
    свойство {Column}
    тип intege string ...
    default - по умолчанию
    primarykey - первичный ключ
    unique — уникальность
    foreignkey - данные связи с другой таблицей
    {ForeignKey('importtable.key')}
    {Column(Integer,)}
    {
        relationship(
            "classname"
        )
        }
    """

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    messages = relationship("Message")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

class Manager:
    def __init__(self, database_url="sqlite:///{file.db}"):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

engine = create_engine("database_url", echo=False)
session = sessionmaker(bind=engine)
session().query(User).filter_by(id=1).first/all  #get element

    