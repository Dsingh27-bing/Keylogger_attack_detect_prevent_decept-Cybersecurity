import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess

# secret key generated once and is reused for future as we want to decrypt the stored file multiple times in multiple sessions
SECRET_KEY_FILE = "secret_key.key"

def load_or_generate_secret_key(): #generate secret key 
    try:
        # Try to load the secret key from a file
        with open(SECRET_KEY_FILE, "rb") as key_file:
            secret_key = key_file.read()
    except FileNotFoundError:
        # If the file doesn't exist, generate a new secret key and save it
        secret_key = Fernet.generate_key()
        with open(SECRET_KEY_FILE, "wb") as key_file:
            key_file.write(secret_key)
    return secret_key

secret_key = load_or_generate_secret_key()
cipher_suite = Fernet(secret_key) #this is for encryption and decryption of stored username passwords

#for running the detection tool and to eliminate the keylogger program
def run_keylogger_detection():
    try:
        completed_process = subprocess.run(["sudo", "python3", "detection.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("Detection script output:")
        print(completed_process.stdout)
        print(completed_process.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")



def get_password_and_run_detection():
    run_keylogger_detection()
    get_password()

def autofill_and_run_detection():
    run_keylogger_detection()
    autofill()

# Specific email for sending secret codes (OTP)
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # Use the appropriate SMTP port
smtp_sender_email = 'bingstudent0@gmail.com'
smtp_sender_password = 'osdpkriqgzsziayf'  

#Fantastic-Pipe-960, Bing@student2023 --- reddit user id and password created only for project purpose

login_url = 'https://www.reddit.com/login/'  # login page URL

def generate_secret_code():  #generation of secret code (OTP) with random numbers
    # Generate a random 6-digit secret code
    return str(random.randint(100000, 999999))

def send_secret_code(email, secret_code):     # Send the secret code(OTP) to the user's email
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    subject = "Your Secret Code"
    message = f'Your secret code is: {secret_code}'
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_sender_email, smtp_sender_password)
            msg = MIMEMultipart()
            msg['From'] = smtp_sender_email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server.sendmail(smtp_sender_email, email, msg.as_string())
        return True
    except Exception as e:
        return False

def generate_key():
    return secret_key

def encrypt_password(key, password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(key, encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def store_account(service, username, password):
    with open("account_info.txt", "a") as file:
        encrypted_username = encrypt_password(secret_key, username)
        encrypted_password = encrypt_password(secret_key, password)
        file.write(f"{service}:{encrypted_username}:{encrypted_password}\n")

def retrieve_account(service):
    with open("account_info.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(":")
            if len(parts) == 3 and parts[0] == service:
                decrypted_username = decrypt_password(secret_key, parts[1])
                decrypted_password = decrypt_password(secret_key, parts[2])
                return decrypted_username, decrypted_password
        return None, None

def autofill_login(username, password):  #autofilling of username and password for particular url
    try:
        driver = webdriver.Firefox()
        driver.get(login_url)

        # Find and autofill the username and password fields using CSS selectors
        username_field = driver.find_element(By.CSS_SELECTOR, 'input#loginUsername') #found loginUsername field input id from developer tool in the url
        password_field = driver.find_element(By.CSS_SELECTOR, 'input#loginPassword')

        # Enter the username and password
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Submit the form (if necessary, modify the element locator accordingly)
        password_field.submit()

        # Wait for the login to complete (you can add more code to detect successful login)
        driver.implicitly_wait(10)

    except Exception as e:
        print(f"Autofill failed: {e}")
    # finally:
    #     # Close the browser window   # not using this because closes the window
    #     driver.quit()

def autofill(): #retrieving username and password for autofill function
    service = service_entry.get()
    if service:
        username, password = retrieve_account(service)
        if username and password:
            autofill_login(username, password)
        else:
            messagebox.showwarning("Error", "Password not found.")

def add_password(): #function to add account name, password and username details 
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if service and username and password:
        store_account(service, username, password)
        messagebox.showinfo("Success", "Password added successfully!")
    else:
        messagebox.showwarning("Error", "Please fill in all the fields.")


def get_password(): #function for fetching password and username for particular account name and 2MFA used for fetching password and username. Usser needs to enter OTP in order to see the password and username. 
    def verify_2mfa():
        entered_2mfa = entered_2mfa_entry.get()
        if entered_2mfa:
            service = service_entry.get()
            if entered_2mfa == secret_code:  # Verify secret_code
                username, encrypted_password = retrieve_account(service)
                if username and encrypted_password:
                    decrypted_password = encrypted_password
                    messagebox.showinfo("Password", f"Username: {username}\nPassword: {decrypted_password}")
                else:
                    messagebox.showwarning("Error", "Password not found.")
                second_window.destroy()
            else:
                messagebox.showwarning("Error", "Invalid 2MFA code.")

    service = service_entry.get()
    if service: #if get password is clicked then new window opens for 2MFA verification
        global secret_code  # Declared it as a global variable
        secret_code = generate_secret_code() 
        second_window = tk.Toplevel()
        second_window.title("Enter 2MFA")
        second_window.geometry("300x150")

        entered_2mfa_label = tk.Label(second_window, text="2MFA Code:")
        entered_2mfa_label.pack()
        entered_2mfa_entry = tk.Entry(second_window, show="*")
        entered_2mfa_entry.pack()

        verify_button = tk.Button(second_window, text="Verify", command=verify_2mfa)
        verify_button.pack()
        send_secret_code(smtp_sender_email, secret_code)

key = generate_key()

instructions = '''To add a password, fill in all the fields and press "Add Password".
To view a password, enter the Account Name and press "Get Password. Then enter the secret code to fetch the password"'''

# GUI code

window = tk.Tk()
window.title("Password Manager")
window.configure(bg="blue")
window.resizable(False, False)

center_frame = tk.Frame(window, bg="#d3d3d3")
center_frame.grid(row=0, column=0, padx=10, pady=10)

instruction_label = tk.Label(center_frame, text=instructions, bg="#d3d3d3")
instruction_label.grid(row=0, column=1, padx=10, pady=5)

service_label = tk.Label(center_frame, text="Account:", bg="#d3d3d3")
service_label.grid(row=1, column=0, padx=10, pady=5)
service_entry = tk.Entry(center_frame)
service_entry.grid(row=1, column=1, padx=10, pady=5)

username_label = tk.Label(center_frame, text="Username:", bg="#d3d3d3")
username_label.grid(row=2, column=0, padx=10, pady=5)
username_entry = tk.Entry(center_frame)
username_entry.grid(row=2, column=1, padx=10, pady=5)

password_label = tk.Label(center_frame, text="Password:", bg="#d3d3d3")
password_label.grid(row=3, column=0, padx=10, pady=5)
password_entry = tk.Entry(center_frame, show="*")
password_entry.grid(row=3, column=1, padx=10, pady=5)

# Bind the run_keylogger_detection function to "FocusIn" event for the username and password entry fields
username_entry.bind("<FocusIn>", lambda event: run_keylogger_detection())
password_entry.bind("<FocusIn>", lambda event: run_keylogger_detection())


add_password_button = tk.Button(center_frame, text="Add Password", command= add_password, height=1, width=10)
add_password_button.grid(row=5, column=4, padx=10, pady=5)

get_password_button = tk.Button(center_frame, text="Get Password", command=get_password_and_run_detection, height=1, width=10)
get_password_button.grid(row=6, column=4, padx=10, pady=5)

autofill_button = tk.Button(center_frame, text="Autofill", command=autofill_and_run_detection, height=1, width=10)
autofill_button.grid(row=7, column=4, padx=10, pady=5)

# Starting the GUI application
window.mainloop()
