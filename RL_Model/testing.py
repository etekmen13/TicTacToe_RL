import json
import numpy as np
with open("./QTables/Qtable_0.json") as file:
    data = json.load(file)

values = []
string = "OX   X O "
for i in range(9):
    if string[i] != ' ':
        continue
    values.append(data.get(string+ str(i),-10))
    print(i, data.get(string+ str(i),-10))
print()
print(np.argmax(values),max(values))
print(np.argmin(values),min(values))