import sqlite3

class Database:

    def __init__(self, db, debug):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self._debug_ = debug

    def create_table(self, table_name, columns):#Классическое создание таблицы в sql

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.cur.execute(query)
        self.conn.commit()

    def select(self, table_name, columns, where=None, order_by=None, limit=None):#Классическое select запрос на выборку в sql
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if self._debug_ : print(query)
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def insert(self, table_name, values, columns=None):#Классическое insert запрос на внесение данных в sql
        if columns:
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        else:
            placeholders = ", ".join(["?" for _ in values[0]])
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"

        if self._debug_ : print(query)
        self.cur.executemany(query, values)
        self.conn.commit()
        return self.cur.lastrowid

    def updateCl(self, table_name, set_values, where=None): #Классическое update запрос на измнение данных в sql
        query = f"UPDATE {table_name} SET {', '.join(set_values)}"
        if where:
            query += f" WHERE {where}"
        if self._debug_ : print(query)
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.rowcount

    def update(self, table_name, attribute, amount,where=None):#Update запрос с изменением некоторого поля на amount
        query = f"UPDATE {table_name} SET {attribute} = {attribute} + {amount} "
        if where:
            query += f" WHERE {where}"

        if self._debug_ : print(query)
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.rowcount


    def table_exists(self, table_name): #проверка на существование таблицы
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result is not None

    def __del__(self):
        self.conn.close()

class MTFeatures():
    __dbName= "debug.db"  # Контстанты, которые можно изменять - название бд
    """Название бд, к которой будет идти коннект"""
    __BankTableName= "Bank"  # Название таблицы для счета
    __UsersTableName = "Users"  # Название таблицы юзеров
    __UsersStatesTableName = "UserStates" # название таблицы для статусов пользователей
    __StatesTableName = "States" # название таблицы для статусов (всего перечня)
    _debug_ = False #если True - будет писать промежуточные логи.
    def __initialTables(self): #Первичная инициация бд вместе с таблицами и значениями по умолчанию
        #Создание основных таблиц
        self.__db.create_table(self.__UsersTableName,["Id_User INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL","User_VkId NUMBER"])
        self.__db.create_table(self.__BankTableName, ["Id_Bank INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL ", "Id_User NUMBER", "Bank_Currency NUMBER DEFAULT 0"])
        self.__db.create_table(self.__UsersStatesTableName,["Id_UserState INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL "," Id_User NUMBER"," Id_State NUMBER DEFAULT 1"])
        self.__db.create_table(self.__StatesTableName, ["Id_State INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ","State_Num NUMBER NOT NULL"," State_Name TEXT NOT NULL"])
        res = self.__db.select(self.__StatesTableName, ["Id_State"])
        if len(res)<1: #Если ещё не заполняли таблицу State, то вносим в нее стандартные значения в поля
            self.__db.insert(self.__StatesTableName,[(0,"Default"),(1,"Ignored"),(2,"WhiteList"),(3,"Owner"),(4,"IgnorePrev")],["State_Num","State_Name"])

    def __GetOrCreateUser(self,id): #Проверяем, есть ли пользователь в таблице юзеров. Есть - возвращаем id из бд. Нет - создаем, добавляем во все таблицы основные и возвращаем id из бд
        res = self.__db.select(self.__UsersTableName,["Id_User"],f"User_VkId= {id}")
        if len(res) > 0:
            return res[0]
        else:
            if self._debug_ : print("No user")
            return self.__AddUser(id)


    def __AddUser(self,id): #Добавление пользователя в бд, если первый раз к нему идет обращение
        self.__db.insert(self.__UsersTableName,[(id,)],["User_VkId"]) #Вносим в таблицу Users
        res = self.__db.select(self.__UsersTableName, ["Id_User"], f"User_VkId= {id}")#Получаем id по бд
        self.__db.insert(self.__BankTableName, [(res[0][0],)], ["Id_User"]) #Добавляем в таблицу банка
        self.__db.insert(self.__UsersStatesTableName, [(res[0][0],)], ["Id_User"]) #Добавляем в таблицу состояний (статусов)
        return res[0] #Возращаем id по сетке

    def __UpdateUserState(self,idUser,state,sender_id):
        prevState = self.__db.select(self.__UsersStatesTableName, ["Id_State"], f"Id_User = {idUser}")
        prevState = self.__db.select(self.__StatesTableName, ["State_Num"], f"Id_State = {prevState[0][0]}")[0][0]
        if sender_id == None:
            try:
                stateId = self.__db.select(self.__StatesTableName, ["Id_State"], f"State_Num = {state}")
                self.__db.updateCl(self.__UsersStatesTableName, [f"Id_State = {stateId[0][0]}"], f"Id_User = {idUser}")
                res = (state, prevState)
            except:
                res = None
        else:
            localSenderId = self.__GetOrCreateUser(sender_id)
            localSenderState =self.__db.select(self.__UsersStatesTableName, ["Id_State"], f"Id_User = {localSenderId[0]}")
            localSenderState = self.__db.select(self.__StatesTableName, ["State_Num"], f"Id_State = {localSenderState[0][0]}")[0][0]
            if self._debug_ == True:print(f"Отправитель со статусом {localSenderState} пытается изменить статус на {state} у пользователя со статусом {prevState}")
            if localSenderState>=prevState and localSenderState>=state:
                try:
                    if self._debug_ == True: print(f"Успешно изменяю")
                    stateId = self.__db.select(self.__StatesTableName, ["Id_State"], f"State_Num = {state}")
                    self.__db.updateCl(self.__UsersStatesTableName, [f"Id_State = {stateId[0][0]}"], f"Id_User = {idUser}")
                    res = (state, prevState)
                except:
                    res = None
            else:
                res = None
        return res




    def __DoAction(self,action, idUser,amount=None, sender_id=None):  # В зависимости от action выполняем разные действия - прибалвяем баллы, вычитаем баллы, получаем баланс
        if idUser:
            id = self.__GetOrCreateUser(idUser)[0] #Получаем id пользователя по сетке
        res = None
        if action == "Add":#Добавление юзеру очков
            if self._debug_ : print(f"Adding to user {idUser} {amount} points")
            self.__db.update(self.__BankTableName,"Bank_Currency",amount,f"Id_User = {id}")
            res = self.__db.select(self.__BankTableName, ["Bank_Currency"], f"Id_User = {id}")
        elif action == "Subs": #Вычитание юзеру очков
            if self._debug_ : print(f"Adding to user {idUser} {amount} points")
            self.__db.update(self.__BankTableName, "Bank_Currency", -amount, f"Id_User = {id}")
            res = self.__db.select(self.__BankTableName,["Bank_Currency"],f"Id_User = {id}")
        elif action == "Balance":# Получение счета юзера
            if self._debug_: print(f"Get balance of user with id {idUser}")
            res = self.__db.select(self.__BankTableName,["Bank_Currency"],f"Id_User = {id}" )
        elif action == "GetState":#Получение статуса пользователя
            if self._debug_: print(f"Get state of user with id {idUser}")
            prevState = self.__db.select(self.__UsersStatesTableName, ["Id_State"], f"Id_User = {id}")
            res = self.__db.select(self.__StatesTableName, ["State_Num"], f"Id_State = {prevState[0][0]}")
        elif action == "UpdateState":#Обновление статуса пользователя
            if self._debug_: print(f"Update state of user with id {idUser} to state with number {amount}")
            res = self.__UpdateUserState(id,amount,sender_id)
        elif action == "ClearPoints":#Очищение очков
            self.__db.updateCl(self.__BankTableName,[f"Bank_Currency = 0"], f"Id_User = {id}")
            res = 0
        elif action == "HARDClear":
            self.__db.updateCl(self.__BankTableName,[f"Bank_Currency = 0"])

        return res

    def AddPoints(self,id, amount): #Публичная функция для добавления очков
        """Добавляет пользователю по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и добавит к 0.
         \n Возвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)"""
        final = int(self.__DoAction("Add", id, amount)[0][0])
        return (final, amount, final - amount)

    def SubstractPoints(self,id, amount): #Вычитание очков у пользователя
        """Вычитает у  пользователя по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и отбавит у 0.
        \nВозвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)
        """
        final = int(self.__DoAction("Subs", id, amount)[0][0])
        return (final ,amount, final + amount)

    def ClearPoints(self,id): #Вычитание очков у пользователя
        """Очищает кол-во баллов у некоторого пользователя по его id. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и отбавит у 0.
        \nВозвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)
        """
        final = self.__DoAction("ClearPoints", id)
        return final

    def HARDClearPoints(self, id = None):  # Вычитание очков у пользователя
        """Очищает кол-во баллов у некоторого пользователя по его id. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и отбавит у 0.
        \nВозвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)
        """
        final = self.__DoAction("HARDClear", id)
        return final

    def GetBalance(self,id):#Получить текущее кол-во очков пользователя
        """Ищет баланс пользователя с некоторым id. Если пользователя нет в бд - добавит и вернет его кол-ко баллов (0).
        \nВозвращает число - кол-во баллов
        """
        final = self.__DoAction("Balance", id)
        return final[0][0]

    def GetUserState(self,id): #Получить текущий статус пользователя
        """Возвращает статус пользователя с некоторым id
                """
        final = self.__DoAction("GetState", id)
        return final[0][0]

    def SetUserState(self,id,state,sender_id = None): #Изменить текущий статус пользователя
        """Изменяет статус пользователя с некоторым id на статус state (номер статуса 0-4). Если указан иной - изменнеие не произойдет. Нужно добавлять в БД вариант и обновлять функцию для инициализации
                """
        final = self.__DoAction("UpdateState", id,state,sender_id)
        return final




    def __init__(self,dbName,debug = False):
        self.__dbName = dbName #Вбиваем имя бд
        self._debug_ =debug #устанавливаем режим отладки
        self.__db = Database(self.__dbName,self._debug_) #создаем и инициализируем подключение к бд
        self.__initialTables() #Создаем таблицы и первичные значения. Уже созданы? Будут пропущенно создание
