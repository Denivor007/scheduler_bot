from utils.db_api.db_gino import TimedBaseModel,BaseModel
from sqlalchemy import Column, Integer, Sequence, BigInteger, String, TIMESTAMP, sql, Time
import datetime


class User(BaseModel):
    __tablename__ = 'users'
    id = Column(BigInteger, Sequence("user_id_seq"), primary_key=True)
    user_id = Column(BigInteger)
    fullname = Column(String(100))
    username = Column(String(100))
    city = Column(String(100))
    morning = Column(Time)
    active = Column(Integer, default=1)

    def __str__(self):
        return f"id = {self.id}\n" \
               f"user_id = {self.user_id}\n" \
               f"fullname = {self.fullname}\n" \
               f"username = {self.username}\n" \
               f"city = {self.city}\n" \
               f"morning = {self.morning}\n" \
               f"active = {self.active}\n"

    query: sql.select

