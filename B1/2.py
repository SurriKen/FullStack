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

