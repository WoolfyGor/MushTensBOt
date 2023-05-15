import  BankClass

if __name__ == "__main__":

    bank = BankClass.Bank()
    bank.__dbName__ = "debug1.db"
    bank._debug_ = True;
    bank.InitialSetup()
    id = 515721924
    res = bank.BankAddPoints(id,10)
    if res != None:
        print(f"У юзера {id} было {res[2]} баллов и после добавления {res[1]} баллов стало {res[0]} баллов. ")
    #id = 33123
    res = bank.BankSubstractPoints(id,50)
    #print(f"У юзера {id} было {res[2]} баллов и после вычитания {res[1]} баллов стало {res[0]} баллов. ")
    #id = 123213213
    #res = bank.UserSetState(id,2)
    #print(f"У юзера {id} статус изменен на {res[0]}, название статуса : {[res[1]]} , id статуса в бд - {res[2]}")




