'''файл взаимодействия с таблицами базы данных'''
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import app
from app import login

from flask_login import UserMixin


#класс бд (подключение, запросы)
class Database(object):

    '''_database = app.config.Config['db_name']
    _user = app.Config['user']
    _user_password = app.Config['password']
    _db_host = app.Config['host']

    _user=Config.user,
    _password=Config.password,
    _host=Config.host,
    _database=Config.db_name
    _connection: psycopg2 = None'''


    @classmethod
    def _connect_to_db(cls) -> psycopg2:
        try:
            # Подключение к существующей базе данных
            cls._connection = psycopg2.connect(user='sav',
                                        password="kotikiandsobachki",
                                        host='localhost',
                                        database="medical_service")

        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'other error:\n{ex}')
        else:
            print("connection to PostgreSQL DB successful")
        return cls._connection
    
    @classmethod
    def execute_query(cls, query) -> bool:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the query executed successfully')
            return True
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто")
        return False

    @classmethod
    def select_query(cls, query) -> list:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Вот результат селекта:')
            print(result)
            return result
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто")
        return None


    
class User(UserMixin):


    def __init__(self,
                id: int = 0,
                sertificate: str = "",
                name: str = "",
                birthdate: str = "",
                password_hash: str = ""):

                self.id : int = id
                self.sertificate: str = sertificate
                self.name : str = name
                self.birthdate : str = birthdate
                self.password_hash: str = password_hash
                self.role = "cl"

    def __repr__(self):
        return f'<User {self.sertificate}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.sertificate}'
        return string

    # генерация хэш-пароля
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        print("Пароль для пользователя успешно сгенерирован")
        print(self.password_hash)
    
    # проверка хэша
    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    
    #добавляем пользователя
    def adduser(self):
        query = f'''INSERT INTO "CLIENT" ("SERTIFICATE", "FIO", "BIRTHDATE", "PASSWORD") VALUES ('{self.sertificate}', '{self.name}', '{self.birthdate}', '{self.password_hash}');'''
        return Database.execute_query(query)

    #получаем пользователя по id
    def get_by_id(id: int):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM "CLIENT" WHERE "ID" = '{id}';'''
        result = Database.select_query(query)
        print(f"Пользователь с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return User(* params)
    

    #получаем пользователя по номеру полиса
    def get_by_sertificate(sertificate: str):
        query = f'''SELECT * FROM "CLIENT" WHERE "SERTIFICATE" = '{sertificate}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return User(* params)

    
    def get_id_by_sertificate(sertificate):
        query = f'''SELECT "ID" FROM "CLIENT" WHERE "SERTIFICATE" = '{sertificate}';'''
        result = Database.select_query(query)
        print("ПОЛУЧАЕМ id пациента ПО ЕГО логину")
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        return result

    
class SuperUser():

    _flag=''


class Doctor(UserMixin):
    def __init__(self,
                id: int = 0,
                login: str = "",
                name: str = "",
                password: str = ""):

                self.id : int = id
                self.login: str = login
                self.name : str = name
                self.password: str = password
                self.role = "doc"

    def __repr__(self):
        return f'<User {self.login}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.login}'
        return string

    
    # проверка хэша
    def check_password(self, password: str):
        if self.password == password:
            return True
        return False

    
    def get_by_docID(id: int):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM "DOCTOR" WHERE "ID" = '{id}';'''
        result = Database.select_query(query)
        print(f"Пользователь с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Doctor(* params)

    #получаем пользователя по номеру полиса
    def get_by_login(login: str):
        query = f'''SELECT * FROM "DOCTOR" WHERE "LOGIN" = '{login}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Doctor(* params)

class Services():
    def get_services():
        query = f'''SELECT "NAME" FROM "SERVICE";'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result

class Specialists():
    def get_specialist():
        query = f'''SELECT "FIO" FROM "DOCTOR";'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result

    def get_spec_by_specialization_id(specialization):
        query = f'''SELECT "DOCTOR"."ID", "FIO" FROM "SPECIALIZATION" JOIN "DOCTOR_SPECIALIZATION"
        ON "SPECIALIZATION"."ID"="SPECIALIZATION_ID" 
        JOIN "DOCTOR" ON "DOCTOR"."ID"="DOC_ID" 
        WHERE "SPECIALIZATION"."ID"='{specialization}';'''
        result = Database.select_query(query)
        #result = list(map(lambda x: x[0] , result))
        return result


    def get_doc_login_by_doc_id(id):
        query = f'''SELECT "LOGIN" FROM "DOCTOR" WHERE "ID" = {id};'''
        result = Database.select_query(query)
        print("ПОЛУЧАЕМ ЛОГИН ДОКТОРА ПО ЕГО АЙДИ")
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        return result


class Specialization():
    def get_specializations():
        query = f'''SELECT "ID", "NAME" FROM "SPECIALIZATION";'''
        result = Database.select_query(query)
        #result = list(map(lambda x: x[0] , result))
        return result


class Ticket():
    def add_ticket(date, time, sertificate, cl_id, d_id, d_login):
        query = f'''INSERT INTO "TICKET"("DATE", "TIME", "PATIENT_SERTIFICATE", "CLIENT_ID", "DOC_ID", "DOC_LOGIN") VALUES ('{date}', '{time}', '{sertificate}', '{cl_id}', '{d_id}', '{d_login}');'''
        return Database.execute_query(query)

#метод загрузки клиента
@login.user_loader
def load_user(id: str):
    flag = SuperUser._flag
    if flag == 'doc':
        user = Doctor.get_by_docID(int(id))
    else:
        user = User.get_by_id(int(id))
    print(f'user loaded, user = {user}')
    return user


    