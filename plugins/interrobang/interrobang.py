"""
Simple module for allowing chatbot to handle extra control characters
"""
#pylint:disable=no-self-use,unused-argument,unused-variable
from errbot import BotPlugin, re_botcmd


class Interrobang(BotPlugin):
    """
    Handles comments like '!!!!!!!!!!!!!!' well
    """

    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Interrobang, self).activate()

    @re_botcmd(pattern='[!]+.*')
    def interrobang(self, msg, match):
        """Responses to numerous exclamation points."""
        count = match.group(0).count('!')
        ohs = ''.join(['o' for x in range(count)])
        return "W%sah nelly!" % ohs
