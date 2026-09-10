#*************************************************************
#*
#* AUTHOR: R.DOUGLAS
#* Contact Email: Rohandouglas01@gmail.com
#* DATE: 29/07/2026
#* PURPOSE: SCRIPT FOR BACK UP PROGRAM FEAUTING AUTOMATIC BACK UP OF JOB's & MANUAL INPUT WITH SLI ARGUMENTS, intended for automatic back up's for clients who are wanting a program to complete back ups of files and directories.
#* VERSION: 6.1
#* FINAL COMPLETED SCRIPT
#* PROGRAMMING LANGUAGE: PYTHON
#* IDE/CODE EDITOR: VS CODE & AWS
#* OPERATING SYSTEM: WINDOWS & UBUNTU LINUX
#*
#*************************************************************



#!/usr/bin/env python3
"""shebang included for Unix Environments"""



import os 
import sys
import shutil 
import datetime 
import traceback 
import smtplib 
from email.mime.text import MIMEText 
import backupcfg 


# Utility Functions


def get_timestamp():
    """Creates a standarized timestamp string for files and logs.
Returns:
    str: Current date and time.
"""
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S") 
    



def log_message(message):
    """Add a message to the log file/folder.

    Args:
        str: The log event text to be recorded.
    """
    with open(backupcfg.LOG_FILE, "a") as log_file: 
        log_file.write(message + "\n")


def send_alert(subject, body):
    """Send email alert on failure with timestamp.

    Args:
        str: The subject line of the email.
        Alert body (str): detailed error details.
    """

    if not backupcfg.EMAIL_SETTINGS["enabled"]:   
        return

    try:
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

def perform_backup(source, destination, job_name="manual"): 
    """Performs the copy operation fromm the source to the destination.

    Handles both single files and deep directories. Creates a timestamp
    to the destination to prevent accidental overwrites

    Args:
        source (str): File system path to the file/directory being backed up.
        destination (str): Directory where the back up should be stored.
        job_name (str, optional): Identity of the calling job. Defaults to "Manual".

    Returns:
         str: The exact destination path of the newly created backup.

    Raises:
        FileNotFoundError: If the source path does not exist on the system.
"""
    timestamp = get_timestamp() 

    if not os.path.exists(source):
        raise FileNotFoundError(f"Source does not exist: {source}") 
    if not os.path.exists(destination):  
        os.makedirs(destination)

    base_name = os.path.basename(source.rstrip("\\/"))
    dest_path = os.path.join(destination, f"{base_name}-{timestamp}") 
    
    if os.path.isdir(source): 
        shutil.copytree(source, dest_path)
    else:
        shutil.copy2(source, dest_path)  

    return dest_path 


# Manual Input Mode


def manual_backup(): 

    """Prompt the user for manual inputs to run a back up of any file or directory or the program its self.

    Captures interactive terminal entries, runs the operation safely,
    and logs success or outputs failures to the terminal/console and email error alert.
    """
    
    print("\n--- Manual Backup Mode ---") 

    source = input("Enter source file/directory path: ").strip() 

    destination = input("Enter destination directory: ").strip() 

    try:
        result = perform_backup(source, destination, "manual") 

        message = f"{get_timestamp()} SUCCESS Manual backup completed -> {result}" 
        print(message)
        log_message(message)

    except Exception as e:
        error_details = traceback.format_exc()
        
        message = f"{get_timestamp()} FAIL Manual backup failed\n{error_details}" 

        print(message) 
       
        log_message(message) 


        send_alert("Backup FAILED (Manual)", message) 

# Job-Based Backup 

def run_job(job_name): 
    """Retrieve settings for and perform a pre-configured back up

    Args:
        Job_name (str): Key mapping to a job in the backupcfg configuration.
    
    Raises:
         ValueError: If the requested job identity is missing from the configuration.
    """

    try:
        
        if job_name not in backupcfg.BACKUP_JOBS: 
            raise ValueError(f"Job '{job_name}' not found.")

        job = backupcfg.BACKUP_JOBS[job_name]  

        result = perform_backup(  
            job["source"],
            job["destination"],
            job_name
        )

        message = f"{get_timestamp()} SUCCESS Job '{job_name}' -> {result}" 
        
        print(message) 
        log_message(message) 
    except Exception as e:          
        error_details = traceback.format_exc()
        
        message = f"{get_timestamp()} FAIL Job '{job_name}' failed\n{error_details}"    

        print(message) 
       
        log_message(message) 


        send_alert(f"Backup FAILED ({job_name})", message) 


def main(): 
    """Evaluate system arguments and driect script execution flow.

    Prioritises CLI arguments first. Falls back on automatic back up/default program profile
    and will route to manual mode otherwise.
    """
    if len(sys.argv) > 1:
        
        job_name = sys.argv[1]  
        run_job(job_name)

    else:
       
        if hasattr(backupcfg, "AUTO_RUN_DEFAULT_JOB"): 
            print("Running automatic backup...")
            run_job(backupcfg.AUTO_RUN_DEFAULT_JOB)

       
        manual_backup() 


if __name__ == "__main__": 
    main()
