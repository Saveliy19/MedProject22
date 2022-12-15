'''файл взаимодействия с таблицами базы данных'''
from werkzeug.security import generate_password_hash, check_password_hash

from app.routes import session

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
                password_hash: str = "",
                sex: str = ""):

                self.id : int = id
                self.sertificate: str = sertificate
                self.name : str = name
                self.birthdate : str = birthdate
                self.password_hash: str = password_hash
                self.sex: str = sex
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

    def update_password_hash(self):
        query = f'''UPDATE "CLIENT" SET "PASSWORD"='{self.password_hash}' WHERE "FIO"='{self.name}';'''
        return Database.execute_query(query)
    
    # проверка хэша
    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    #def edit_password():

    
    #добавляем пользователя
    def adduser(self):
        query = f'''INSERT INTO "CLIENT" ("SERTIFICATE", "FIO", "BIRTHDATE", "PASSWORD", "SEX") VALUES ('{self.sertificate}', '{self.name}', '{self.birthdate}', '{self.password_hash}', '{self.sex}');'''
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

    def get_id_by_username(username):
        query = f'''SELECT "ID" FROM "CLIENT" WHERE "FIO" = '{username}';'''
        result = Database.select_query(query)
        print("ПОЛУЧАЕМ id пациента ПО ЕГО имени")
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        return result

    def get_sertificate_by_id(id):
        query = f'''SELECT "SERTIFICATE" FROM "CLIENT" WHERE "ID" = '{id}';'''
        result = Database.select_query(query)
        print("ПОЛУЧАЕМ сертификат пациента ПО ЕГО айди")
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        return result

    
class Note():
    def add_note(description, ticket_id, client_id, sertificate):
        query = f'''INSERT INTO "NOTE"("DESCRIPTION", "TICKET_ID", "CLIENT_ID", "PATIENT_SERTIFICATE") 
        VALUES ('{description}', '{ticket_id}', '{client_id}', '{sertificate}')'''
        return Database.execute_query(query)


    def get_notes_by_client_sertificate(sertificate):
        query = f'''SELECT "DESCRIPTION" FROM "NOTE" JOIN "CLIENT" 
        ON "NOTE"."CLIENT_ID"="CLIENT"."ID"
        WHERE "CLIENT"."SERTIFICATE"='{sertificate}';'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result

class Doctor(UserMixin):
    def __init__(self,
                id: int = 0,
                login: str = "",
                name: str = "",
                birthdate: str = "",
                password: str = "",
                sex: str = ""):

                self.id : int = id
                self.login: str = login
                self.name : str = name
                self.birthdate: str = birthdate
                self.password: str = password
                self.sex: str = sex
                self.role = "doc"

    def __repr__(self):
        return f'<User {self.login}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.login}'
        return string

    
    # проверка пароля
    def check_password(self, password: str):
        if self.password == password:
            return True
        return False

    def update_password(self):
        query = f'''UPDATE "DOCTOR" SET "PASSWORD"='{self.password}' WHERE "FIO"='{self.name}';'''
        return Database.execute_query(query)

    
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

    def get_services_by_doc_name(name):
        query = f'''SELECT "SERVICE"."NAME"
        FROM "DOCTOR" JOIN "DOCTOR_SERVICE" ON "DOCTOR_SERVICE"."DOC_ID"="DOCTOR"."ID"
        JOIN "SERVICE" ON "DOCTOR_SERVICE"."SERVICE_ID"="SERVICE"."ID"
        WHERE "DOCTOR"."FIO"='{name}';'''
        result = Database.select_query(query)
        result = map(lambda x: x[0] , result)
        return result
    
    def get_services_by_doc_id(id):
        query = f'''SELECT "SERVICE"."ID", "SERVICE"."NAME"
        FROM "DOCTOR" JOIN "DOCTOR_SERVICE" ON "DOCTOR_SERVICE"."DOC_ID"="DOCTOR"."ID"
        JOIN "SERVICE" ON "DOCTOR_SERVICE"."SERVICE_ID"="SERVICE"."ID"
        WHERE "DOCTOR"."ID"='{id}';'''
        result = Database.select_query(query)
        return result
    
    def get_service_id_by_name(service):
        query = f'''SELECT "ID" FROM "SERVICE" WHERE "NAME"='{service}';'''
        result = Database.select_query(query)
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        print('рррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррррр')
        print(result)
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

    def get_specialists_by_service(service):
        query = f'''SELECT "DOCTOR"."ID", "DOCTOR"."FIO"
        FROM "DOCTOR" JOIN "DOCTOR_SERVICE" ON "DOCTOR_SERVICE"."DOC_ID"="DOCTOR"."ID"
        JOIN "SERVICE" ON "DOCTOR_SERVICE"."SERVICE_ID"="SERVICE"."ID"
        WHERE "SERVICE"."NAME"='{service}';'''
        result = Database.select_query(query)
        return result

class Ticket():

    def delete_ticket(sertificate, date, time):
        query = f'''DELETE FROM "TICKET"
        WHERE "ID" IN
        (SELECT "TICKET"."ID" FROM "TICKET" JOIN "CLIENT"
        ON "TICKET"."CLIENT_ID"="CLIENT"."ID"
        WHERE "CLIENT"."SERTIFICATE"='{sertificate}' AND "DATE"='{date}' AND "TIME"='{time}');'''
        return Database.execute_query(query)

    def set_status_for_ticket_by_id(ticket_id, status):
        query = f'''UPDATE "TICKET" SET "STATUS"={status} WHERE "ID"={ticket_id};'''
        return Database.execute_query(query)


    def get_ticket_by_DOC(login):
        query = f'''SELECT "DATE", "TIME", "FIO", "SERVICE"."NAME" 
        FROM "TICKET" JOIN "CLIENT" ON "CLIENT"."SERTIFICATE"="PATIENT_SERTIFICATE"
        JOIN "TICKET_FOR_SERVICE" ON "TICKET_FOR_SERVICE"."TICKET_ID"="TICKET"."ID"
        JOIN "SERVICE" ON "TICKET_FOR_SERVICE"."SERVICE_ID"="SERVICE"."ID"
        WHERE "DOC_LOGIN"= '{login}' AND "STATUS"=false;'''
        result = Database.select_query(query)
        result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3])) , result)
        return result
        
    def get_ticket_by_CLIENT(sertificate):
        query = f'''SELECT "DATE", "TIME", "DOCTOR"."FIO", "SERVICE"."NAME"
        FROM "DOCTOR" JOIN "TICKET" ON "TICKET"."DOC_ID"="DOCTOR"."ID"
        JOIN "CLIENT" ON "CLIENT"."ID"="TICKET"."CLIENT_ID"
        JOIN "TICKET_FOR_SERVICE" ON "TICKET"."ID"="TICKET_FOR_SERVICE"."TICKET_ID"
        JOIN "SERVICE" ON "TICKET_FOR_SERVICE"."SERVICE_ID"="SERVICE"."ID"
        WHERE "CLIENT"."SERTIFICATE"='{sertificate}' AND "STATUS"=false;'''
        result = Database.select_query(query)
        result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3])) , result)
        return result
        
    def get_ticket_by_doclog_pat_dat(doc_login, client_name, day):
        query = f'''SELECT "TICKET"."ID" FROM "CLIENT" JOIN "TICKET" ON "TICKET"."CLIENT_ID"="CLIENT"."ID"
        JOIN "DOCTOR" ON "TICKET"."DOC_ID"="DOCTOR"."ID"
        WHERE "DOCTOR"."LOGIN"='{doc_login}' AND "CLIENT"."FIO"='{client_name}' AND "TICKET"."DATE"='{day}';'''
        result = Database.select_query(query)
        print("ПОЛУЧАЕМ АЙДИ ПРИЕМА ПО ЛОГИНУ ВРАЧА, ИМЕНИ ПАЦИЕНТА И ТЕКУЩЕМУ ДНЮ")
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        return result

    def get_ticket_by_docid_pat_dat(doc_id, client_name, day):
        query = f'''SELECT "TICKET"."ID" FROM "CLIENT" JOIN "TICKET" ON "TICKET"."CLIENT_ID"="CLIENT"."ID"
        JOIN "DOCTOR" ON "TICKET"."DOC_ID"="DOCTOR"."ID"
        WHERE "DOCTOR"."ID"='{doc_id}' AND "CLIENT"."SERTIFICATE"='{client_name}' AND "TICKET"."DATE"='{day}';'''
        result = Database.select_query(query)
        print("ПОЛУЧАЕМ АЙДИ ПРИЕМА ПО ЛОГИНУ ВРАЧА, ИМЕНИ ПАЦИЕНТА И ТЕКУЩЕМУ ДНЮ")
        result = list(map(lambda x: x[0] , result))
        result = result[0]
        print(result)
        return result

    def add_ticket(date, time, sertificate, cl_id, d_id, d_login):
        query = f'''INSERT INTO "TICKET"("DATE", "TIME", "PATIENT_SERTIFICATE", "CLIENT_ID", "DOC_ID", "DOC_LOGIN", "STATUS") 
        VALUES ('{date}', '{time}', '{sertificate}', '{cl_id}', '{d_id}', '{d_login}', false);'''
        return Database.execute_query(query)

    def add_ticket_for_service(service, ticket_id):
        service_id = Services.get_service_id_by_name(service)
        query = f'''INSERT INTO "TICKET_FOR_SERVICE" VALUES ('{service_id}', '{ticket_id}');'''
        return Database.execute_query(query)



class Specialization():
    def get_specializations():
        query = f'''SELECT "ID", "NAME" FROM "SPECIALIZATION";'''
        result = Database.select_query(query)
        #result = list(map(lambda x: x[0] , result))
        return result


    

#метод загрузки клиента
@login.user_loader
def load_user(id: str):
    if session['role'] == 'doc':
        user = Doctor.get_by_docID(int(id))
    elif session['role'] == 'cl':
        user = User.get_by_id(int(id))
    print(f'user loaded, user = {user}')
    return user


    