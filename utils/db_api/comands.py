import asyncpg

from asyncpg import Connection
from aiogram import types, Bot
from utils.db_api.db_gino import *
import config

from utils.db_api.schemas.task import Task
from utils.db_api.schemas.user import User


async def create_pool():
    return await asyncpg.create_pool(
        user = config.PGUSER,
        password = config.PGPASSWORD,
        host = config.ip,
        database = 'gino'
    )

loop = asyncio.get_event_loop()
db_asyncpg = loop.run_until_complete(create_pool())


class DBCommands:
    pool: Connection = db_asyncpg
    GET_FIRST_TASK = "SELECT * FROM tasks WHERE datetime = (SELECT min(datetime) FROM tasks) AND user_id = $1"
    SET_CITY = "UPDATE users SET city = $2 WHERE user_id = $1;"
    SET_MORNING = "UPDATE users SET morning = $2 WHERE user_id = $1;"
    GET_TASKS = "SELECT * FROM tasks WHERE (datetime BETWEEN $1 AND $2) AND user_id = $3;"
    GET_TASKS_NWU = "SELECT * FROM tasks WHERE (datetime BETWEEN $1 AND $2);"
    DELETE_TASK = "DELETE FROM tasks WHERE id = $1;"
    GET_ALL_USERS = "SELECT * FROM users ORDER BY morning"

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.all()
        return user

    async def set_morning(self, user_id, morning):
        command = self.SET_MORNING
        result = await self.pool.fetch(command, user_id, morning)

    async def set_city(self, user_id, city):
        command = self.SET_CITY
        result = await self.pool.fetch(command, user_id, city)

    async def get_all_users(self):
        command = self.GET_ALL_USERS
        users = await self.pool.fetch(command)
        result = []
        for res in users:
            user = User()
            user.id = res[0]
            user.user_id = res[1]
            user.fullname = res[2]
            user.username = res[3]
            user.city = res[4]
            user.morning = res[5]
            result.append(user)
        return result

    async def add_new_user(self):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        try:
            new_user = User()
            new_user.user_id = user.id
            new_user.username = user.username
            new_user.fullname = user.full_name
            await new_user.create()
            return new_user
        except:
            print(f"SOME TROUBLE IN add_new_user() {user.id} {user.username} {user.full_name}")

    async def count_users(self):
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def count_tasks(self):
        total = await db.func.count(Task.id).gino.scalar()
        return total

    async def get_task(self, id):
        task = await Task.query.where(Task.id == id).gino.all()
        return task[0]

    async def delete_task(self, id):
        print(f"try to delete {id}")
        await self.pool.execute(self.DELETE_TASK, id)

    async def get_all_tasks(self, user_id = 0):
        user = types.User.get_current()
        user_id = user_id if user_id else user.id
        tasks = await Task.query.where(Task.user_id == user_id).gino.all()
        return tasks

    async def get_all_tasks_nwu(self):
        tasks = await Task.query.gino.all()
        return tasks

    #жесткий костыль через библиотеку asyncpg.
    async def get_first_task(self):
        user = types.User.get_current()
        user_id = user.id
        command = self.GET_FIRST_TASK

        result = await self.pool.fetch(command, (user_id))
        task = Task()
        task.id = result[0][0]
        task.user_id = result[0][1]
        task.datetime = result[0][2]
        task.remind_for = result[0][3]
        task.name = result[0][4]
        task.description = result[0][5]
        return task

    #жесткий костыль через библиотеку asyncpg.
    async def get_tasks(self, start, end, user_id = 0):
        command = self.GET_TASKS
        if not user_id:
            user = types.User.get_current()
            u_id = user.id
        else:
            u_id = user_id
        results = await self.pool.fetch(command, start, end, u_id)
        answ = []
        for result in results:
            task = Task()
            task.id = result[0]
            task.user_id = result[1]
            task.datetime = result[2]
            task.remind_for = result[3]
            task.name = result[4]
            task.description = result[5]
            answ.append(task)

        return answ

    async def get_tasks_nwu(self, start, end):
        command = self.GET_TASKS_NWU
        user = types.User.get_current()
        results = await self.pool.fetch(command,start,end)
        answ = []
        for result in results:
            task = Task()
            task.id = result[0]
            task.user_id = result[1]
            task.datetime = result[2]
            task.remind_for = result[3]
            task.name = result[4]
            task.description = result[5]
            answ.append(task)

        return answ

    async def get_tasks_where(self, year, month=0, day=0):
        user = types.User.get_current()
        user_id = user.id
        tasks = await Task.query.where(Task.user_id == user_id).gino.all()
        result = list()
        for task in tasks:
            if task.datetime.year == year:
                if not month:
                    result.append(task)
                    continue
                if task.datetime.month == month:
                    if not day:
                        result.append(task)
                        continue
                    if task.datetime.day == day:
                        result.append(task)
        return result

    async def add_new_task(self, datatime, name, description, femind_for = 30, user_id = 0):
        user = types.User.get_current()
        try:
            new_task = Task()
            new_task.user_id = user_id if user_id else user.id
            new_task.datetime = datatime
            new_task.name = name
            new_task.description = description
            new_task.remind_for = femind_for
            await new_task.create()
            return new_task
        except:
            print(f"SOME TROUBLE IN add_new_task() {user.id} {datatime} {name} {description}")


async def start_connection():
    print('connecting with PostgreSQL')
    await db.set_bind(config.POSTGRES_URI)


async def rebot():
    print('connecting with PostgreSQL')
    await db.set_bind(config.POSTGRES_URI)
    #db.gino = GinoSchemaVisitor
    await db.gino.drop_all()
    await db.gino.create_all()


async def refill():
    print('connecting with PostgreSQL')
    dbt = DBCommands()
    await db.set_bind(config.POSTGRES_URI)
    all_tasks = await dbt.get_all_tasks_nwu()
    await db.gino.drop_all()
    await db.gino.create_all()
    for task in all_tasks:
        await dbt.add_new_task(task.datetime, task.name, task.description, 30, task.user_id)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_connection())


async def test1():
    dbt = DBCommands()
    date = datetime.datetime.now()

    for i in range(3,7):
       delta = datetime.timedelta(hours=(i-2)*0.5)
       await dbt.add_new_task(date+delta, f"Затримка {i*10}хвилин", f"заплановано на {date+delta}", i*10, 422929010)

    # result = await dbt.get_tasks_not_gino(start, end)
    # print(f"from {start} until {end}")
    # for task in result:
    #     print(str(task.datetime) + " : " +task.name)

if __name__ == "__main__":
    loop.run_until_complete(test1())

