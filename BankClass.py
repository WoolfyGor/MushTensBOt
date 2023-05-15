import sqlite3 #Для работы с SQLite

class Bank:
    """Главный класс, который хранит в себе функцию для взаимодействия с БД, получением и изменением в ней значений """
    checkedForUser = True
    _debug_ = False;
    __currentId = ""
    __dbName__ = "debug.db"  # Контстанты, которые можно изменять - название бд
    """Название бд, к которой будет идти коннект"""
    __BankTableName__ = "Bank"  # Название таблицы для счета
    __UsersTableName__ = "Users"  # Название таблицы юзеров
    __UsersStatesTableName__ = "UsersStates"  # Название таблицы юзеров
    __StatesTableName__ = "States"

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
                    "Id_Bank INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL , Id_User NUMBER, Bank_Currency NUMBER")  # Создание таблицы под банк
        self.__CreateTable(cursor,self.__UsersStatesTableName__,"Id_UserState INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL , Id_User NUMBER, Id_State NUMBER DEFAULT 0")
        self.__CreateTable(cursor,self.__StatesTableName__,f"Id_State INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL ,State_Num NUMBER NOT NULL, StateName TEXT NOT NULL); Insert Into {self.__StatesTableName__}(State_Num,StateName) Values(0,\"Default\"),(1,\"Ignored\"),(2,\"WhiteList\"),(3,\"Owner\"),(4,\"IgnorePrev\"")



    def __CreateTable(self,cursor, name, fields):  # Создание таблицы с определенным названием и перечнем атрибутов
        res = cursor.execute(
            f"select count(*) from sqlite_master where type='table' and name='{name}'")  # проверяем, создана ли уже таблица
        if (res.fetchone()[0] > 0):  # Если создана - скипаем
            print(f"\"{name}\" table already exists, skip")
        else:
            if self._debug_ : print(  f"CREATE TABLE IF NOT EXISTS  \"{name}\" ({fields} );")
            cursor.executescript(
                f"CREATE TABLE IF NOT EXISTS  \"{name}\" ({fields} );")  # иначе создаем (на всякий случай проверяя, что не существует) с перечнем атрибутов
            print(f"Created \"{name}\" table")
        cursor.connection.commit()

    def __CheckInTable(self,cursor, idUser, table,
                     attribute):  # Проверка на наличие пользователя с id в конкретной table и указанием attribute, который проверяем
        if type(idUser) == sqlite3.Cursor:
            idUser = idUser
            print("error")

        if self._debug_ : print( f"Select {attribute} From {table} Where {table}.{attribute} ={str(idUser)}")
        res = cursor.execute(
            f"Select {attribute} From {table} Where {table}.{attribute} ={str(idUser)}")  # проверяем, есть ли юзер в таблице Users
        result = res.fetchone()
        return result

    def __AddToTable(self,cursor, values, table,
                   attribute):  # Добавляем значение(-я) в таблицу table, используя аттрибут(-ы) attribute и данные value
        if self._debug_ : print(f"Insert into {table} ({attribute}) Values ({values})")
        res = cursor.execute(f"Insert into {table} ({attribute}) Values ({values})")  # Добавляем юзера в таблицу
        if (str(values).__contains__(",")):
            id = values[:-values.find(",")]
        print(f"Added user with id {values} to table \"{table}\"")  # Принт сделан с учетом, что первый аттрибут - id
        cursor.connection.commit()  # Отправляем транзакцию в бд (применяем запрос, чтобы изменения отразились)
        return res

    def __OveralCheck(self,cursor,idUser,table,attribute, isBank = False):
        if len(str(idUser))<7:
            return
        if (str(idUser).__contains__(",")):
            localId = idUser[:idUser.find(",")]
        else:
            localId = idUser

        if table != self.__UsersTableName__:
            localId = self.__SelectQuerry(cursor,idUser,"Id_User",self.__UsersTableName__,"User_VkID").fetchone()[0]



        if self._debug_ : print(localId)
        resultUser = self.__CheckInTable(cursor, localId, table,
                                       attribute)  # Если пользователя нет в таблице - вернет None
        if isBank:
            localId= str(localId)+",0"
            attribute+=",Bank_Currency"

        if resultUser == None:
            resultUser = self.__AddToTable(cursor, localId, table,
                                         attribute)  # Раз пользователя нет - добавляем его в таблицу юзеров


    def __UpdateQuery(self,cursor, idUser, amount,isState = False):  # Функция по обновлению данных в таблице
        self.__OveralCheck(cursor,idUser,self.__UsersTableName__, "User_VkId")
        self.__OveralCheck(cursor,str(idUser),self.__BankTableName__,"Id_User",True)
        self.__OveralCheck(cursor, idUser, self.__UsersStatesTableName__, "Id_User")

        if not isState:
            # Берем текущее значение баллов у юзера и добавляем amount (при добавлении amount положительный, при вычитании - отрицательный : происходит уменьшение)

            query = f"Update {self.__BankTableName__} Set Bank_Currency = (Select {self.__BankTableName__}.Bank_Currency From {self.__BankTableName__} Where {self.__BankTableName__}.Id_User ={idUser})+{amount} Where Id_User = {idUser}"
            if self._debug_ : print(query)
            cursor.execute(query)
            cursor.connection.commit()  # Отправляем транзакцию в бд, чтобы изменения сохранились
            res = self.__SelectQuerry(cursor, idUser, "Bank_Currency", self.__BankTableName__,
                                      "Id_Bank")  # Возвращаем новое кол-во баллов после добавления

        else:
            localId = self.__GetId(cursor,idUser)
            query =  f"Update {self.__UsersStatesTableName__} Set Id_State = (Select {self.__StatesTableName__}.Id_State From {self.__StatesTableName__} Where {self.__StatesTableName__}.State_Num = {amount}) Where {self.__UsersStatesTableName__}.Id_User = {localId}"
            if self._debug_ :  print(query)
            cursor.execute(query)
            cursor.connection.commit()  # Отправляем транзакцию в бд, чтобы изменения Id_User
            res = self.__SelectQuerry(cursor, amount, "Id_State,StateName", self.__StatesTableName__,
                               "State_Num")  # Возвращаем новое кол-во баллов после добавления

        return res.fetchone()
    def __GetId(self,cursor,idUser):
        localId = self.__SelectQuerry(cursor, idUser, "Id_User", self.__UsersTableName__, "User_VkID")
        if not isinstance(localId,tuple):
            return None
        else:
            localId = localId.fetchone()[0]
        return localId



    def __SelectQuerry(self,cursor, idUser, attribute, table,idAttribute="" ):  # Производим  выборку атрибута attribute из таблицы table, где id юзера равен idUser
        if not self.checkedForUser:
            self.__OveralCheck(cursor,idUser,self.__UsersTableName__, "User_VkId") #Проверка на наличие в таблице юзеров. Нет - добавят
            self.checkedForUser = True
            self.__OveralCheck(cursor,str(idUser),self.__BankTableName__,"Id_User",True)#Проверка на наличие в таблице банка. Нет - добавят
            self.__OveralCheck(cursor, idUser, self.__UsersStatesTableName__, "Id_User")



        if self._debug_ : print(f"Select {attribute} From {table} Where {table}.{idAttribute} = {idUser}")
        res = cursor.execute(
            f"Select {attribute} From {table} Where {table}.{idAttribute} = {idUser}")  # проверяем, есть ли юзер в таблице Users


        return res

    def __DoAction(self,action, idUser,
                 amount=None):  # В зависимости от action выполняем разные действия - прибалвяем баллы, вычитаем баллы, получаем баланс
        self.checkedForUser = False;

        cursor = self.__GetCursor()
        localId = self.__GetId(cursor, idUser)
        if(localId is None):
            localId = idUser



        if action == "Add":
            print(f"Adding to user {idUser} {amount} points")
            res = self.__UpdateQuery(cursor, localId,
                              amount)  # Результат - turple в формате (итого, на_сколько_изменяли, сколько_было)

        elif action == "Subs":
            print(f"Substract from user {idUser} {amount} points")
            res = self.__UpdateQuery(cursor, localId,
                              amount)  # Результат - turple в формате (итого, на_сколько_изменяли, сколько_было)

        elif action == "Balance":
            localId = self.__GetId(cursor,idUser).fetchone()[0]
            res = self.__SelectQuerry(cursor, localId, "Bank_Currency", self.__BankTableName__,
                               "Id_User")  # Результат - число - текущий баланс

        elif action == "GetState":
            localId = self.__GetId(cursor, idUser).fetchone()[0]
            res = self.__SelectQuerry(cursor, localId, "ID_State", self.__UsersStatesTableName__,
                                      "Id_User")  # Результат - число - текущий баланс

        elif action == "UpdateState":
            print(f"Substract from user {idUser} {amount} points")
            res = self.__UpdateQuery(cursor, idUser,
                                     amount,True)  # Результат - turple в формате (итого, на_сколько_изменяли, сколько_было)

        return res

    def BankAddPoints(self,id, amount):
        """Добавляет пользователю по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и добавит к 0.
         \n Возвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)"""

        final = self.__DoAction("Add", id, amount)
        if(final == None):
            return final
        else:
            return (final, amount, final - amount)

    def BankSubstractPoints(self,id, amount):
        """Вычитает у  пользователя по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и отбавит у 0.
        \nВозвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)
        """
        final = self.__DoAction("Subs", id, -amount)
        if (final == None):
            return final
        else:
            return (final, amount, final - amount)


    def BankGetBalance(self,id):
        """Ищет баланс пользователя с некоторым id. Если пользователя нет в бд - добавит и вернет его кол-ко баллов (0).
        \nВозвращает число - кол-во баллов
        """
        final = self.__DoAction("Balance", id)
        return final.fetchone()[0]

    def UserGetState(self,id):
        """Возвращает статус  пользователя с некоторым id. Если пользователя нет в бд - добавит и вернет его статус - по-умолчанию (0).
               \nВозвращает число - номер статуса
               """
        final = self.__DoAction("GetState", id)
        return final.fetchone()[0]

    def UserSetState(self,id,amount):
        """Устанавливает статус  пользователя с некоторым id. Если пользователя нет в бд - добавит и вернет его статус - по-умолчанию (0).
                       \nВозвращает turple в формате (новый_статус,название_статуса_в_бд,id_статуса_в_бд)
                       """
        final = self.__DoAction("UpdateState", id,amount)
        return (amount,final[1],final[0])
