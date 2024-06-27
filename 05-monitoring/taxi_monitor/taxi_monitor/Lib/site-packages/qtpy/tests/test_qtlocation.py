import pytest

from qtpy import PYQT5, PYSIDE2


@pytest.mark.skipif(
    not (PYQT5 or PYSIDE2),
    reason="Only available in Qt5 bindings",
)
def test_qtlocation():
    """Test the qtpy.QtLocation namespace"""
    from qtpy import QtLocation

    if PYSIDE2:
        assert QtLocation.QGeoServiceProviderFactory is not None

    assert QtLocation.QGeoCodeReply is not None
    assert QtLocation.QGeoCodingManager is not None
    assert QtLocation.QGeoCodingManagerEngine is not None
    assert QtLocation.QGeoManeuver is not None
    assert QtLocation.QGeoRoute is not None
    assert QtLocation.QGeoRouteReply is not None
    assert QtLocation.QGeoRouteRequest is not None
    assert QtLocation.QGeoRouteSegment is not None
    assert QtLocation.QGeoRoutingManager is not None
    assert QtLocation.QGeoRoutingManagerEngine is not None
    assert QtLocation.QGeoServiceProvider is not None
    assert QtLocation.QPlace is not None
    assert QtLocation.QPlaceAttribute is not None
    assert QtLocation.QPlaceCategory is not None
    assert QtLocation.QPlaceContactDetail is not None
    assert QtLocation.QPlaceContent is not None
    assert QtLocation.QPlaceContentReply is not None
    assert QtLocation.QPlaceContentRequest is not None
    assert QtLocation.QPlaceDetailsReply is not None
    assert QtLocation.QPlaceEditorial is not None
    assert QtLocation.QPlaceIcon is not None
    assert QtLocation.QPlaceIdReply is not None
    assert QtLocation.QPlaceImage is not None
    assert QtLocation.QPlaceManager is not None
    assert QtLocation.QPlaceManagerEngine is not None
    assert QtLocation.QPlaceMatchReply is not None
    assert QtLocation.QPlaceMatchRequest is not None
    assert QtLocation.QPlaceProposedSearchResult is not None
    assert QtLocation.QPlaceRatings is not None
    assert QtLocation.QPlaceReply is not None
    assert QtLocation.QPlaceResult is not None
    assert QtLocation.QPlaceReview is not None
    assert QtLocation.QPlaceSearchReply is not None
    assert QtLocation.QPlaceSearchRequest is not None
    assert QtLocation.QPlaceSearchResult is not None
    assert QtLocation.QPlaceSearchSuggestionReply is not None
    assert QtLocation.QPlaceSupplier is not None
    assert QtLocation.QPlaceUser is not None
