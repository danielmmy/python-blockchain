class Food:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind


    def describe(self):
        print('Name: {}, Kind: {}'.format(self.name, self.kind))


    def __repr__(self):
        return 'Name: {}, Kind: {}'.format(self.name, self.kind)


class Fruit(Food):
    def clean(self):
        print('Cleaning {}'.format(self.name))


class Meat(Food):
    def cook(self):
        print('Cooking {}'.format(self.name))




    
food = Food('comida', 'boa')
food.describe()
apple = Fruit('apple', 'fruit')
apple.clean()
apple.describe()
steak = Meat('steak', 'meat')
steak.describe()
steak.cook()
print(food, apple, steak)