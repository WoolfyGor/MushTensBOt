import  BankClass
import  MTFeatures
'''
if __name__ == "__main__":

    bank = BankClass.Bank()
    bank.__dbName__ = "debug.db"
    bank.InitialSetup()
    id = 19734129847
    res = bank.BankAddPoints(id,50)
    print(f"У юзера {id} было {res[2]} баллов и после добавления {res[1]} баллов стало {res[0]} баллов. ")
    id = 55887614
    res = bank.BankSubstractPoints(id,50)
    print(f"У юзера {id} было {res[2]} баллов и после вычитания {res[1]} баллов стало {res[0]} баллов. ")
    id = 8989899
    res = bank.BankGetBalance(id)
    print(f"У юзера {id} на балансе сейчас {res} баллов ")



'''

if __name__ == "__main__":
    bank = MTFeatures.MTFeatures("test.db")
    res = bank.BankAddPoints(11266123,50)
    print(res)
