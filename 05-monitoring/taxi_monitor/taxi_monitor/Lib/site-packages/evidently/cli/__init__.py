from evidently.cli.collector import collector
from evidently.cli.main import app
from evidently.cli.ui import ui

__all__ = ["app", "ui", "collector"]


def main():
    app()


if __name__ == "__main__":
    main()
