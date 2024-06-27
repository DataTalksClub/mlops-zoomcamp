from typing import Optional

from typer import Option

from evidently.cli.main import app


@app.command("collector")
def collector(
    host: str = Option("0.0.0.0", help="Collector host"),
    port: int = Option(8001, help="Collector port"),
    config_path: str = Option(None, help="Path to config file"),
    secret: Optional[str] = Option(None, help="Secret for writing operations"),
):
    """Start Evidently collector service"""
    from evidently.collector.app import run
    from evidently.collector.config import CONFIG_PATH

    run(host, port, config_path or CONFIG_PATH, secret)
