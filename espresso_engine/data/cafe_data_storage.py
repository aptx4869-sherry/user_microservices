users = []

def get_user_by_email(email: str):
    """Retrieves a user from the in-memory store by email."""
    for user in users:
        if user["email"] == email:
            return user
    return None

def add_user(user_data: dict):
    """Adds a new user to the in-memory store."""
    users.append(user_data)