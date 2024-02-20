# Automated Backup

## Performs the backup of a local folder to Google Drive without needing user input.

This python script was written to stop spending your precious time on performing the mindless task of manually performing backups. It works by connecting to Google Drive through its API and uploading the contents of a local folder to it.

## How It Works

The script makes use of a google service account, a special type of account used when an app needs authentication when accessing Google APIs and to perform automated tasks. OAuth tokens are used to authenticate with the API. The account's JSON key file contains the credentials used when authenticating and making requests to the API; a copy of this file must be kept locally. 

The script uploads the files to a folder that must already exist on the drive of the user. This is because you must give the permissions of an editor/owner to the folder before the execution of the script for the service account to be able to access and modify it. 

New files are uploaded to the backup folder while files that already exist on it are updated. No duplicates are created.

## Why Should I Use This?

There are many backup automation scripts you can easily find, but all that I've found still require some manual input from the user when performing the backup. This is due to them using their own personal account to perform the backups instead of a google service account. By using a service account, it is possible authenticate the connection to the Google Drive API automatically. Therefore, by creating a scheduled task for the OS to run the script, the backup can be performed with no user input.

## How To Use

### Setting up your google drive & service account

* Create a project in the Google Cloud Console

* Enable the Drive API for that project

* Create a service account

* Create a key for this account and download the JSON credentials file

* Create a folder on google drive and give the service account permission as editor

### Instructions

To clone the repository:
```
git clone https://github.com/carlos-silva-1/Automated-Backup
```

To install dependencies:
```
pip install -r requirements.txt
```

To run script:
```
python3 backup_drive.py
```

To setup scheduled task:
```
./setup_backup_schedule.sh
```

### Setting up configuration file

The configuration file config_example.py provides the following constants:
```
BACKUP_FOLDER_PATH = '/path/to/local/folder/'
CREDS_PATH = '/path/to/service-account/credentials/file/credential_file.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_NAME = 'Folder_name_on_google_drive'
``` 
These should be changed with your personal information, except for 'SCOPES', which should remain as it is.

### Creating a scheduled task to run the script

The following shell script sets up the scheduled task that runs the script automatically:
```
#!/bin/bash

# Define the cron job command to run your script
# In this exemple, it runs everyday at 12:00
cron_command="0 12 * * * /usr/bin/python3 /path/to/your/script.py"

# Write the cron job to a temporary file
echo "$cron_command" > /tmp/cron_job

# Install the cron job from the temporary file
crontab /tmp/cron_job

# Clean up the temporary file
rm /tmp/cron_job

echo "Cron job set up successfully."
```
"/path/to/your/script.py" needs to be modified to the path to the script on your machine.
To modify when the task should be executed, " 0 12 * * * " needs to be modified. [This](https://crontab.guru) resource should prove useful.
