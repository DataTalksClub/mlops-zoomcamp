from qtpy import PYQT6, PYSIDE2, PYSIDE6, QtNetwork


def test_qtnetwork():
    """Test the qtpy.QtNetwork namespace"""
    assert QtNetwork.QAbstractNetworkCache is not None
    assert QtNetwork.QNetworkCacheMetaData is not None
    if not PYSIDE2:
        assert QtNetwork.QHttpMultiPart is not None
        assert QtNetwork.QHttpPart is not None
    assert QtNetwork.QNetworkAccessManager is not None
    assert QtNetwork.QNetworkCookie is not None
    assert QtNetwork.QNetworkCookieJar is not None
    assert QtNetwork.QNetworkDiskCache is not None
    assert QtNetwork.QNetworkReply is not None
    assert QtNetwork.QNetworkRequest is not None
    if not (PYSIDE6 or PYQT6):
        assert QtNetwork.QNetworkConfigurationManager is not None
        assert QtNetwork.QNetworkConfiguration is not None
        assert QtNetwork.QNetworkSession is not None
    assert QtNetwork.QAuthenticator is not None
    assert QtNetwork.QHostAddress is not None
    assert QtNetwork.QHostInfo is not None
    assert QtNetwork.QNetworkAddressEntry is not None
    assert QtNetwork.QNetworkInterface is not None
    assert QtNetwork.QNetworkProxy is not None
    assert QtNetwork.QNetworkProxyFactory is not None
    assert QtNetwork.QNetworkProxyQuery is not None
    assert QtNetwork.QAbstractSocket is not None
    assert QtNetwork.QLocalServer is not None
    assert QtNetwork.QLocalSocket is not None
    assert QtNetwork.QTcpServer is not None
    assert QtNetwork.QTcpSocket is not None
    assert QtNetwork.QUdpSocket is not None
    assert QtNetwork.QSslCertificate is not None
    assert QtNetwork.QSslCipher is not None
    assert QtNetwork.QSslConfiguration is not None
    assert QtNetwork.QSslError is not None
    assert QtNetwork.QSslKey is not None
    assert QtNetwork.QSslSocket is not None
