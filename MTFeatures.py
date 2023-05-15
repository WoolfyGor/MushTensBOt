import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.cur.execute(query)
        self.conn.commit()

    def select(self, table_name, columns, where=None, order_by=None, limit=None):
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"

        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def insert(self, table_name, values, columns=None):
        if columns:
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        else:
            placeholders = ", ".join(["?" for _ in values[0]])
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"

        print(query)
        self.cur.executemany(query, values)
        self.conn.commit()
        return self.cur.lastrowid

    def update(self, table_name, set_values, where=None):
        query = f"UPDATE {table_name} SET {', '.join(set_values)}"
        if where:
            query += f" WHERE {where}"

        self.cur.execute(query)
        self.conn.commit()
        return self.cur.rowcount

    def update(self, table_name, attribute, amount,where=None):
        query = f"UPDATE {table_name} SET {attribute} = {attribute} + {amount} "
        if where:
            query += f" WHERE {where}"
            print(query)
        self.cur.execute(query)
        self.conn.commit()
        return self.cur.rowcount


    def table_exists(self, table_name):
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result is not None

    def __del__(self):
        self.conn.close()

class MTFeatures():
    __dbName__ = "debug.db"  # Контстанты, которые можно изменять - название бд
    """Название бд, к которой будет идти коннект"""
    __BankTableName__ = "Bank"  # Название таблицы для счета
    __UsersTableName__ = "Users"  # Название таблицы юзеров
    __UsersStatesTableName__ = "UserStates"
    __StatesTableName__ = "States"

    def initialTables(self):
        self.db.create_table(self.__UsersTableName__,["Id_User INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL","User_VkId NUMBER"])
        self.db.create_table(self.__BankTableName__, ["Id_Bank INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL ", "Id_User NUMBER", "Bank_Currency NUMBER DEFAULT 0"])
        self.db.create_table(self.__UsersStatesTableName__,["Id_UserState INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL "," Id_User NUMBER"," Id_State NUMBER DEFAULT 0"])
        self.db.create_table(self.__StatesTableName__, ["Id_State INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ","State_Num NUMBER NOT NULL"," State_Name TEXT NOT NULL"])
        res = self.db.select(self.__StatesTableName__, ["Id_State"])
        if len(res)<1:
            self.db.insert(self.__StatesTableName__,[(0,"Default"),(1,"Ignored"),(2,"WhiteList"),(3,"Owner"),(4,"IgnorePrev")],["State_Num","State_Name"])

    def GetOrCreateUser(self,id):
        res = self.db.select(self.__UsersTableName__,["Id_User"],f"User_VkId= {id}")
        if len(res) > 0:
            return res[0]
        else:
            print("No user")
            return self.AddUser(id)


    def AddUser(self,id):
        self.db.insert(self.__UsersTableName__,[(id,)],["User_VkId"])
        res = self.db.select(self.__UsersTableName__, ["Id_User"], f"User_VkId= {id}")
        self.db.insert(self.__BankTableName__, [(res[0][0],)], ["Id_User"])
        self.db.insert(self.__UsersStatesTableName__, [(res[0][0],)], ["Id_User"])
        return res[0]

    def __DoAction(self,action, idUser,amount=None):  # В зависимости от action выполняем разные действия - прибалвяем баллы, вычитаем баллы, получаем баланс
        id = self.GetOrCreateUser(idUser)
        if action == "Add":
            print(f"Adding to user {idUser} {amount} points")
            res = self.db.update(self.__BankTableName__,"Bank_Currency",amount,f"Id_User = {id[0]}")

        elif action == "Subs":
            print(f"Adding to user {idUser} {amount} points")
            res = self.db.update(self.__BankTableName__, "Bank_Currency", -amount, f"Id_User = {id[0]}")

        elif action == "Balance":
            res = self.db.select(self.__BankTableName__,["Bank_Currency"] )

        return res

    def BankAddPoints(self,id, amount):
        """Добавляет пользователю по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и добавит к 0.
         \n Возвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)"""
        final = int(self.__DoAction("Add", id, amount))
        return (final, amount, final - amount)

    def BankSubstractPoints(self,id, amount):
        """Вычитает у  пользователя по его id некоторое (amount) кол-во баллов. Если пользователь есть в бд - обновит его кол-во баллов. Если нет - добавит в таблицы с 0 по умолчанию и отбавит у 0.
        \nВозвращает turple в формате : \n(итого, на_сколько_изменяли, сколько_было)
        """

        final = int(self.__DoAction("Subs", id, amount))
        return (final, amount, final - amount)

    def BankGetBalance(self,id):
        """Ищет баланс пользователя с некоторым id. Если пользователя нет в бд - добавит и вернет его кол-ко баллов (0).
        \nВозвращает число - кол-во баллов
        """
        final = self.__DoAction("Balance", id)
        return final


    def __init__(self,dbName):
        self.__dbName__ = dbName
        self.db = Database(self.__dbName__)
        self.initialTables()
