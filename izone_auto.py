import os  
import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoSuchWindowException, WebDriverException

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
    return None, None  # Return None if file doesn't exist or is incomplete

# Function to delete credentials
def delete_credentials():
    if os.path.exists(credentials_file):
        os.remove(credentials_file)
        status_label.config(text="Credentials deleted.", fg="blue")
 

# Function to check if the browser window is still open
def is_browser_window_open():
    try:
        driver.current_url  # Try accessing the current URL to see if the window is still open
        return True
    except (NoSuchWindowException, WebDriverException):
        return False

# Function to ensure user is logged in
def ensure_logged_in():
    try:
        # Check for an element that only appears when logged in
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "iCheckInUrl")))
        return True
    except (NoSuchElementException, TimeoutException):
        return False

# Function to log in
def login(auto_login=False):
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    
    if not username:
        if not auto_login:  # Only show this if it's not an auto-login
            status_label.config(text="Please enter a username.")
        return False
    if not password:
        if not auto_login:  # Only show this if it's not an auto-login
            status_label.config(text="Please enter a password.")
        return False
    
    try:
        driver.get(url)
        
        # Wait for the username field and enter credentials
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "student_uid"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.ID, "submit").click()

        try:
            # Wait for the successful login indicator
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "iCheckInUrl")))
            status_label.config(text="Login successful.", fg="green")
            check_in_button.config(state=tk.NORMAL)
            
            if remember_var.get() == 1:
                save_credentials(username, password)
            else:
                delete_credentials()
                
            return True
        
        except TimeoutException:
            status_label.config(text="Login failed. Check credentials.", fg="red")
            return False
    
    except (NoSuchElementException, TimeoutException):
        status_label.config(text="Login elements not found or page load timed out.", fg="red")
        return False
    except NoSuchWindowException:
        status_label.config(text="Browser window closed unexpectedly during login.", fg="red")
        return False


# Function to check in
def check_in():
    try:
        driver.find_element(By.ID, "iCheckInUrl").click()
        
        check_in_code = check_in_entry.get()
        if not check_in_code:
            status_label.config(text="Please enter the check in code")
            return 

        if not check_in_code.isdigit():
            status_label.config(text="Check-in code must be numeric.", fg ="red")
            return

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "checkin_code"))).send_keys(check_in_code)
            driver.find_element(By.ID, "iCheckin").click()
            
            notification = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "notification"))
            ).text.lower()

            if "not valid" in notification:
                status_label.config(text="Invalid check-in code.", fg="red")
            else:
                status_label.config(text="Check-in successful!")
                driver.quit()
                root.quit()

        except TimeoutException:
            status_label.config(text="Check-in failed. Please try again.")

    except NoSuchElementException:
        status_label.config(text="Check-in button not found.")

# Set up Chrome options to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=800,600")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load saved credentials
saved_username, saved_password = load_credentials()

# Set up the GUI
root = tk.Tk()
root.title("iZone Auto Check-In")

tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5)
username_entry = ttk.Entry(root, width=30)
username_entry.grid(row=0, column=1, padx=10, pady=5)
if saved_username:
    username_entry.insert(0, saved_username)

tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5)
password_entry = ttk.Entry(root, show="*", width=30)
password_entry.grid(row=1, column=1, padx=10, pady=5)
if saved_password:
    password_entry.insert(0, saved_password)

remember_var = tk.IntVar(value=1)
remember_check = tk.Checkbutton(root, text="Remember me", variable=remember_var)
remember_check.grid(row=2, column=0, columnspan=2)

login_button = ttk.Button(root, text="Login", command=lambda: login(auto_login=False))
login_button.grid(row=3, column=0, columnspan=2, pady=10)

tk.Label(root, text="Check-In Code:").grid(row=4, column=0, padx=10, pady=5)
check_in_entry = ttk.Entry(root, width=30)
check_in_entry.grid(row=4, column=1, padx=10, pady=5)

check_in_button = ttk.Button(root, text="Check In", command=check_in)
check_in_button.grid(row=5, column=0, columnspan=2, pady=10)
check_in_button.config(state=tk.DISABLED)

# Add the Delete Credentials button
delete_button = ttk.Button(root, text="Delete Credentials", command=delete_credentials)
delete_button.grid(row=6, column=0, columnspan=2, pady=5)

status_label = tk.Label(root, text="", fg="red")
status_label.grid(row=7, column=0, columnspan=2, pady=5)

# Automatically log in if credentials are saved
if saved_username and saved_password:
    status_label.config(text="Logging in automatically...", fg="blue")
    root.after(1000, lambda: login(auto_login=True))  # Trigger login after 1 second delay

root.mainloop()
