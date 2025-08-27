
import configparser
import os

def get_registration_data(ini_path=None):
    if ini_path is None:
        ini_path = os.path.join(os.path.dirname(__file__), 'registration_data.ini')
    config = configparser.ConfigParser()
    config.read(ini_path)
    user = config['user']
    return {
        'username': user['username'],
        'email': user['email'],
        'password': user['password'],
        'url': user.get('url', 'http://127.0.0.1:8000/register')
    }

# Example usage
if __name__ == "__main__":
    data = get_registration_data()
    print(data)
