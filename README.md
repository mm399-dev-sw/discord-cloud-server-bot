# discord-cloud-server-bot

Discord bot to remotely start/stop and manage cloud VMs hosted on GCP

## Commands

    [ help ]: Prints help
    [ config ]: Prints config

    [ install <name> <image> <port> [--<arg> <value>] [<env-key>=<value> ...] ]: Installs VM from image. Optional environment key=value pairs may be appended for image configuration.  
        <name>: name to be given
        <image>: docker image to run
        <port>: port (range) to publish on container
    [ delete <name> ]: Deletes VM

    [ play <name> ]: Starts VM
    [ stop <name> [--timeout s]]: Stops VM. A timeout may be passed to delay the shutdown
    [ status <name> ]: Prints status of VM
    [ list ]: Lists all available VMs

Commands without arguments will print general information.
Default prefix is '+', but it may be changed in appl/default.conf

## Installation

### Discord

1. Create bot application for discord (<https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot>)

2. Add bot to your server (<https://discordjs.guide/preparations/adding-your-bot-to-servers.html#bot-invite-links>)

3. The bots only requirement is to send text messages. Save the obtained token.

### GCP

1. Create account for GCP (<https://cloud.google.com/>).

2. Create a new project in the cloud console.

3. In this project go to Compute Engine and enable the API. This may take a while.

4. Go to IAM and admin -> Service accounts and select the default service account *@developer.gserviceaccount.com

5. Under keys, add key -> create new key -> .json

6. Save this file under appl/authentication/auth-key.json. The name of the file can be adjusted in appl/default.conf

7. Add your Discord token and the ID of your GCP project to appl/default.conf. The ID may be obtained by accessing the project selection.

### Docker host

1. Navigate into the root of the repository

2. Build and run the container with the command 'docker compose up -d'

3. The bot should come online in Discord

## Creating a game server

For example to create a Valheim server on the default port
'+install valheim lloesche/valheim-server 2456 WORLD_NAME=saltheim SERVER_PASS=123456789 SERVER_PUBLIC=false'
