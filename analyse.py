import json

with open("resultado2.log.copy.txt", "r") as logfile:
    lines = logfile.readlines()

anterior = ""
last_type = ""
new_type = ""
tps = {}
cont = -1
name = "Runtime"
show = True
m111 = json.loads(
    lines[0].replace("\n", "").replace("<", "\"").replace(">", "\"").replace("\'", "\"").replace("None",
                                                                                                 "\"None\"").strip())

m111.pop(name)
for line in lines:
    if "Type" in line:
        new_type = line.replace("\n", "").strip().split(" ")[-1]
    if new_type != last_type:
        last_type = new_type
        # print("\n")
        # break #somente avaliar os do tipo 1
        cont += 1
        if cont == 1:
            break

    if name in line:
        year = json.loads(
            line.replace("\n", "").replace("<", "\"").replace(">", "\"").replace("\'", "\"").replace("None",
                                                                                                     "\"None\"").strip())[
            name]
        m22 = json.loads(
            line.replace("\n", "").replace("<", "\"").replace(">", "\"").replace("\'", "\"").replace("None",
                                                                                                     "\"None\"").strip())
        m22.pop(name)
        if m111 == m22:
            print("x")
        if year not in tps:
            tps[year] = []

    if "---" in line:
        if "---" in anterior:
            break
        if "erro" in anterior:
            tps[year].append(anterior)
            # print("e\t", end="")
        else:
            # print(anterior + "\t", end="")
            tps[year].append(anterior)
    anterior = line.replace("\n", "").strip()

# tps[-1] = tps[-1][:-1]
# print(tps)
size = 0
for j in tps:
    size = len(tps[j])

keyss = tps.keys()
all_lines_ok = []
num_not_ok = 0
for i in range(size):
    rs = []
    for j in keyss:
        try:
            if tps[j][i] == "nan":
                raise Exception
            r = float(tps[j][i])
            rs.append(r)
        except:
            pass
    if len(rs) == len(tps):
        all_lines_ok.append(rs)
    else:
        num_not_ok += 1
print(num_not_ok)

import matplotlib.pyplot as plt
import numpy as np

nkeeis = []
for i in keyss:
    if "thing" in i:
        nkeeis.append("Without")
    elif i == ",":
        nkeeis.append("Unigram")
    elif "Bigram" in i:
        nkeeis.append("Bigram")
    elif "None" in i:
        nkeeis.append("Without\nInterval")
    elif "interval" in i:
        nkeeis.append("Using\nInterval")

plt.figure(figsize=(3.5 * 1, 2.5 * 1))
plt.ylabel("RMSE", fontdict={"fontsize": 8})
plt.boxplot(np.array(all_lines_ok), showfliers=False, )
# plt.axhline(2.84, -3, 3, ls='--', lw=0.8, color='k')
# plt.xticks((1, 2, 3), nkeeis)
plt.xticks(range(1, len(nkeeis) + 1), nkeeis)
# plt.xticks((1, 2, 3), ("User Mean", "Reescal\nMin.Max", "Reescal"))
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.title("Impact of " + name, fontdict={"fontsize": 8})
plt.tight_layout()

if show:
    plt.show()
print(keyss)

if not show:
    plt.savefig("impact_"+name+".png", dpi=200)
