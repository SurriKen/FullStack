liner = [(3, 3), (4, 3)] # (2, 3) (4, 3)

vec = 0 if liner[0][0] == liner[-1][0] else 1
print(vec)
dot1 = (liner[0][0], liner[0][1] - 1) if vec == 0 else (liner[0][0] - 1, liner[0][1])
print(dot1)
dot2 = (liner[-1][0], liner[-1][1] + 1) if vec == 0 else (liner[-1][0] + 1, liner[-1][1])
print(dot2)