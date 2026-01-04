from sqlalchemy import create_engine, Column, String, Boolean, Text, CheckConstraint, Integer,DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime, timedelta

engine = create_engine('sqlite:///Databases/Inventives.db')
Base = declarative_base()

class Feedbacks(Base):
    __tablename__ = 'Inventives'
    id = Column(Integer,primary_key=True)
    emailrecive = Column(String)
    emailsent = Column(String)
    typeinventive = Column(String)
    time = Column(DateTime, default=datetime.now())
    
    def __repr__(self):
        data = {
            "emailrecive": self.emailrecive,
            "emailsent": self.emailsent,
            "typeinventive": self.typeinventive,
            "time": self.time
        }
        return json.dumps(data, ensure_ascii=False)
    
Base.metadata.create_all(engine)

class Feedback_Manager:
    def __init__(self, database_url='sqlite:///Databases/Inventives.db'):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def add_Inventive(self, emailrecive, emailsent, typeinventive):
        session = self.Session()
        try:
            if session.query(Feedbacks).filter(Feedbacks.email == email).first():
                return {"error": f"Пользователь с email {email} уже существует"}
            
            # Создаем пользователя
            new_user = Feedbacks(
                email=email,
                why=why,
                when=datetime.now()
            )
            
            session.add(new_user)
            session.commit()
            
            return self._feedback_to_dict(new_user)
            
        except Exception as e:
            session.rollback()
            print("error adding")
            return {"error": str(e)}
        finally:
            session.close()