import pickle

def restore(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)