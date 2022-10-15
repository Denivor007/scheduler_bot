from utils.db_api.db_gino import TimedBaseModel, BaseModel
from sqlalchemy import Column, Integer, Sequence, BigInteger, String, TIMESTAMP, sql


class Task(BaseModel):
    __tablename__ = 'tasks'
    id = Column(BigInteger, Sequence("task_id_seq"), primary_key=True)
    user_id = Column(BigInteger)
    datetime = Column(TIMESTAMP)
    remind_for = Column(BigInteger, default=30)
    name = Column(String(33))
    description = Column(String)
    mode = Column(String, default="none")

    query: sql.select

    def get_datetime_str(self):
        return self.datetime.strftime("%d.%m.%Y  %H:%M")

    def __str__(self):
        return f"id = {self.id}\n" \
               f"user_id = {self.user_id}\n" \
               f"datetime = {self.datetime}\n" \
               f"remind for = {self.remind_for}\n" \
               f"name = {self.name}\n" \
               f"description = {self.description}\n" \
               f"mode = {self.mode}\n"


