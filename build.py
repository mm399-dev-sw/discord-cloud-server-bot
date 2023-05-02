#!/usr/bin/python3

import argparse
import os

def clean(projectName: str):
    os.system(f'docker image rm {projectName}')

def build(projectName: str, timezone: str):
    # arguments
    buildArgs = f'--build-arg TIMEZONE="{timezone}" '\
                f'--build-arg PROJECT_NAME="{projectName}" '
    createArgs = '--restart unless-stopped '
    # image
    print('Building image...')
    os.system(f'docker build --tag {projectName} {buildArgs} .')
    print('...done')
    # container
    print('Building container...')
    os.system(f'docker create --name {projectName} {createArgs} {projectName}')
    print('...done')

def run(projectName: str):
    os.system(f'docker start {projectName}')

def enterInteractively(projectName: str):
    os.system(f'docker exec -it {projectName} bash')

def stop(projectName: str):
    os.system(f'docker stop {projectName}')


def main():
    parser = argparse.ArgumentParser('Application to build and run docker container\n', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # change workdir
    wd = os.getcwd()
    if wd != os.path.dirname(os.path.abspath(__file__)):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ##### command line arguments #####
    # config
    parser.add_argument('-tz', '--timezone', type=str, default='Europe/Berlin', help='Timezone of the container')
    parser.add_argument('-pn', '--project-name', type=str, default=os.path.basename(os.path.dirname(os.path.abspath(__file__))), help='Name of the project')

    # build
    parser.add_argument('-c', '--clean', action='store_true', help='Clean up before building project')
    parser.add_argument('-b', '--build', action='store_true', help='Build project')
    
    # run
    parser.add_argument('-r', '--run', action='store_true', help='Run project')
    parser.add_argument('-it', '--interactive', action='store_true', help='Run project interactively')
    parser.add_argument('-s', '--stop', action='store_true', help='Stop project')

    # get arguments
    args = vars(parser.parse_args())

    timezone = args['timezone']
    projectName = args['project_name']

    cleanFlag = args['clean']
    buildFlag = args['build']
    runFlag = args['run']
    intFlag = args['interactive']
    stopFlag = args['stop']

    # do stuff
    if buildFlag:
        os.system(f'docker container rm -f {projectName}')
        if cleanFlag:
            clean(projectName)
        build(projectName, timezone)
    if runFlag:
        run(projectName)
    if intFlag:
        enterInteractively(projectName)
    if stopFlag:
        stop(projectName)
    
    os.chdir(wd)

if __name__ == '__main__':
    main()
