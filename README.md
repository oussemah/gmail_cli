This is a sample python script that checks a gmail account for incoming
emails with a certain specs (sender, subject)
and then if it finds and email, it parse the snippet fo the email which contains a command to execute.
It executes that command in a subprocess and takes 
a snapshot of the desktop once done and send it back to the email.

For example, if i have a linux pc running this script in a cron once hour,
I just need to send an email with title execute, and with body : cd $WORKSPACE/python/;git clone https://github.com/oussemah/ComesteroPy.git
The script will execute that command and send the result via email.

This is just to bypass the doifficulty of accessing my pc via ssh from remote.

This script is based on latest Google GMAIL Python API and OAuth2 released in Summer 2015.
Dpn't forget to add your proper client_secret.json file which contains your private authorization for apps to access your gmail account.

This can evolve into something much more complicated and much more useful appilcation depending on  your needs.

Author : Oussema Harbi <oussema.elharbi@gmail.com>

