# Copyright © 2009- The Spyder Development Team
# Copyright © 2012- University of North Carolina at Chapel Hill
#                   Luke Campagnola    ('luke.campagnola@%s.com' % 'gmail')
#                   Ogi Moore          ('ognyan.moore@%s.com' % 'gmail')
#                   KIU Shueng Chuan   ('nixchuan@%s.com' % 'gmail')
# Licensed under the terms of the MIT License

"""
Compatibility functions for scoped and unscoped enum access.
"""

from . import PYQT6

if PYQT6:
    import enum

    from . import sip

    def promote_enums(module):
        """
        Search enums in the given module and allow unscoped access.

        Taken from:
        https://github.com/pyqtgraph/pyqtgraph/blob/pyqtgraph-0.12.1/pyqtgraph/Qt.py#L331-L377
        and adapted to also copy enum values aliased under different names.

        """
        class_names = [name for name in dir(module) if name.startswith("Q")]
        for class_name in class_names:
            klass = getattr(module, class_name)
            if not isinstance(klass, sip.wrappertype):
                continue
            attrib_names = [name for name in dir(klass) if name[0].isupper()]
            for attrib_name in attrib_names:
                attrib = getattr(klass, attrib_name)
                if not isinstance(attrib, enum.EnumMeta):
                    continue
                for name, value in attrib.__members__.items():
                    setattr(klass, name, value)
