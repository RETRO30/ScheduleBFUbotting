

def get_token(file):
    with open(file) as f:
        token = f.readline().strip()
    return token


