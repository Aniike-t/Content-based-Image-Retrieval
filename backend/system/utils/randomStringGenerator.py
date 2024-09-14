import random
import string

def generate_random_string(length):
    """Generate an alphanumeric random string of the specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))