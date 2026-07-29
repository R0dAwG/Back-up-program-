#*************************************************************
#*
#* AUTHOR: R.DOUGLAs
#* DATE: 29/07/2026
#* PURPOSE: SCRIPT FOR BACK UP PROGRAM FEAUTING AUTOMATIC BACK UP OF JOB's & MANUAL INPUT WITH SLI ARGUMENTS
#* VERSION: 6.0
#* FINAL COMPLETED SCRIPT
#* PROGRAMMING LANGUAGE: PYTHON
#* IDE/CODE EDITOR: VS CODE & AWS
#* OPERATING SYSTEM: WINDOWS & UBUNTU LINUX
#*
#*************************************************************



#!/usr/bin/env python3  #Shebang included for Unix based operating systems such as Linux Distros and Mac OS

import os #This module will allow the program to interact with the operating system
import sys #Used to interact with the python interpreter
import shutil #This module is for high-level file and directory operations
import datetime #Used to create and modify dates and times including current dates and times
import traceback #will provides tools to caputre and display error information
import smtplib #This module is used to let python send emails using the smtp protocol
from email.mime.text import MIMEText #used to create the email message content in plain text
import backupcfg #imports the back up module


# Utility Functions

def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S") #This will return the current date and time as a formatted timestamp.


def log_message(message):
    with open(backupcfg.LOG_FILE, "a") as log_file: #Writes a log message to the log file.
        log_file.write(message + "\n")


def send_alert(subject, body):
    """Send email alert on failure with timestamp""" #Sends an email alert when failure occurs with included timestamp.

    if not backupcfg.EMAIL_SETTINGS["enabled"]:  #this will check if email alerts are disabled 
        return

    try:
       
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Creates a timestamp for logging if a error occured
        full_body = f""" 

Backup Error Report 

Time: {timestamp} 

Details:
{body}    
"""

        msg = MIMEText(full_body) 
        msg["Subject"] = subject
        msg["From"] = backupcfg.EMAIL_SETTINGS["sender_email"]   #this will define the sender address for the email alert and the emails header
        msg["To"] = backupcfg.EMAIL_SETTINGS["receiver_email"]

        server = smtplib.SMTP(
            backupcfg.EMAIL_SETTINGS["smtp_server"], #Connects to the smtp server for gmail
            backupcfg.EMAIL_SETTINGS["smtp_port"]
        )
        server.starttls()
        server.login(
            backupcfg.EMAIL_SETTINGS["sender_email"], #This will log into the stmp server using the users credentials
            backupcfg.EMAIL_SETTINGS["sender_password"]
        )

        server.send_message(msg) #This will close the connection to the server
        server.quit() #ends the sesion

    except Exception as e:
        log_message(f"{get_timestamp()} FAIL Email Error: {str(e)}") #if a exception occurs this will catch it and convert it to a error 


# Core Backup Logic

def perform_backup(source, destination, job_name="manual"): #This will handle the file backup process
    timestamp = get_timestamp() #The back up is being time stamped.

    if not os.path.exists(source):
        raise FileNotFoundError(f"Source does not exist: {source}") #this will heck if the source past exists before coninuning 

    if not os.path.exists(destination): #This will create a desination folder if it does not exist 
        os.makedirs(destination)

    base_name = os.path.basename(source.rstrip("\\/"))
    dest_path = os.path.join(destination, f"{base_name}-{timestamp}") #This will create a back up destination path with a timestamp

    if os.path.isdir(source): #Checks if source is a directory before making a copy
        shutil.copytree(source, dest_path)
    else:
        shutil.copy2(source, dest_path) #Copies as single file to the back up destinaiton 

    return dest_path #returns the path of the created back up


# Manual Input Mode


def manual_backup(): 
    print("\n--- Manual Backup Mode ---") #Displays manual backup mode within terminal 

    source = input("Enter source file/directory path: ").strip() #Takes user input for the file path and cleans the user input for the source path
    destination = input("Enter destination directory: ").strip() #Gets destination directory path from the user

    try:
        result = perform_backup(source, destination, "manual") #runs the manual back up and stores the retruned back up path

        message = f"{get_timestamp()} SUCCESS Manual backup completed -> {result}" #Creates the success messsage for the compelted back up
        print(message)
        log_message(message)

    except Exception as e:
        error_details = traceback.format_exc()
        message = f"{get_timestamp()} FAIL Manual backup failed\n{error_details}" #Creates a error message if the back up has failed

        print(message) #displays the output message
        log_message(message) #stores message in a log file

        send_alert("Backup FAILED (Manual)", message) #sends email alert for manual back up failure


# Job-Based Backup 

def run_job(job_name): #Runs a back up job and handles success or failure
    try:
        if job_name not in backupcfg.BACKUP_JOBS: #This will ensure that the job exists in the back up configuration
            raise ValueError(f"Job '{job_name}' not found.")

        job = backupcfg.BACKUP_JOBS[job_name] #This will retreive the job configuration from the back up settings, back up config named job for the variable 

        result = perform_backup(  #This will run the back up using the job configuration
            job["source"],
            job["destination"],
            job_name
        )

        message = f"{get_timestamp()} SUCCESS Job '{job_name}' -> {result}" #Creates success message for the completed back up job
        print(message) #Displays output to the user
        log_message(message) #logs the output

    except Exception as e:          
        error_details = traceback.format_exc()
        message = f"{get_timestamp()} FAIL Job '{job_name}' failed\n{error_details}"    #Creates the failure message with traceback

        print(message) #Display output to the user 
        log_message(message) #logs the output

        send_alert(f"Backup FAILED ({job_name})", message) #Sends email alert to the user of the failed back up


def main(): #Handles CLI input and runs the back up job 

    if len(sys.argv) > 1:
        job_name = sys.argv[1] #Varilable to get job name to run from the CLI argument 
        run_job(job_name)

    else:
        
        if hasattr(backupcfg, "AUTO_RUN_DEFAULT_JOB"): #Runs default backup jbo if no CLI argument is provided
            print("Running automatic backup...")
            run_job(backupcfg.AUTO_RUN_DEFAULT_JOB)

       
        manual_backup() #Runs manual backup mode


if __name__ == "__main__": #Entry point when the program is run by the user
    main()
