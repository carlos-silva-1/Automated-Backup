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
