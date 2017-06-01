# Copyright (C) 2017 Red Hat, Inc.
#
# fedmsg_meta_umb is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# fedmsg_meta_umb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with fedmsg; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Authors:  Ralph Bean <rbean@redhat.com>

from fedmsg.meta.base import BaseProcessor


class ErrataProcessor(BaseProcessor):
    topic_prefix_re = r'/topic/VirtualTopic\.eng'

    __name__ = 'errata'
    __description__ = 'the Errata Tool'
    __link__ = 'https://errata.devel.redhat.com/'
    __docs__ = 'https://errata.devel.redhat.com/user-guide/'
    __obj__ = 'errata events'
    __icon__ = ('https://errata.devel.redhat.com/assets/'
                'images/erratatool18.png')

    def __init__(self, *args, **kwargs):
        super(ErrataProcessor, self).__init__(*args, **kwargs)
        self.simple_subtitle_templates = {
            'errata.activity.status': self._(
                '{agent} moved {fulladvisory} from {from} to {to}'),
            'errata.activity.created': self._(
                '{agent} filed a new {type} advisory for {release}'),
            'errata.activity.signing': self._(
                '{agent} reported signing {to} for {fulladvisory}'),
        }

    def title(self, msg, **config):
        return msg['topic'].split('.', 2)[-1]

    def subtitle(self, msg, **config):
        headers = msg['headers']
        title = self.title(msg, **config)
        agent = self.agent(msg, **config)

        # First, handle the simple cases...
        template = self.simple_subtitle_templates.get(title)
        if template:
            return template.format(agent=agent, **headers)

        # Then, handle these more complex cases if that failed.
        if title == 'errata.activity.security_approved':
            if headers['to'] == 'true':
                template = self._('{agent} approved the security '
                                  'request on {fulladvisory}')
            elif headers['to'] == 'null':
                template = self._('{agent} unset the security '
                                  'flag on {fulladvisory}')
            elif headers['to'] == 'false':
                # Two very different senses of "false"
                if headers['from'] == 'null':
                    template = self._('{agent} requested security '
                                      'approval on {fulladvisory}')
                else:
                    template = self._('{agent} denied the security '
                                      'request on {fulladvisory}')

            return template.format(agent=agent, **headers)

    def agent(self, msg, **config):
        return msg['headers']['who'].split('@')[0].split('/')[0]

    def usernames(self, msg, **config):
        return set([self.agent(msg, **config)])

    def link(self, msg, **config):
        template = 'https://errata.devel.redhat.com/advisory/{errata_id}'
        return template.format(**msg['headers'])
