from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel
import requests

# Инициализация FastAPI
app = FastAPI()

# Инициализация соединения с БД через SQLAlchemy 
DATABASE_URL = "postgresql://admin:admin@localhost:5432/muhob1207"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#Создаем модель Question (таблица с названием questions)
class Question(Base):
    #Определяем название таблицы
    __tablename__ = "questions"
    #Ниже список колонок данной таблицы. Созданы в соответствии с ответом публичного АПИ
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    value = Column(Integer) 
    airdate = Column(DateTime)  
    created_at = Column(DateTime) 
    updated_at = Column(DateTime) 
    game_id = Column(Integer)  
    invalid_count = Column(Integer, nullable=True) 
    category_id = Column(Integer)  
    category_title = Column(String) 
    category_created_at = Column(DateTime) 
    category_updated_at = Column(DateTime)  
    category_clues_count = Column(Integer)  
    #Это поле добавил от себя. Дата создания записи в нашей БД
    local_created_date = Column(DateTime, server_default=func.now())


#Создаем таблицу questions если ее еще нет в БД
Base.metadata.create_all(bind=engine)


#Определяем параметры, которые надо передавать в POST запросе к нашему эндпоинту. В данном случае это только количество вопросов 
class QuestionRequest(BaseModel):
    questions_num: int



# Создаем сам эндпоинт
@app.post("/get_questions/")
def get_question(question_request: QuestionRequest):
    db = SessionLocal()
    #Делаем запрос в публичное АПИ, указывая переданное количество вопросов, и получаем ответ
    response = requests.get(f"https://jservice.io/api/random?count={question_request.questions_num}")
    #В данном случае ответ - это список вопросов
    question_data = response.json()

    # Проходим по каждому вопросу в списке
    for q in question_data:
        # Смотрим, есть ли уже в нашей БД вопрсов с таким id
        existing_question = db.query(Question).filter(Question.id == q["id"]).first()
        # Если такого вопроса еще нет, то создаем новую запись в БД
        if not existing_question:
            # Заполняем поля согласно пришедшим данным
            new_question = Question(id=q['id'], question=q["question"], answer=q["answer"], value=q['value'], airdate=q['airdate'],
                                    created_at=q['created_at'], updated_at=q['updated_at'], game_id=q['game_id'],
                                    invalid_count=q['invalid_count'],category_id=q['category']['id'], category_title=q['category']['title'],
                                    category_created_at=q['category']['created_at'], category_updated_at=q['category']['updated_at'],
                                    category_clues_count = q['category']['clues_count'])
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
        else:
            # В случае если такой вопрос уже найден, то начинаем цикл.
            # Запрашиваем новый вопрос из публичного АПИ, пока не получим такой вопрос, id которого еще нет в нашей БД
            while True:
                # Получаем новый вопрос из публичного АПИ
                new_response = requests.get(f"https://jservice.io/api/random?count=1")
                # Берем первый элемент в списке (в списке - всего один элемент)
                new_question_data = new_response.json()[0]
                # Смотрим, есть ли в БД такой вопрос
                new_existing_question = db.query(Question).filter(Question.id == new_question_data["id"]).first()

                # Если такого вопроса в БД нет то создаем 
                if not new_existing_question:
                    another_new_question = Question(id=new_question_data['id'], question=new_question_data["question"], answer=new_question_data["answer"], value=new_question_data['value'], airdate=new_question_data['airdate'],
                                    created_at=new_question_data['created_at'], updated_at=new_question_data['updated_at'], game_id=new_question_data['game_id'],
                                    invalid_count=new_question_data['invalid_count'],category_id=new_question_data['category']['id'], category_title=new_question_data['category']['title'],
                                    category_created_at=new_question_data['category']['created_at'], category_updated_at=new_question_data['category']['updated_at'],
                                    category_clues_count = new_question_data['category']['clues_count'])
                    
                    db.add(another_new_question)
                    db.commit()
                    db.refresh(another_new_question)
                    # Прерываем цикл while и возвращаемся к основному циклу for
                    break
                else:
                    # Если же и этот вопрос есть в БД, то продолжаем цикл while
                    continue

        
    #Получаем последний по дате создания вопрос из БД
    latest_question = db.query(Question).order_by(Question.local_created_date.desc()).first()

    #Отключаемся от БД
    db.close()

    print('everything successful')

    # Если последний вопрос есть, то возвращаем его данные
    if latest_question:
        return {'id':latest_question.id,
                'question':latest_question.question,
                'answer':latest_question.answer,
                'created_at':latest_question.created_at,
                'local_created_date':latest_question.local_created_date}
    #Если последнего вопроса нет, то возвращаем пустой объект
    else:
        return {}
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
