# Backup job definitions

BACKUP_JOBS = {
    "job1": {
        "source": "C:/Users/rohan/Desktop/backup_project",
        "destination": "C:/Users/rohan/Desktop/backups"
    }
}

LOG_FILE = "backup.log"

EMAIL_SETTINGS = {
    "enabled": True,  # ✅ turn this ON
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "rohandouglas01@gmail.com",
    "sender_password": "uxev ednw wzqz bwtj",
    "receiver_email": "rohandouglas01@gmail.com"
}


AUTO_RUN_DEFAULT_JOB = "job1"