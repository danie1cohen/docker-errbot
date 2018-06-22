errbot-kodi
=========

A plugin for controlling kodi/xbmc installations from within errbot.


Configuration
-------------
Send a dm to your errbot with `!plugin config Kodi` to get the default
configuration.

    {'HOST': 'http://localhost/jsonrpc', 'LOGIN': 'kodi', 'PASSWORD': 'kodi'}

Make your adjustments by running your config command in the dm.

    !plugin config Kodi {'HOST': 'http://yourxbmc:8080/jsonrpc', 'LOGIN': 'smarty', 'PASSWORD': 'pants'}

Available Commands
------------------
* !kodi message
* !kodi url
* !kodi volume
* !kodi ping
* !kodi home
* !kodi weather
* !kodi scan
* !kodi clean
* !kodi mute
* !kodi pause
* !kodi play
* !kodi stop
* !kodi left
* !kodi right
* !kodi up
* !kodi down
* !kodi back
* !kodi info
* !kodi select
