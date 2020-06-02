names = ['Daniel', 'Lohana', 'Ana', 'pedro', 'ivi', 'Mimi', 'Yokoyama', 'Navio']

for name in names:
    if len(name) > 5:
        print(len(name))
    if 'n' in name or 'N' in name:
        print(name + ' constains n')

while len(names) > 0:
    print(names.pop())