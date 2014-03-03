from sleekxmpp.xmlstream import ET, ElementBase, register_stanza_plugin

class SharedStatus(ElementBase):
    name = 'query'
    namespace = 'google:shared-status'
    plugin_attrib = 'shared_status'
    interfaces = set(('status-max', 'status-list-max', 'status-list-contents-max',
                      'status-min-ver', 'status', 'show', 'version'))

    sub_interfaces = set(('status', 'show'))

    def add_list(self, show_type):
        status_list = StatusList()
        status_list['show'] = show_type
        self.append(status_list)
        return status_list

class StatusList(ElementBase):
    name = 'status-list'
    namespace = 'google:shared-status'
    plugin_attrib = 'status_list'
    plugin_multi_attrib = 'status_lists'
    interfaces = set(['show'])

    def add_status(self, contents):
        if self.parent:
            if len(self) >= self.parent['status-list-contents-max']:
                raise ValueError
            if len(contents) > self.parent['status-max']:
                raise ValueError

        status = Status()
        status.xml.text = contents
        self.append(status)
        return status

class Status(ElementBase):
    name = 'status'
    namespace = 'google:shared-status'
    plugin_attrib = name
    plugin_multi_attrib = 'statuses'

class Invisible(ElementBase):
    name = 'invisible'
    namespace = 'google:shared-status'
    plugin_attrib = name

    interfaces = set(("value",))

    def set_value(self, invisible):
        if isinstance(invisible, basestring):
            raise ValueError
        key = "true" if invisible else "false"
        self._set_attr("value", key)

    def get_value(self):
        key = self._get_attr("invisible", "false")
        if key not in ("true", "false"):
            raise ValueError("Unknown key value '{}' for invisible".format(key))
        return key == "true"

register_stanza_plugin(SharedStatus, StatusList, iterable=True)
register_stanza_plugin(SharedStatus, Invisible)
register_stanza_plugin(StatusList, Status, iterable=True)
