"""
Kodi plugin for errbot
"""
# pylint: disable=unused-argument,too-many-public-methods,no-self-use
from itertools import chain
from functools import wraps
import os
import re
from datetime import datetime, timedelta

from errbot import BotPlugin, botcmd
from xbmcjson import XBMC, PLAYER_VIDEO


KODI_CONFIG = {
    'HOST': os.environ.get('KODI_HOST', 'http://localhost/jsonrpc'),
    'LOGIN': os.environ.get('KODI_LOGIN', 'kodi'),
    'PASSWORD': os.environ.get('KODI_PWD', 'kodi'),
}


def result(func):
    """
    Return the result value of a json/dict, if its present in the returned object.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Return the response text, if it exists.
        """
        response = func(*args, **kwargs)
        if isinstance(response, dict):
            if 'result' in response.keys():
                result_response = response['result']
                if isinstance(result_response, dict):
                    response = ''
                    for item in result_response.items():
                        response += '%s is %s.\n' % item
                else:
                    response = result_response
        return response
    return wrapper


class Kodi(BotPlugin):
    """
    Interact with a networked XBMC or Kodi installation via errbot.
    """
    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        self.load_config()
        super(Kodi, self).activate()

    def configure(self, configuration):
        """Set the configuration for the kodi plugin."""
        if configuration is not None and configuration != {}:
            config = dict(chain(KODI_CONFIG.items(),
                                configuration.items()))
        else:
            config = KODI_CONFIG

        super(Kodi, self).configure(config)

    def load_config(self):
        """Create the .xbmc client."""
        self.xbmc = XBMC(
            self.config['HOST'], self.config['LOGIN'], self.config['PASSWORD']
        )

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return KODI_CONFIG

    @result
    @botcmd
    def kodi_message(self, message, args):
        """
        Send a message to be displayed on screen.
        """
        title = "%s says:" % message.frm
        return self.xbmc.GUI.ShowNotification(title=title, message=args)

    @result
    @botcmd
    def kodi_url(self, message, args):
        """
        Play a given url on kodi.
        """
        if 'youtube' in args:
            args = format_youtube(args)
        return self.xbmc.Player.Open(item={'file': args})

    @result
    @botcmd
    def kodi_volume(self, message, args):
        """Set the volume to a value from 0-100"""
        try:
            return self.xbmc.Application.SetVolume(volume=int(args))
        except TypeError:
            return "Volume must be set to an integer."""

    @botcmd
    def kodi_help(self, message, args):
        """Lists possible kodi commands."""
        args = ['%s: %s' % (arg, getattr(self, arg).__doc__)
                for arg in dir(self) if arg.startswith('kodi')]
        return '\n'.join(args)

    @result
    @botcmd
    def kodi(self, message, args):
        """
        Run commands on the configured kodi/xbmc instance:

        * ping
        * home
        * weather
        * scan
        * clean
        * mute
        * pause
        * play
        * stop
        * left
        * right
        * up
        * down
        * back
        * info
        * select

        """
        if args in dir(self):
            method = getattr(self, args)
            return method()
        else:
            return "Command %s unrecognized. %s" % (message, args)

    @botcmd
    def htpc(self, message, args):
        """Just a symlink for kodi."""
        return self.kodi(message, args)

    def home(self):
        """Navigate to the home screen."""
        return self.xbmc.GUI.ActivateWindow(window='home')

    def weather(self):
        """Navigate to the weather screen."""
        return self.xbmc.GUI.ActivateWindow(window='weather')

    def scan(self):
        """Scan the video library."""
        return self.xbmc.VideoLibrary.Scan()

    def clean(self):
        """Clean the video library."""
        return self.xbmc.VideoLibrary.Clean()

    def mute(self):
        """Mute the audio."""
        return self.xbmc.Application.SetMute({'mute': True})

    def unmute(self):
        """Unmute the audio."""
        return self.xbmc.Application.SetMute({'mute': False})

    def pause(self):
        """Pause/Unpause."""
        return self.xbmc.Player.PlayPause([PLAYER_VIDEO])

    def stop(self):
        """Stop the video."""
        return self.xbmc.Player.Stop([PLAYER_VIDEO])

    def context(self):
        """Show context menu."""
        return self.xbmc.Input.ContextMenu()

    def showcodec(self):
        """Display the current codec."""
        return self.xbmc.Input.ShowCodec()

    def osd(self):
        """
        Show the on screen display.
        """
        return self.xbmc.Input.ShowOSD()

    def left(self):
        """Hit the left button."""
        return self.xbmc.Input.Left()

    def right(self):
        """Hit the right button."""
        return self.xbmc.Input.Right()

    def up(self):
        """Hit the up button."""
        return self.xbmc.Input.Up()

    def down(self):
        """Hit the down button."""
        return self.xbmc.Input.Down()

    def back(self):
        """Hit the back button."""
        return self.xbmc.Input.Back()

    def info(self):
        """View the info for the currently selected item."""
        return self.xbmc.Input.Info()

    def select(self):
        """Select the current item."""
        return self.xbmc.Input.Select()

    def ping(self):
        """Returns pong if everything's working."""
        return self.xbmc.JSONRPC.Ping()

    def eject(self):
        """Eject optical drive."""
        return self.xbmc.System.EjectOpticalDrive()

    def getproperties(self):
        """Get properties of current selection."""
        return self.xbmc.System.GetProperties()

    def hibernate(self):
        """Send the system into hibernation."""
        return self.xbmc.Player.Hibernate()

    def reboot(self):
        """Reboot the system."""
        return self.xbmc.System.Reboot()

    def shutdown(self):
        """Shutdown the system."""
        return self.xbmc.System.Shutdown()

    def suspend(self):
        """Suspend the system."""
        return self.xbmc.System.Suspend()

    def _update(self):
        """Load the latest video library data into memory."""
        movies = self.xbmc.VideoLibrary.GetMovies()['result']['movies']
        tv = self.xbmc.VideoLibrary.GetTVShows()['result']['tvshows']
        self._video_lib = {
            'mv': [KodiMedia(m) for m in movies],
            'tv': [KodiMedia(t) for t in tv],
            'date_update': datetime.now()
        }

    def _check_library(self):
        """Update library if it doesn't exist, or is stale."""
        if '_video_library' not in dir(self):
            self._update()
        elif self._video_lib['date_updated'] < datetime.now() - timedelta(days=1):
            self._update()

    def search(self, q, media_type=None):
        """Return matches for the query in tv and movies."""
        self._check_library()
        matches = []

        if media_type in ('mv_id', 'tv_id'):
            libtype = media_type.split('_')[0]
            try:
                m = [m for m in self._video_lib[libtype] if m.id == int(q)][0]
            except (TypeError, IndexError):
                pass
            else:
                return [m]

        if media_type is None or media_type == 'tv':
            tv = [show for show in self._video_lib['tv'] if show.match(q)]
            matches.extend(tv)

        if media_type is None or media_type == 'mv':
            movies = [mv for mv in self._video_lib['mv'] if mv.match(q)]
            matches.extend(movies)

        return matches

    @botcmd(split_args_with=None)
    def kodi_find(self, message, args):
        """Finds a response, optimistically trying to parse a type."""
        media_type, query = parse_args(args)
        r = self.search(query, media_type=media_type)
        return format_responses(r)

    def _play_matches(self, responses):
        """
        Play the found file if it matches, return useful message either way.
        """
        if len(responses) == 1:
            msg = 'Playing %s' % responses[0]
            self._play(responses[0])
        else:
            msg = format_responses(responses)
        return msg

    def _play(self, kodi_media):
        """Play a playable thing based on input params."""
        self.xbmc.Player.Open(item=kodi_media.params)

    @botcmd
    def kodi_playmovie(self, message, args):
        """Play a movie by name, if only one match found."""
        responses = self.search(args, media_type='mv')
        return self._play_matches(responses)

    @botcmd(split_args_with=None)
    def kodi_play(self, message, args):
        """Play a movie or tv ep by name, if only one match found."""
        if args in (None, []): return self.pause()

        media_type, query = parse_args(args)

        responses = self.search(query, media_type=media_type)
        return self._play_matches(responses)

    @botcmd
    def kodi_markasplayed(self, message, args):
        """
        If you are hovering over an item, you can use this to mark the item
        as played.
        """
        self.context()
        self.up()
        self.up()
        self.select()

class KodiMedia(object):
    """
    This object represents a single media item from kodi. Either movie or tv.
    """
    def __init__(self, item):
        """Instantiate and set properties."""
        self.id_type = detect_type(item)
        self.id = item[self.id_type]
        self.label = item['label']

    def __str__(self):
        """Formats as a string so nice!"""
        return '(%s.%s) %s' % (self.id_type, self.id, self.label)

    @property
    def params(self):
        """Return the params needed to identify a file to Kodi."""
        return {self.id_type: self.id}

    def match(self, q):
        """Does a given query match this item?"""
        return match(q, self.label)

def format_youtube(url):
    """Strip youtube video id and format it for kodi playing."""
    m = re.match(r'.*youtube.com/watch\?v=(.{11})', url)
    if m is None:
        raise ValueError('No youtube video found: %s' % url)
    video_id = m.group(1)
    prefix = "plugin://plugin.video.youtube/?action=play_video&videoid="
    return prefix + video_id

def match(query, string):
    """Return True if the query matches the string."""
    if query.lower() in string.lower():
        return True
    else:
        return False

def parse_args(args):
    """Grab a media type argument if one exists."""
    mappings = {
        'movie': 'mv',
        'tv': 'tv',
        'movie_id': 'mv_id',
        'tv_id': 'tv_id',
    }
    if args[0] in mappings.keys():
        media_type = mappings[args[0].lower()]

        if args[1] == 'id':
            query = ''.join(args[2:]).strip()
            media_type = media_type + '_id'
        else:
            query = ' '.join(args[1:])
    else:
        media_type = None
        query = ' '.join(args)

    return media_type, query

def format_responses(responses):
    """Return a string representing a group of responses."""
    string = "No matching found."
    count = len(responses)
    if count > 0:
        string = "Found %d matches:\n" % count
        string += '\n'.join([str(i) for i in responses])
    return string

def detect_type(response):
    """Detects the media type of a single response item."""
    id_field = None
    opts = ['movieid', 'tvshowid']
    for opt in opts:
        if opt in response.keys():
            id_field = opt
    return id_field
