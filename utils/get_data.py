import yaml
from yaml.loader import SafeLoader

def get_data(role):
    role_data = []
    with open('config.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=SafeLoader)
    for username, user_info in data['credentials']['usernames'].items():
            if role in user_info['roles']:
                role_data.append({
                'Username': username,
                'Email': user_info['email'],
                'First Name': user_info['first_name'],
                'Last Name': user_info['last_name']
        })
    return role_data

def get_student_data(username):
    with open('config.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=SafeLoader)
    user_info = data['credentials']['usernames'].get(username)
    if user_info:
        return {
            'Username': username,
            'Email': user_info['email'],
            'First Name': user_info['first_name'],
            'Last Name': user_info['last_name']
            }
    return None