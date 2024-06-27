# -*- coding: utf-8 -*-

import os
import pprint
import pytzdata

from cleo import Command


class ZonesCommand(Command):
    """
    Dumps available timezones to the _timezone.py file.

    zones:dump
    """

    TEMPLATE = """# -*- coding: utf-8 -*-

timezones = {}
"""

    def handle(self):
        zones = pytzdata.get_timezones()

        tz_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            '_timezones.py'
        )

        with open(tz_file, 'w') as fd:
            fd.write(
                self.TEMPLATE.format(pprint.pformat(zones))
            )

        self.info('Dumped <comment>{}</> timezones'.format(len(zones)))
