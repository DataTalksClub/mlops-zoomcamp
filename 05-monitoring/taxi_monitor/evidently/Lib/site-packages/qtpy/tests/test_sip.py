import pytest


def test_sip():
    """Test the qtpy.sip namespace"""
    sip = pytest.importorskip("qtpy.sip")

    assert sip.assign is not None
    assert sip.cast is not None
    assert sip.delete is not None
    assert sip.dump is not None
    assert sip.enableautoconversion is not None
    assert sip.isdeleted is not None
    assert sip.ispycreated is not None
    assert sip.ispyowned is not None
    assert sip.setdeleted is not None
    assert sip.settracemask is not None
    assert sip.simplewrapper is not None
    assert sip.transferback is not None
    assert sip.transferto is not None
    assert sip.unwrapinstance is not None
    assert sip.voidptr is not None
    assert sip.wrapinstance is not None
    assert sip.wrapper is not None
    assert sip.wrappertype is not None
