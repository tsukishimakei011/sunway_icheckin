import os    
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# File to store the username and password
credentials_file = 'credentials.txt'
url = "https://izone.sunway.edu.my/login"
service = Service(r"C:/Users/RACHEL LAM/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")

# Function to save credentials
def save_credentials(username, password):
    with open(credentials_file, 'w') as file:
        file.write(f"{username}\n{password}")

# Function to load saved credentials
def load_credentials():
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as file:
            credentials = file.readlines()
            if len(credentials) >= 2:
                return credentials[0].strip(), credentials[1].strip()  # username, password
    return None, None  # Return None if file doesn't exist or is empty/incomplete

# Function to delete credentials
def delete_credentials():
    if os.path.exists(credentials_file):
        os.remove(credentials_file)

# Function to log in
def login(driver, username, password):
    driver.get(url)
    driver.find_element(By.ID, "student_uid").clear()
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "student_uid").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.ID, "submit").click()

    try:
        driver.find_element(By.ID, "msg")  # Adjust ID for error message
        return False  # Login failed
    except NoSuchElementException:
        print("Logged in successfully.")
        return True  # Login successful

# Set up Chrome options to run in headless mode with 50x50 window size
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage for headless mode
chrome_options.add_argument("--no-sandbox")  # Disable the sandbox for headless mode
chrome_options.add_argument("--window-size=800,600")  

# Initialize WebDriver with headless and window size options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Attempt to load saved credentials
saved_username, saved_password = load_credentials()

if saved_username and saved_password:
    # If credentials are found, try to log in
    print("Logging in with saved credentials...")
    if login(driver, saved_username, saved_password):
        print("Logged in using saved credentials.")
    else:
        print("Saved credentials are incorrect.")
else:
    # Ask user for credentials if none are saved
    print("No saved credentials found. Please enter your credentials.")
    while True:
        username = input("Please enter the username: ")
        if not username:
            print("Warning: Username cannot be empty. Please enter a valid username.")
            continue

        password = input("Please enter the password: ")
        if not password:
            print("Warning: Password cannot be empty. Please enter your password.")
            continue

        # Try logging in with provided credentials
        if login(driver, username, password):
            # Ask the user if they want to save the credentials
            save_choice = input("Do you want to save your username and password for next time? (y/n): ").lower()
            if save_choice == 'y':
                save_credentials(username, password)
                print("Credentials saved.")
            else:
                delete_credentials()  # Remove saved credentials if they exist
                print("Credentials will not be saved.")
            break  # Exit loop on successful login
        else:
            print("Wrong UserID or Password. Please try again.")

# Proceed with check-in after successful login
driver.find_element(By.ID, "iCheckInUrl").click()

# Loop until the correct check-in code is entered or user types "keluar"
while True:
    checkIn = input("Please enter the check-in code (or type 'keluar' to exit): ")
    
    # Exit condition
    if checkIn.lower() == 'keluar':
        print("Exiting the program.")
        driver.quit()
        exit()  # Exit the program
    
    # Validation: Check if the input is numeric
    if not checkIn.isdigit():
        print("Warning: The check-in code must be a number. Please try again.")
        continue  # Go back to the start of the loop to prompt the user again

    # Proceed with check-in if input is valid
    driver.find_element(By.ID, "checkin_code").clear()
    driver.find_element(By.ID, "checkin_code").send_keys(checkIn)
    driver.find_element(By.ID, "iCheckin").click()

    try:
        # Check for the notification element
        notification_element = driver.find_element(By.ID, "notification")
        notification_text = notification_element.text.lower()  # Get the notification text and convert to lowercase
        
        # Determine success or failure based on the text content
        if "not valid" in notification_text:  # Adjust this string based on the actual error message
            print("Wrong CheckIn Code, please enter the check-in code again.")
        else:
            print("Check in successfully!")
            driver.quit()  # Close the browser automatically
            exit()  # Exit the program automatically
    except NoSuchElementException:
        print("Unexpected error. Please check your connection or the check-in system.")
ke