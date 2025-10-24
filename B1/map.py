L = ['THIS', 'IS', 'LOWER', 'STRING']

print(list(map(str.lower, L)))

# Из заданного списка вывести только положительные элементы
def positive(x):
    return x > 0  # функция возвращает только True или False

def odd(x):
    return x % 2 == 1

def even(x):
    return x % 2 == 0

print(list(filter(positive, [-2, -1, 0, 1, -3, 2, -3])))
print(list(filter(odd, [1, 2, 3, 4])))
print(list(filter(even, [-3, -2, -1, 0, 1, 2, 3])))


# map + filter
some_list = [i - 10 for i in range(20)]
def pow2(x): return x**2
def positive(x): return x > 0

print(some_list)
print(list(map(pow2, filter(positive, some_list))))

a = ["asd", "bbd", "ddfa", "mcsa"]
print(list(map(len, a)))