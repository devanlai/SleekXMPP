"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from sleekxmpp.plugins.base import register_plugin

from sleekxmpp.plugins.google.status import stanza
from sleekxmpp.plugins.google.status.stanza import SharedStatus
from sleekxmpp.plugins.google.status.status import GoogleSharedStatus


register_plugin(GoogleSharedStatus)
