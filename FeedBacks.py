from sqlalchemy import create_engine, Column, String, Boolean, Text, CheckConstraint, Integer,DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime, timedelta

engine = create_engine('sqlite:///Why_delete.db')
Base = declarative_base()

class Feedbacks(Base):
    __tablename__ = 'FeedBacks'
    
    email = Column(String(255), primary_key=True)
    why = Column(String(2048))
    when = Column(DateTime, default=None)
    
    __table_args__ = (
        CheckConstraint('LENGTH(why) <= 2048', name='about_length_check'),
    )
    
    def __repr__(self):
        data = {
            "email": self.email,
            "why": self.why,
            "when": self.when,
        }
        return json.dumps(data, ensure_ascii=False)
    
# Создаем таблицу
Base.metadata.create_all(engine)

class Feedback_Manager:
    def __init__(self, database_url='sqlite:///Why_delete.db'):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def _feedback_to_dict(self, user):
        """Конвертирует объект User в словарь"""
        if not user:
            return None

        return {
            "email": user.email,
            "why": user.why,
            "when": user.when,
        }

    def get_all_feedbaks(self):
        """Получить всех пользователей как list of dict"""
        session = self.Session()
        try:
            users = session.query(Feedbacks).all()
            return [self._feedback_to_dict(user) for user in users]
        finally:
            session.close()

    def add_userFeedBack(self, email, why):
        session = self.Session()
        try:
            # Проверяем существование
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