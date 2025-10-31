def e():
    n = 1
    while True:
        yield (1 + 1 / n) ** n
        n += 1
# eee = iter(e())
# for _ in range(10):
#     print(next(eee))

last = 0
count = 0
for a in e(): # e() - генератор
    if (a - last) < 0.0000000000000001: # ограничение на точность
        print(a, count)
        break # после достижения которого - завершаем цикл
    else:
        count += 1
        last = a

RED = '\033[31m'
RED_BG = '\033[41m'
GREEN = '\033[42m'
BLUE = '\033[34m'
BLUE_BG = '\033[44m'
BLACK = '\033[30m'
YELLOW = '\033[33m'
RESET = '\033[0m'

print(f"{YELLOW}FFfFF{RESET}     v   {BLUE}FFfFF{RESET}")
print(f"{RED_BG}{BLACK}FFfFF{RESET}     v   {BLUE_BG}{BLACK}FFfFF{RESET}")


from colorama import init, Fore, Style
print(f"{Fore.RED}FFfFF{Fore.RESET}     v   {Fore.LIGHTBLUE_EX}{Fore.BLACK}FFfFF{Fore.RESET}")

