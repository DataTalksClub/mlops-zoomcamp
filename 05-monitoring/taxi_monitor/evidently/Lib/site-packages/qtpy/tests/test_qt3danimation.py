import pytest


def test_qt3danimation():
    """Test the qtpy.Qt3DAnimation namespace"""
    Qt3DAnimation = pytest.importorskip("qtpy.Qt3DAnimation")

    assert Qt3DAnimation.QAnimationController is not None
    assert Qt3DAnimation.QAdditiveClipBlend is not None
    assert Qt3DAnimation.QAbstractClipBlendNode is not None
    assert Qt3DAnimation.QAbstractAnimation is not None
    assert Qt3DAnimation.QKeyframeAnimation is not None
    assert Qt3DAnimation.QAbstractAnimationClip is not None
    assert Qt3DAnimation.QAbstractClipAnimator is not None
    assert Qt3DAnimation.QClipAnimator is not None
    assert Qt3DAnimation.QAnimationGroup is not None
    assert Qt3DAnimation.QLerpClipBlend is not None
    assert Qt3DAnimation.QMorphingAnimation is not None
    assert Qt3DAnimation.QAnimationAspect is not None
    assert Qt3DAnimation.QVertexBlendAnimation is not None
    assert Qt3DAnimation.QBlendedClipAnimator is not None
    assert Qt3DAnimation.QMorphTarget is not None
