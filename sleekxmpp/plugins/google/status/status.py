"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from sleekxmpp import Iq
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.plugins import BasePlugin
from sleekxmpp.xmlstream.handler import Callback
from sleekxmpp.xmlstream.matcher import MatchXPath
from sleekxmpp.plugins.google.status import stanza
from sleekxmpp.plugins.google.status.stanza import SharedStatus, StatusList, Status


class GoogleSharedStatus(BasePlugin):

    """
    Google: Shared Status

    Also see: <https://developers.google.com/talk/jep_extensions/shared_status>
    """

    name = 'google_shared_status'
    description = 'Google: Shared Status'
    dependencies = set(['xep_0030'])
    stanza = stanza

    def plugin_init(self):
        self.version = '2'
        self.last_status = None
        self.last_show = None
        self.last_invisible = None
        self.last_status_lists = []

        register_stanza_plugin(Iq, SharedStatus)

        self.xmpp.register_handler(
            Callback('Google Shared Status',
                MatchXPath('{%s}iq/{%s}%s' % (
                    self.xmpp.default_ns,
                    stanza.SharedStatus.namespace,
                    stanza.SharedStatus.name)),
                self._handle_shared_status_update))

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=SharedStatus.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(SharedStatus.namespace)

    def get_shared_status(self, block=True, timeout=None, callback=None):
        iq = self.xmpp.make_iq_get();
        #iq['type'] = 'get'
        iq.enable('shared_status')
        iq['shared_status']['version'] = self.version
        return iq.send(block=block, timeout=timeout, callback=callback)

    def update_shared_status(self, settings=None, status_lists=None,
                             block=True, timeout=None, callback=None):
        if not settings:
            settings = {}

        # status and show must always be included, even if we don't intend to
        # change one or change either of them
        settings.setdefault("status", self.last_status or "")
        settings.setdefault("show", self.last_show or "default")

        # include the shared-status protcol version, if not supplied by the user
        settings.setdefault("version", self.version)

        iq = self.xmpp.make_iq_set();
        iq.enable('shared_status')

        if "invisible" in settings:
            iq['shared_status']['invisible']['value'] = settings.pop("invisible")

        for key, value in settings.items():
            iq['shared_status'][key] = value

        if status_lists is None:
            status_lists = self.last_status_lists or {}

        for show_mode, statuses in status_lists:
            status_list = iq['shared_status'].add_list(show_mode)
            for status in statuses:
                status_list.add_status(status)

        iq.send(block=block, timeout=timeout, callback=callback)

    def set_shared_status(self, status=None, do_not_disturb=None, invisible=None,
                   block=True, timeout=None, callback=None):
        settings = {}
        if status is not None:
            settings["status"] = status
        if do_not_disturb is not None:
            settings["show"] = "dnd" if do_not_disturb else "default"
        if invisible is not None:
            settings["invisible"] = invisible

        self.update_shared_status(settings, self.last_status_lists,
                                  block=block, timeout=timeout, callback=callback)
    
    def _handle_shared_status_update(self, iq):
        self.last_status = iq['shared_status']['status']
        self.last_show = iq['shared_status']['show']
        self.last_invisible = iq['shared_status']['invisible']['value']

        self.last_status_lists = {}
        for status_list in iq['shared_status']:
            statuses = []
            for status in status_list:
                print status.text
                #statuses.append(status.text)
            self.last_status_lists[status_list['show']] = statuses

        print "Last status: {}".format(self.last_status)
        print "Last show state: {}".format(self.last_show)

        iq.reply().send()
        self.xmpp.event('google_shared_status_updated')
