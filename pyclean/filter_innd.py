# vim: tabstop=4 expandtab shiftwidth=4 autoindent
##  $Id: filter_innd.py 8955 2010-02-07 20:05:39Z iulius $
##
##  This is a sample filter for the Python innd hook.
##
##  See the INN Python Filtering and Authentication Hooks documentation
##  for more information.
##
##  You have access to the following methods from the module INN:
##   - addhist(message-id)
##   - article(message-id)
##   - cancel(message-id)
##   - havehist(message-id)
##   - hashstring(string)
##   - head(message-id)
##   - newsgroup(groupname)
##   - set_filter_hook(instance)
##   - syslog(level, message)

from Config import config
import os.path
import traceback
import PyClean
#from string import *

class InndFilter:
    """Provide filtering callbacks to innd."""

    def __init__(self):
        """This runs every time the filter is loaded or reloaded.
        This is a good place to initialize variables and precompile
        regular expressions, or maybe reload stats from disk.

        """
        try:
            self.pyclean = PyClean.pyclean()
        except:
            fn = os.path.join(config.get('paths', 'log'), 'init_traceback')
            f = open(fn, 'a')
            traceback.print_exc(file=f)
            f.close()

    def filter_before_reload(self):
        """Runs just before the filter gets reloaded.

        You can use this method to save state information to be
        restored by the __init__() method or down in the main module.
        """
        reload(PyClean)

    def filter_close(self):
        """Runs when innd exits.

        You can use this method to save state information to be
        restored by the __init__() method or down in the main module.
        """
        syslog('notice', "filter_close running, bye!")

    def filter_messageid(self, msgid):
        """Filter articles just by their Message-IDs.

        This method interacts with the CHECK, IHAVE and TAKETHIS
        NNTP commands.
        If you return a non-empty string here, the offered article
        will be refused before you ever have to waste any bandwidth
        looking at it (unless TAKETHIS is used before an earlier CHECK).
        Make sure that such a message is properly encoded in UTF-8
        so as to comply with the NNTP protocol.
        """
        return ""               # Deactivate the samples.

    def filter_art(self, art):
        """Decide whether to keep offered articles.

        art is a dictionary with a bunch of headers, the article's
        body, and innd's reckoning of the line count.  Items not
        in the article will have a value of None.

        The available headers are the ones listed near the top of
        innd/art.c.  At this writing, they are:

            Also-Control, Approved, Archive, Archived-At, Bytes, Cancel-Key,
            Cancel-Lock, Content-Base, Content-Disposition,
            Content-Transfer-Encoding, Content-Type, Control, Date,
            Date-Received, Distribution, Expires, Face, Followup-To, From,
            In-Reply-To, Injection-Date, Injection-Info, Keywords, Lines,
            List-ID, Message-ID, MIME-Version, Newsgroups, NNTP-Posting-Date,
            NNTP-Posting-Host, NNTP-Posting-Path, Organization,
            Original-Sender, Originator, Path, Posted, Posting-Version,
            Received, References, Relay-Version, Reply-To, Sender, Subject,
            Summary, Supersedes, User-Agent, X-Auth, X-Auth-Sender,
            X-Canceled-By, X-Cancelled-By, X-Complaints-To, X-Face,
            X-HTTP-UserAgent, X-HTTP-Via, X-Mailer, X-Modbot, X-Modtrace,
            X-Newsposter, X-Newsreader, X-No-Archive, X-Original-Message-ID,
            X-Original-NNTP-Posting-Host, X-Original-Trace, X-Originating-IP,
            X-PGP-Key, X-PGP-Sig, X-Poster-Trace, X-Postfilter, X-Proxy-User,
            X-Submissions-To, X-Trace, X-Usenet-Provider, X-User-ID, Xref.

        The body is the buffer in art[__BODY__] and the INN-reckoned
        line count is held as an integer in art[__LINES__].  (The
        Lines: header is often generated by the poster, and large
        differences can be a good indication of a corrupt article.)

        If you want to keep an article, return None or "".  If you
        want to reject, return a non-empty string.  The rejection
        string will appear in transfer and posting response banners,
        and local posters will see them if their messages are
        rejected (make sure that such a response is properly encoded
        in UTF-8 so as to comply with the NNTP protocol).

        """
        try:
            return self.pyclean.filter(art)
        except:
            fn = os.path.join(config.get('paths', 'log'), 'traceback')
            f = open(fn, 'a')
            traceback.print_exc(file=f)
            f.close()
            return ""

    def filter_mode(self, oldmode, newmode, reason):
        """Capture server events and do something useful.

        When the admin throttles or pauses innd (and lets it go
        again), this method will be called.  oldmode is the state we
        just left, and newmode is where we are going.  reason is
        usually just a comment string.

        The possible values of newmode and oldmode are the five
        strings 'running', 'paused', 'throttled', 'shutdown' and
        'unknown'.  Actually 'unknown' shouldn't happen; it's there
        in case feeping creatures invade innd.
        """
        syslog('n', 'state change from %s to %s - %s'
               % (oldmode, newmode, reason))

"""
Okay, that's the end of our class definition.  What follows is the
stuff you need to do to get it all working inside innd.
"""

##  This import must succeed, or your filter won't work.  I'll repeat
##  that: You MUST import INN.
from INN import *

##  Some of the stuff below is gratuitous, just demonstrating how the
##  INN.syslog call works.  That first thingy tells the Unix syslogger
##  what severity to use; you can abbreviate down to one letter and
##  it's case insensitive.  Available levels are (in increasing levels
##  of seriousness) Debug, Info, Notice, Warning, Err, Crit, and
##  Alert.  If you provide any other string, it will be defaulted to
##  Notice.  You'll find the entries in the same log files innd itself
##  uses, with an 'innd: python:' prefix.
##
##  The native Python syslog module seems to clash with INN, so use
##  INN's.  Oh yeah -- you may notice that stdout and stderr have been
##  redirected to /dev/null -- if you want to print stuff, open your
##  own files.

try:
    import sys

except Exception, errmsg:    # Syntax for Python 2.x.
#except Exception as errmsg: # Syntax for Python 3.x.
    syslog('Error', "import boo-boo: " + errmsg[0])


##  If you want to do something special when the server first starts
##  up, this is how to find out when it's time.

if 'pyclean' not in dir():
    syslog('n', "First load, so I can do initialization stuff.")
    # Initialize the standard Python logger
    # You could unpickle a saved hash here, so that your hard-earned
    # spam scores aren't lost whenever you shut down innd.
else:
    syslog('n', "I'm just reloading, so skip the formalities.")


##  Finally, here is how we get our class on speaking terms with innd.
##  The hook is refreshed on every reload, so that you can change the
##  methods on a running server.  Don't forget to test your changes
##  before reloading!
pyclean = InndFilter()
try:
    set_filter_hook(pyclean)
    syslog('n', "pyclean successfully hooked into INN")
except Exception, errmsg:    # Syntax for Python 2.x.
#except Exception as errmsg: # Syntax for Python 3.x.
    syslog('e', "Cannot obtain INN hook for pyclean: %s" % errmsg[0])
