from evidently.utils.dashboard import inline_iframe_html_template


def determine_template(mode: str):
    """
    :param str mode: Deprecated. Left it for BC
    """
    return inline_iframe_html_template
