import os
import time
import traceback

import discord
from discord.ext import commands
import argparse
from io import StringIO
import shlex


def parseFileConfig(file: str = 'default.conf') -> dict:
    ret = {}
    if os.path.isfile(file):
        with open(file) as f:
            content = f.read().split('\n')
        for line in content:
            try:
                key, value = line.replace(' ', '').split('=')
                if key[0] != '#':
                    ret[key] = value
            except:
                pass
    return ret

class CloudHandler:
    def __init__(self, config: dict):
        self.config = config
    
    def createVM(self, name: str, image: str):
        pass
    def deleteVM(self, name: str):
        pass
    def createFW(self, name: str, port):
        pass
    def deleteFW(self, name: str):
        pass

    def install(self, name: str, image: str, port: str) -> bool:
        # create firewall rule
        # create vm from image
        pass
    def delete(self, name: str) -> bool:
        # delete vm
        # delete firewall rule
        pass
    def getMachineTypesLink(self) -> str:
        # get link to available machine types
        pass
    
    def start(self, name: str) -> bool:
        # start vm
        pass
    def stop(self, name: str) -> bool:
        # stop vm
        pass
    
    def getIP(self, name: str) -> str:
        # get ip of vm
        pass
    def getPort(self, name: str) -> str:
        # get port of firewall rule
        pass
    def list(self) -> list:
        # list vms
        pass


class GCPhandler(CloudHandler):
    def __init__(self, config: dict):
        super().__init__(config)
        command = f'gcloud auth activate-service-account {self.config["user"]} --key-file={self.config["auth-key"]} --project={self.config["project-id"]}'
        os.system(f'echo "{command}"')
        os.system(command)
    
    def createVM(self, name: str, image: str, machineType: str, diskSizeGB: str, mountVolumes: list, *envArgs: str):
        command =   f'gcloud compute instances create-with-container {name} --container-image={image} --tags={name} --zone={self.config["zone"]} '\
                    f'--machine-type={machineType} --boot-disk-size={diskSizeGB}GB --boot-disk-type={self.config["disk-type"]} '\
                    f'--container-restart-policy=never ' + (f'--container-env={",".join(envArgs)} ' if envArgs and envArgs[0] else '') + \
                    (f'--container-mount-host-path=host-path=/home/{self.config["user"].split("@")[0]}/{mountVolumes[0]},mount-path={mountVolumes[1]} ' if mountVolumes else '')
        os.system(f'echo "{command}"')
        return os.system(command)

    def deleteVM(self, name: str):
        command = f'gcloud compute instances delete {name} -q --zone={self.config["zone"]}'
        os.system(f'echo "{command}"')
        return os.system(command)

    def getMachineTypesLink(self) -> str:
        return 'https://cloud.google.com/compute/docs/general-purpose-machines#e2_machine_types_table'

    def createFW(self, name: str, port):
        items = [line.split(' ') for line in os.popen(f'gcloud compute firewall-rules list').read().split('\n')]
        if name not in [col[0] for col in items]:
            command = f'gcloud compute firewall-rules create {name} --allow tcp:{port},udp:{port} --target-tags={name}'
            os.system(f'echo "{command}"')
            return os.system(command)
        else:
            return 0

    def deleteFW(self, name: str):
        command = f'gcloud compute firewall-rules delete {name} -q'
        os.system(f'echo "{command}"')
        return os.system(command)

    def install(self, name: str, image: str, port: str, machineType: str, diskSizeGB: str, mountVolumes: list, *envArgs: str) -> bool:
        if self.createFW(name, port):
            return 1
        if self.createVM(name, image, machineType, diskSizeGB, mountVolumes, *envArgs):
            self.deleteFW(name)
            return 1
        else:
            return 0

    def delete(self, name: str) -> bool:
        if self.deleteVM(name) or self.deleteFW(name):
            return 1
        else:
            return 0

    def start(self, name: str) -> bool:
        return os.system(f'gcloud compute instances start {name} --zone={self.config["zone"]}')

    def stop(self, name: str) -> bool:
        return os.system(f'gcloud compute instances stop {name} --zone={self.config["zone"]}')
    
    def getIP(self, name: str) -> str:
        try:
            return os.popen(f'gcloud compute instances describe {name} --zone={self.config["zone"]} --format="get(networkInterfaces[0].accessConfigs[0].natIP)"').read().split('\n')[0]
        except Exception as e:
            return traceback.format_exc()

    def getPort(self, name: str) -> str:
        try:
            return os.popen(f'gcloud compute firewall-rules describe {name} --format="get(allowed[].map().firewall_rule().list())"').read().split('\n')[0].split("'")[-2]
        except Exception as e:
            return traceback.format_exc()

    def list(self) -> list:
        content = os.popen(f'gcloud compute instances list --zones={self.config["zone"]}').read()
        if content:
            return [line.split(' ')[0] for line in content.split('\n')[1:-1]]
        else:
            return []


class AWShandler(CloudHandler):
    def __init__(self, config: dict):
        super().__init__(config)


# Discord bot
class CloudBot(commands.Bot):
    def __init__(self, configFile):
        # init from config file
        self.config = parseFileConfig(configFile)
        # overwrite with environment variables
        for key in self.config:
            envKey = key.replace('-', '_').upper()
            if envKey in os.environ:
                if key == 'auth-key':
                    with open(self.config[key], 'w') as f:
                        f.write(os.environ[envKey])
                else:
                    self.config[key] = os.environ[envKey]

        intents = discord.Intents.all()
        super().__init__(command_prefix=self.config['prefix'], help_command=None, intents=intents)
        if self.config['type'] == 'GCP':
            self.handler = GCPhandler(self.config)
        elif self.config['type'] == 'AWS':
            self.handler = AWShandler(self.config)

        # help and config
        @self.command(pass_context=True)
        async def help(ctx, *args):
            await ctx.send('Ah shit, here we go again.\n')
            await ctx.send( f'{self.config["prefix"]}[ help ]: Prints help\n'\
                            f'{self.config["prefix"]}[ config ]: Prints config\n'\
                            f'\n'\
                            f'{self.config["prefix"]}[ install <name> <image> <port> [--<arg> <value>] [<env-key>=<value> ...] ]: Installs VM from image. Optional environment key=value pairs may be appended for image configuration.  \n'\
                            f'    <name>: name to be given\n'\
                            f'    <image>: docker image to run\n'\
                            f'    <port>: port (range) to publish on container\n'\
                            f'{self.config["prefix"]}[ delete <name> ]: Deletes VM\n'\
                            f'\n'\
                            f'{self.config["prefix"]}[ play <name> ]: Starts VM\n'\
                            f'{self.config["prefix"]}[ stop <name> [--timeout s]]: Stops VM. A timeout may be passed to delay the shutdown\n'\
                            f'{self.config["prefix"]}[ status <name> ]: Prints status of VM\n'\
                            f'{self.config["prefix"]}[ list ]: Lists all available VMs\n'\
                            )

        @self.command(pass_context=True)
        async def config(ctx, *args):
            await ctx.send('Ah shit, here we go again.\n')
            await ctx.send('Config:\n' + '\n'.join(f'{key} = {self.config[key]}' for key in self.config))
        
        # install and delete containers
        @self.command(pass_context=True)
        async def install(ctx, *args):
            parser = argparse.ArgumentParser('', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser.add_argument('-mt', '--machine-type', type=str, default=self.config['machine-type'], help='Type of VM')
            parser.add_argument('-ds', '--disk-size-gb', type=str, default=self.config['disk-size-gb'], help='Disk size in GB')
            parser.add_argument('-v', '--volume', type=str, default='', help='<host-volume>:<container-volume>')
            if len(args) > 2:
                await ctx.send('Ah shit, here we go again.\n')
                # main parameters
                name, image, port = args[:3]
                # optional config arguments
                parsedArgs, envArgs = parser.parse_known_args(shlex.split(' '.join(args[3:])))
                parsedArgs = vars(parsedArgs)
                machineType = parsedArgs['machine_type']
                diskSizeGB = parsedArgs['disk_size_gb']
                mountVolumes = parsedArgs['volume'].split(':') if parsedArgs['volume'] else []
                if name in self.handler.list():
                    await ctx.send(f'{name} already installed\n')
                else:
                    if self.handler.install(name, image, port, machineType, diskSizeGB, mountVolumes, *envArgs):
                        await ctx.send(f'Failed installing {name} from {image}\n')
                    else:
                        await ctx.send(f'Installed {name} from {image} on {self.handler.getIP(name)}:{self.handler.getPort(name)}\n')
            else:
                await help(ctx, *args)
                await ctx.send(f'Install:\n[ {self.config["prefix"]}install <name> <image> <port> [--<arg> <value>] [<env-key>=<value> ...] ]\n'\
                                'Additional arguments:\n')
                parserHelp = StringIO()
                parser.print_help(parserHelp)
                await ctx.send(parserHelp.getvalue())
                await ctx.send(f'A list of standard machine types may be obtained here: {self.handler.getMachineTypesLink()}\n')
        
        @self.command(pass_context=True)
        async def delete(ctx, *args):
            if args:
                await ctx.send('Ah shit, here we go again.\n')
                name = args[0]
                if name in self.handler.list():
                    if self.handler.delete(name):
                        await ctx.send(f'Failed deleting {name}\n')
                    else:
                        await ctx.send(f'Deleted {name}\n')
                else:
                    await ctx.send(f'{name} not found\n')
            else:
                await help(ctx, *args)
        
        # manage existing containers
        @self.command(pass_context=True)
        async def play(ctx, *args):
            if args:
                await ctx.send('Ah shit, here we go again.\n')
                name = args[0]
                if name in self.handler.list():
                    if self.handler.start(name):
                        await ctx.send(f'Failed starting {name}\n')
                    else:
                        await ctx.send(f'Started {name} on {self.handler.getIP(name)}:{self.handler.getPort(name)}\n')
                else:
                    await ctx.send(f'{name} not found\n')
            else:
                await help(ctx, *args)

        @self.command(pass_context=True)
        async def stop(ctx, *args):
            if args:
                await ctx.send('Ah shit, here we go again.\n')
                name = args[0]
                parser = argparse.ArgumentParser('', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
                parser.add_argument('-t', '--timeout', type=str, default='', help='Delay execution by amount. Allows for suffix m for minutes, h for hours. Default is seconds')
                parsedArgs, otherArgs = parser.parse_known_args(shlex.split(' '.join(args[1:])))
                parsedArgs = vars(parsedArgs)
                if name in self.handler.list():
                    if parsedArgs['timeout']:
                        if parsedArgs['timeout'][-1] == 'm':
                            timeout = int(parsedArgs['timeout'][:-1]) * 60
                        elif parsedArgs['timeout'][-1] == 'h':
                            timeout = int(parsedArgs['timeout'][:-1]) * 60 * 60
                        else:
                            timeout = int(parsedArgs['timeout'])
                    else:
                        timeout = 0

                    if timeout:
                        for i in range(4):
                            await ctx.send(f'Stop scheduled for {name} in {timeout - i * timeout / 4} seconds\n')
                            time.sleep(timeout/4)
                    if self.handler.stop(name):
                        await ctx.send(f'Failed stopping {name}\n')
                    else:
                        await ctx.send(f'Stopped {name}\n')
                else:
                    await ctx.send(f'{name} not found\n')
            else:
                await help(ctx, *args)
        
        @self.command(pass_context=True)
        async def status(ctx, *args):
            if args:
                await ctx.send('Ah shit, here we go again.\n')
                name = args[0]
                if name in self.handler.list():
                    ip = self.handler.getIP(name)
                    if ip:
                        await ctx.send(f'{name} running on {ip}:{self.handler.getPort(name)}\n')
                    else:
                        await ctx.send(f'{name} not running\n')
                else:
                    await ctx.send(f'{name} not found\n')
            else:
                await ctx.send('Ah shit, here we go again.\n')
                available = self.handler.list()
                if available:
                    for name in available:
                        ip = self.handler.getIP(name)
                        await ctx.send(f'{name}: {ip if ip else "not alive"}{":" + self.handler.getPort(name) if ip else ""}\n')
                else:
                    await ctx.send('Nothing to show\n')

        @self.command(pass_context=True)
        async def list(ctx, *args):
            await ctx.send('Ah shit, here we go again.\n')
            content = self.handler.list()
            if content:
                await ctx.send("\n".join(content))
            else:
                await ctx.send('Nothing to list\n')
