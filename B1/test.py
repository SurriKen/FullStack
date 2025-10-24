def counter(func):
   count = {}
   def wrapper(num):
       nonlocal count
       if not count.get(num):
           res = func(num)
           count[num] = res
           return res
       else:
           print(f"Для {num} значение {count[num]} взято из словаря")
           return count[num]
   return wrapper

@counter
def f(n):
    return n * 123456789


for i in [1, 2, 3, 4, 5, 1, 6, 8, 15, 2]:
   print(f(i))
   print("----")

print(requests.__version__)
print(bs4.__version__)