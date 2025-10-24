yesno = input("""Введите Y, если хотите авторизоваться или N, 
             если хотите продолжить работу как анонимный пользователь: """)

auth = yesno == "Y"

def is_auth(func):
    def wrapper(*args, **kwargs):
        if auth:
            print("Пользователь авторизован")
            func(*args, **kwargs)
        else:
            print("Пользователь неавторизован. Функция выполнена не будет")
    return wrapper

@is_auth
def from_db():
    print("some data from database")

from_db()