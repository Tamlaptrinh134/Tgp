import random as rd
m = 100 
for i in range(1, m + 1):
    print(f"{round(i/m*100, 2)}% {rd.randint(0, 4)*' '} like")