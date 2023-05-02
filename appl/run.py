#!/usr/bin/python3

import cloudbot

def main():
    bot = cloudbot.CloudBot('/appl/default.conf')
    bot.run(bot.config['token'])

if __name__ == '__main__':
    main()
