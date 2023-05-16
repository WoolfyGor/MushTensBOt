import MTFeatures

if __name__ == "__main__":
    # Указываем название бд и режим отладки - True (будут писаться логи) или False (логи не будут писаться)
    worker = MTFeatures.MTFeatures("debug12.db", False)
    id = 123123123
    res = worker.GetBalance(id)
    if res is not None: print(f"У пользователя с id {id} на счету " + str(res))
    res = worker.AddPoints(id, 5)
    if res is not None: print(f"Добавляю пользователю с id {id} на счет {res[1]} очков, изменилось с {res[2]} до {res[0]}")
    res = worker.SubstractPoints(id, 3)
    if res is not None: print(f"Вычитаю у пользователя с id {id} со счета {res[1]} очков, изменилось с {res[2]} до {res[0]}")
    res = worker.GetUserState(id)
    if res is not None: print(f"У пользователя с id {id} статус " + str(res))
    res = worker.SetUserState(id, 4)
    if res is not None: print(f"Изменяю статус пользователя с id {id} с {res[1]} на статус {res[0]}")
    res = worker.GetUserState(id)
    if res is not None: print(f"У пользователя с id {id} статус " + str(res))
