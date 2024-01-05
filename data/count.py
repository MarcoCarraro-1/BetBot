f = open("nlu.yml", "r")
counter = 0
for line in f:
    if 'intent' not in line:
        if 'examples' not in line:
            if 'version' not in line:
                if 'nlu' not in line:
                    counter += 1
print(counter)