import pickle


def get_stats_from_file():
    with open('stats/user.pkl', 'rb') as f:
        loaded_dict = pickle.load(f)
        return loaded_dict

def save_stats_to_file(dictionary):
    with open('stats/user.pkl', 'wb') as f:
        pickle.dump(dictionary, f)


def view_stats():
    print(get_stats_from_file())


if __name__ == "__main__":
    view_stats()