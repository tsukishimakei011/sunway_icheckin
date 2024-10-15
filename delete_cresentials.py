# Function to clear the contents of the credentials file
def clear_credentials():
    with open('credentials.txt', 'w') as file:
        file.write("")  # Overwrite with an empty string
    print("Credentials cleared.")

# Call the function to clear the file
clear_credentials()
