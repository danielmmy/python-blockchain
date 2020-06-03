import json
import pickle

DATA_FILE_PATH = 'data/data.txt'
data_list = []


def save_data():
    data = input('Input: ')
    data_list.append(data)
    try:
        with open(DATA_FILE_PATH, 'wb') as f:
            f.write(pickle.dumps(data_list))
    except:
        print('Error')


def read_data():
    global data_list
    try:
        with open(DATA_FILE_PATH, 'rb') as f:
            data_list = pickle.loads(f.read())
    except:
        print('Error reading data')

while True:
    option = input('Enter option:\n1-Enter data\n2-read data\nq-quit\n')
    if option == '1':
        save_data()
    elif option == '2':
        read_data()
    elif option == 'q':
        print('Exiting...')
        break
    else:
        print('Invalid option {option}'.format())
    print('-'*30)
    print(data_list)
    print('-'*30)
