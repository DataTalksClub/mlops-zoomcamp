""" Defines miscellaneous Qt-related helper classes and functions.
"""

import inspect

from qtpy import QtCore, QtGui

from traitlets import HasTraits, TraitType

#-----------------------------------------------------------------------------
# Metaclasses
#-----------------------------------------------------------------------------

MetaHasTraits = type(HasTraits)
MetaQObject = type(QtCore.QObject)

class MetaQObjectHasTraits(MetaQObject, MetaHasTraits):
    """ A metaclass that inherits from the metaclasses of HasTraits and QObject.

    Using this metaclass allows a class to inherit from both HasTraits and
    QObject. Using SuperQObject instead of QObject is highly recommended. See
    QtKernelManager for an example.
    """
    def __new__(mcls, name, bases, classdict):
        # FIXME: this duplicates the code from MetaHasTraits.
        # I don't think a super() call will help me here.
        for k,v in iter(classdict.items()):
            if isinstance(v, TraitType):
                v.name = k
            elif inspect.isclass(v):
                if issubclass(v, TraitType):
                    vinst = v()
                    vinst.name = k
                    classdict[k] = vinst
        cls = MetaQObject.__new__(mcls, name, bases, classdict)
        return cls

    def __init__(mcls, name, bases, classdict):
        # Note: super() did not work, so we explicitly call these.
        MetaQObject.__init__(mcls, name, bases, classdict)
        MetaHasTraits.__init__(mcls, name, bases, classdict)

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

def superQ(QClass):
    """ Permits the use of super() in class hierarchies that contain Qt classes.

    Unlike QObject, SuperQObject does not accept a QObject parent. If it did,
    super could not be emulated properly (all other classes in the heierarchy
    would have to accept the parent argument--they don't, of course, because
    they don't inherit QObject.)

    This class is primarily useful for attaching signals to existing non-Qt
    classes. See QtKernelManagerMixin for an example.
    """
    class SuperQClass(QClass):

        def __new__(cls, *args, **kw):
            # We initialize QClass as early as possible. Without this, Qt complains
            # if SuperQClass is not the first class in the super class list.
            inst = QClass.__new__(cls)
            QClass.__init__(inst)
            return inst

        def __init__(self, *args, **kw):
            # Emulate super by calling the next method in the MRO, if there is one.
            mro = self.__class__.mro()
            for qt_class in QClass.mro():
                mro.remove(qt_class)
            next_index = mro.index(SuperQClass) + 1
            if next_index < len(mro):
                mro[next_index].__init__(self, *args, **kw)

    return SuperQClass

SuperQObject = superQ(QtCore.QObject)

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def get_font(family, fallback=None):
    """Return a font of the requested family, using fallback as alternative.

    If a fallback is provided, it is used in case the requested family isn't
    found.  If no fallback is given, no alternative is chosen and Qt's internal
    algorithms may automatically choose a fallback font.

    Parameters
    ----------
    family : str
      A font name.
    fallback : str
      A font name.

    Returns
    -------
    font : QFont object
    """
    font = QtGui.QFont(family)
    # Check whether we got what we wanted using QFontInfo, since exactMatch()
    # is overly strict and returns false in too many cases.
    font_info = QtGui.QFontInfo(font)
    if fallback is not None and font_info.family() != family:
        font = QtGui.QFont(fallback)
    return font


# -----------------------------------------------------------------------------
# Vendored from ipython_genutils
# -----------------------------------------------------------------------------
def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


def _find_optimal(rlist, *, separator_size, displaywidth):
    """Calculate optimal info to columnize a list of strings"""
    for nrow in range(1, len(rlist) + 1):
        chk = list(map(max, _chunks(rlist, nrow)))
        sumlength = sum(chk)
        ncols = len(chk)
        if sumlength + separator_size * (ncols - 1) <= displaywidth:
            break

    return {
        "columns_numbers": ncols,
        "rows_numbers": nrow,
        "columns_width": chk,
    }


def _get_or_default(mylist, i, *, default):
    """return list item number, or default if don't exist"""
    if i >= len(mylist):
        return default
    else:
        return mylist[i]


def compute_item_matrix(items, empty=None, *, separator_size=2, displaywidth=80):
    """Returns a nested list, and info to columnize items

    Parameters
    ----------
    items
        list of strings to columnize
    empty : (default None)
        Default value to fill list if needed
    separator_size : int (default=2)
        How much characters will be used as a separation between each column.
    displaywidth : int (default=80)
        The width of the area onto which the columns should enter

    Returns
    -------

    strings_matrix

        nested list of strings, the outer most list contains as many list as
        rows, the innermost lists have each as many element as column. If the
        total number of elements in `items` does not equal the product of
        rows*columns, the last element of some lists are filled with `None`.

    dict_info
        Some info to make columnize easier:

        columns_numbers
          number of columns
        rows_numbers
          number of rows
        columns_width
          list of width of each columns

    Examples
    --------
    ::

        In [1]: l = ['aaa','b','cc','d','eeeee','f','g','h','i','j','k','l']
           ...: compute_item_matrix(l,displaywidth=12)
        Out[1]:
            ([['aaa', 'f', 'k'],
            ['b', 'g', 'l'],
            ['cc', 'h', None],
            ['d', 'i', None],
            ['eeeee', 'j', None]],
            {'columns_numbers': 3,
            'columns_width': [5, 1, 1],
            'rows_numbers': 5})
    """
    info = _find_optimal(
        [len(it) for it in items], separator_size=separator_size, displaywidth=displaywidth
    )
    nrow, ncol = info["rows_numbers"], info["columns_numbers"]
    return (
        [
            [_get_or_default(items, c * nrow + i, default=empty) for c in range(ncol)]
            for i in range(nrow)
        ],
        info,
    )


def columnize(items, separator="  ", displaywidth=80):
    """Transform a list of strings into a single string with columns.

    Parameters
    ----------
    items : sequence of strings
        The strings to process.

    Returns
    -------
    The formatted string.
    """
    if not items:
        return "\n"
    matrix, info = compute_item_matrix(
        items, separator_size=len(separator), displaywidth=displaywidth
    )
    fmatrix = [filter(None, x) for x in matrix]
    sjoin = lambda x: separator.join(
        [y.ljust(w, " ") for y, w in zip(x, info["columns_width"])]
    )
    return "\n".join(map(sjoin, fmatrix)) + "\n"


def import_item(name):
    """Import and return ``bar`` given the string ``foo.bar``.

    Calling ``bar = import_item("foo.bar")`` is the functional equivalent of
    executing the code ``from foo import bar``.

    Parameters
    ----------
    name : string
      The fully qualified name of the module/package being imported.

    Returns
    -------
    mod : module object
       The module that was imported.
    """
    parts = name.rsplit(".", 1)

    if len(parts) == 2:
        # called with 'foo.bar....'
        package, obj = parts
        module = __import__(package, fromlist=[obj])
        try:
            pak = getattr(module, obj)
        except AttributeError:
            raise ImportError("No module named %s" % obj)
        return pak
    else:
        # called with un-dotted string
        return __import__(parts[0])
