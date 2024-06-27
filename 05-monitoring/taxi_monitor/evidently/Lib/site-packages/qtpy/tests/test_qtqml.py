from qtpy import PYSIDE2, PYSIDE6


def test_qtqml():
    """Test the qtpy.QtQml namespace"""
    from qtpy import QtQml

    assert QtQml.QJSEngine is not None
    assert QtQml.QJSValue is not None
    assert QtQml.QJSValueIterator is not None
    assert QtQml.QQmlAbstractUrlInterceptor is not None
    assert QtQml.QQmlApplicationEngine is not None
    assert QtQml.QQmlComponent is not None
    assert QtQml.QQmlContext is not None
    assert QtQml.QQmlEngine is not None
    assert QtQml.QQmlImageProviderBase is not None
    assert QtQml.QQmlError is not None
    assert QtQml.QQmlExpression is not None
    assert QtQml.QQmlExtensionPlugin is not None
    assert QtQml.QQmlFileSelector is not None
    assert QtQml.QQmlIncubationController is not None
    assert QtQml.QQmlIncubator is not None
    if not (PYSIDE2 or PYSIDE6):
        # https://wiki.qt.io/Qt_for_Python_Missing_Bindings#QtQml
        assert QtQml.QQmlListProperty is not None
    assert QtQml.QQmlListReference is not None
    assert QtQml.QQmlNetworkAccessManagerFactory is not None
    assert QtQml.QQmlParserStatus is not None
    assert QtQml.QQmlProperty is not None
    assert QtQml.QQmlPropertyValueSource is not None
    assert QtQml.QQmlScriptString is not None
    assert QtQml.QQmlPropertyMap is not None
