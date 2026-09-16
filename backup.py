


#Shebang included for Unix based operating systems such as Linux Distros and Mac OS
#!/usr/bin/env python3


"""
 AUTHOR: R.DOUGLAS
 DATE: 29/07/2026
 PURPOSE: SCRIPT FOR BACK UP PROGRAM FEAUTING AUTOMATIC BACK UP OF JOB's & MANUAL INPUT WITH SLI ARGUMENTS
 VERSION: 6.2
 FINAL COMPLETED SCRIPT
 PROGRAMMING LANGUAGE: PYTHON
 IDE/CODE EDITOR: VS CODE & AWS
 OPERATING SYSTEM: WINDOWS & UBUNTU LINUX 
                                      """

#This module will allow the program to interact with the operating system
import os 
#Used to interact with the python interpreter
import sys
#This module is for high-level file and directory operations
import shutil 
#Used to create and modify dates and times including current dates and times
import datetime 
#will provides tools to caputre and display error information
import traceback 
#This module is used to let python send emails using the smtp protocol
import smtplib 
#used to create the email message content in plain text
from email.mime.text import MIMEText 
#imports the back up module
import backupcfg 


# Utility Functions

#This will return the current date and time as a formatted timestamp.
def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S") 

#Writes a log message to the log file.
def log_message(message):
    with open(backupcfg.LOG_FILE, "a") as log_file: 
        log_file.write(message + "\n")

#Sends an email alert when failure occurs with included timestamp.
def send_alert(subject, body):
    """Send email alert on failure with timestamp""" 

    #this will check if email alerts are disabled
    if not backupcfg.EMAIL_SETTINGS["enabled"]:   
        return

    try:
       #Creates a timestamp for logging if a error occured
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        full_body = f""" 

Backup Error Report 

Time: {timestamp} 

Details:
{body}    
"""

        msg = MIMEText(full_body) 
        msg["Subject"] = subject
        #this will define the sender address for the email alert and the emails header
        msg["From"] = backupcfg.EMAIL_SETTINGS["sender_email"]   
        msg["To"] = backupcfg.EMAIL_SETTINGS["receiver_email"]

        server = smtplib.SMTP(
            #Connects to the smtp server for gmail
            backupcfg.EMAIL_SETTINGS["smtp_server"], 
            backupcfg.EMAIL_SETTINGS["smtp_port"]
        )
        server.starttls()
        server.login(
            #This will log into the stmp server using the users credentials
            backupcfg.EMAIL_SETTINGS["sender_email"], 
            backupcfg.EMAIL_SETTINGS["sender_password"]
        )
#This will close the connection to the server
        server.send_message(msg) 
        server.quit() #ends the sesion
#if a exception occurs this will catch it and convert it to a error 
    except Exception as e:
        log_message(f"{get_timestamp()} FAIL Email Error: {str(e)}") 

# Core Backup Logic

#This will handle the file backup process
def perform_backup(source, destination, job_name="manual"): 
    #The back up is being time stamped.
    timestamp = get_timestamp() 

    if not os.path.exists(source):
        #this will heck if the source past exists before coninuning 
        raise FileNotFoundError(f"Source does not exist: {source}") 

#This will create a desination folder if it does not exist
    if not os.path.exists(destination):  
        os.makedirs(destination)

    base_name = os.path.basename(source.rstrip("\\/"))
    #This will create a back up destination path with a timestamp
    
    dest_path = os.path.join(destination, f"{base_name}-{timestamp}") 
    #Checks if source is a directory before making a copy
    if os.path.isdir(source): 
        shutil.copytree(source, dest_path)
    else:
        #Copies as single file to the back up destinaiton
        shutil.copy2(source, dest_path)  

    return dest_path #returns the path of the created back up


# Manual Input Mode


def manual_backup(): 
    #Displays manual backup mode within terminal 
    print("\n--- Manual Backup Mode ---") 
    #Takes user input for the file path and cleans the user input for the source path
    source = input("Enter source file/directory path: ").strip() 
    #Gets destination directory path from the user
    destination = input("Enter destination directory: ").strip() 

    try:
        #runs the manual back up and stores the retruned back up path
        result = perform_backup(source, destination, "manual") 
        #Creates the success messsage for the compelted back up
        message = f"{get_timestamp()} SUCCESS Manual backup completed -> {result}" 
        print(message)
        log_message(message)

    except Exception as e:
        error_details = traceback.format_exc()
        #Creates a error message if the back up has failed
        message = f"{get_timestamp()} FAIL Manual backup failed\n{error_details}" 
        #displays the output message
        print(message) 
        #stores message in a log file
        log_message(message) 
        #sends email alert for manual back up failure

        send_alert("Backup FAILED (Manual)", message) 

# Job-Based Backup 

#Runs a back up job and handles success or failure
def run_job(job_name): 
    try:
        #This will ensure that the job exists in the back up configuration
        if job_name not in backupcfg.BACKUP_JOBS: 
            raise ValueError(f"Job '{job_name}' not found.")
        #This will retreive the job configuration from the back up settings, back up config named job for the variable
        job = backupcfg.BACKUP_JOBS[job_name]  
        #This will run the back up using the job configuration
        result = perform_backup(  
            job["source"],
            job["destination"],
            job_name
        )
        #Creates success message for the completed back up job
        message = f"{get_timestamp()} SUCCESS Job '{job_name}' -> {result}" 
        #Displays output to the user
        print(message) 
        log_message(message) #logs the output

    except Exception as e:          
        error_details = traceback.format_exc()
        #Creates the failure message with traceback
        message = f"{get_timestamp()} FAIL Job '{job_name}' failed\n{error_details}"    
        #Display output to the user 
        print(message) 
        #logs the output
        log_message(message) 
        #Sends email alert to the user of the failed back up

        send_alert(f"Backup FAILED ({job_name})", message) 
        #Handles CLI input and runs the back up job 

def main(): 
    if len(sys.argv) > 1:
        #Varilable to get job name to run from the CLI argument
        job_name = sys.argv[1]  
        run_job(job_name)

    else:
        #Runs default backup jbo if no CLI argument is provided
        if hasattr(backupcfg, "AUTO_RUN_DEFAULT_JOB"): 
            print("Running automatic backup...")
            run_job(backupcfg.AUTO_RUN_DEFAULT_JOB)

       #Runs manual backup mode
        manual_backup() 

#Entry point when the program is run by the user
if __name__ == "__main__": 
    main()
