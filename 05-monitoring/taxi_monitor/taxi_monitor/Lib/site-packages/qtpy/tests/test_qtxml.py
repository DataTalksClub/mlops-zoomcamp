def test_qtxml():
    """Test the qtpy.QtXml namespace"""
    from qtpy import QtXml

    assert QtXml.QDomAttr is not None
    assert QtXml.QDomCDATASection is not None
    assert QtXml.QDomCharacterData is not None
    assert QtXml.QDomComment is not None
    assert QtXml.QDomDocument is not None
    assert QtXml.QDomDocumentFragment is not None
    assert QtXml.QDomDocumentType is not None
    assert QtXml.QDomElement is not None
    assert QtXml.QDomEntity is not None
    assert QtXml.QDomEntityReference is not None
    assert QtXml.QDomImplementation is not None
    assert QtXml.QDomNamedNodeMap is not None
    assert QtXml.QDomNode is not None
    assert QtXml.QDomNodeList is not None
    assert QtXml.QDomNotation is not None
    assert QtXml.QDomProcessingInstruction is not None
    assert QtXml.QDomText is not None
