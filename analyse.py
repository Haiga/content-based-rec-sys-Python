with open("log.txt", "r") as logfile:
    lines = logfile.readlines()

anterior = ""
last_type = ""
new_type = ""
for line in lines:
    if "Type" in line:
        new_type = line.replace("\n", "").strip().split(" ")[-1]
    if new_type != last_type:
        last_type = new_type
        print("\n")
    if "---" in line:
        if "erro" in anterior:
            print("e\t", end="")
        else:
            print(anterior + "\t", end="")
    anterior = line.replace("\n", "").strip()
