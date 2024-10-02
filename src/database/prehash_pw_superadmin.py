from passlib.context import CryptContext

# Set up CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the password to hash
password_to_hash = "YourStaticSuperAdminPassword"  # Replace with your desired password

# Hash the password
hashed_password = pwd_context.hash(password_to_hash)

# Print the hashed password
print("Hashed Password:", hashed_password)
