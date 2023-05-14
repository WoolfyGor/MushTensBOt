import sqlite3 #Для работы с SQLite
class Bank:
    """Главный класс, который хранит в себе функцию для взаимодействия с БД, получением и изменением в ней значений """

    __dbName__ = "debug.db"  # Контстанты, которые можно изменять - название бд
    """Название бд, к которой будет идти коннект"""
    __BankTableName__ = "Bank"  # Название таблицы для счета
    __UsersTableName__ = "Users"  # Название таблицы юзеров

    def __ConnectToDb(self,dbName):  # Возвращает коннект к определенной бд
        return sqlite3.connect(dbName)

    def __GetCursor(self):  # Возвращает курсор по определенному коннекту (через курсор идут запросы)
        connection = self.__ConnectToDb(self.__dbName__)
        return connection.cursor()
    def InitialSetup(self):  # Первичная настройка - создание таблиц по определенному курсору с перечнем атрибутов в них
        """Производит первичную настройку соединения. Коннектится к бд по указанному в переменной __dbName__ адресу (если его нет - создает), а
        затем создает таблицы при для пользователей и для банка (где хранятся валюты). Названия таблиц в переменных __UsersTableName__ и __BankTableName__ - при необходимости нужно изменить перед сетапом.
        """
        print(f"Start working with database \"{self.__dbName__}\"")
        cursor = self.__GetCursor()
        self.__CreateTable(cursor, self.__UsersTableName__,
                    "Id_User INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL , User_VkId NUMBER")  # Создание таблицы для пользователей
        self.__CreateTable(cursor, self.__BankTableName__,
                    "Id_Bank INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL , User_VkId NUMBER, Bank_Currency NUMBER")  # Создание таблицы под банк

    def __CreateTable(self,cursor, name, fields):  # Создание таблицы с определенным названием и перечнем атрибутов
        res = cursor.execute(
            f"select count(*) from sqlite_master where type='table' and name='{name}'")  # проверяем, создана ли уже таблица
        if (res.fetchone()[0] > 0):  # Если создана - скипаем
            print(f"\"{name}\" table already exists, skip")
        else:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS  \"{name}\" ({fields} );")  # иначе создаем (на всякий случай проверяя, что не существует) с перечнем атрибутов
            print(f"Created \"{name}\" table")

    def __CheckInTable(self,cursor, id, table,
                     attribute):  # Проверка на наличие пользователя с id в конкретной table и указанием attribute, который проверяем
        res = cursor.execute(
            f"Select {attribute} From {table} Where {table}.{attribute} ={str(id)}")  # проверяем, есть ли юзер в таблице Users
        result = res.fetchone()
        return result

    def __AddToTable(self,cursor, values, table,
                   attribute):  # Добавляем значение(-я) в таблицу table, используя аттрибут(-ы) attribute и данные value
        res = cursor.execute(f"Insert into {table} ({attribute}) Values ({values})")  # Добавляем юзера в таблицу
        if (str(values).__contains__(",")):
            id = values[:-values.find(",")]
        print(f"Added user with id {values} to table \"{table}\"")  # Принт сделан с учетом, что первый аттрибут - id
        cursor.connection.commit()  # Отправляем транзакцию в бд (применяем запрос, чтобы изменения отразились)
        return res

    def __OveralCheck(self,cursor,id,table,attribute, isBank = False):

        if (str(id).__contains__(",")):
            localId = id[:id.find(",")]
        else:
            localId = id
            
        resultUser = self.__CheckInTable(cursor, localId, table,
                                       attribute)  # Если пользователя нет в таблице - вернет None
        if isBank:
            localId+=",0"
            attribute+=",Bank_Currency"

        if resultUser == None:
            resultUser = self.__AddToTable(cursor, localId, table,
                                         attribute)  # Раз пользователя нет - добавляем его в таблицу юзеров


    def __UpdateQuery(self,cursor, id, amount):  # Функция по обновлению данных в таблице
        self.__OveralCheck(cursor,id,self.__UsersTableName__, "User_VkId")
        self.__OveralCheck(cursor,str(id),self.__BankTableName__,"User_VkId",True)

        # Берем текущее значение баллов у юзера и добавляем amount (при добавлении amount положительный, при вычитании - отрицательный : происходит уменьшение)
        cursor.execute(
            f"Update {self.__BankTableName__} Set Bank_Currency = (Select {self.__BankTableName__}.Bank_Currency From {self.__BankTableName__} Where {self.__BankTableName__}.User_VkId ={id})+{amount} Where User_VkId = {id}")
        cursor.connection.commit()  # Отправляем транзакцию в бд, чтобы изменения сохранились
        res = self.__SelectQuerry(cursor, id, "Bank_Currency", self.__BankTableName__,
                           "User_VkId")  # Возвращаем новое кол-во баллов после добавления
        return res.fetchone()

    def __SelectQuerry(self,cursor, idUser, attribute, table,idAttribute=""):  # Производим  выборку атрибута attribute из таблицы table, где id юзера равен idUser
        self.__OveralCheck(cursor,idUser,self.__UsersTableName__, "User_VkId") #Проверка на наличие в таблице юзеров. Нет - добавят
        self.__OveralCheck(cursor,str(idUser),self.__BankTableName__,"User_VkId",True)#Проверка на наличие в таблице банка. Нет - добавят
        res = cursor.execute(
            f"Select {attribute} From {table} Where {table}.{idAttribute} = {str(idUser)}")  # проверяем, есть ли юзер в таблице Users

        return res

    def __DoAction(self,action, idUser,
                 amount=None):  # В зависимости от action выполняем разные действия - прибалвяем баллы, вычитаем баллы, получаем баланс
        cursor = self.__GetCursor()
        if action == "Add":
            print(f"Adding to user {idUser} {amount} points")
            res = self.__UpdateQuery(cursor, idUser,
                              amount)  # Результат - turple в формате (итого, на_сколько_изменяли, сколько_было)

        elif action == "Subs":
            print(f"Substract from user {idUser} {amount} points")
            res = self.__UpdateQuery(cursor, idUser,
                              amount)  # Результат - turple в формате (итого, на_сколько_изменяли, сколько_было)

        elif action == "Balance":
            res = self.__SelectQuerry(cursor, idUser, "Bank_Currency", self.__BankTableName__,
                               "User_VkId")  # Результат - число - текущий баланс

        return res

    def BankAddPoints(self,id, amount):
        """Добавляет пользователю по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и добавит к 0.
         \n Возвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)"""
        final = int(self.__DoAction("Add", id, amount)[0])
        return (final, amount, final - amount)

    def BankSubstractPoints(self,id, amount):
        """Вычитает у  пользователя по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и отбавит у 0.
        \nВозвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)
        """

        final = int(self.__DoAction("Subs", id, -amount)[0])
        return (final, amount, final + amount)

    def BankGetBalance(self,id):
        """Ищет баланс пользователя с некоторым id. Если пользователя нет в бд - добавит и вернет его кол-ко баллов (0).
        \nВозвращает число - кол-во баллов
        """
        final = self.__DoAction("Balance", id)
        return final.fetchone()[0]


