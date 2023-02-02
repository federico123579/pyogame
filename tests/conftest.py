import pytest

FLAGS = {
    "slow": {
        "help": "run slow tests",
        "mark_desc": "mark test as slow to run",
        "default": False,
    },
    "dirty": {
        "help": "run tests that can change the state of the game",
        "mark_desc": "mark test as dirty to run",
        "default": False,
    },
    "social": {
        "help": "run tests that can change other players attitudes",
        "mark_desc": "mark test as social to run",
        "default": False,
    },
}


def pytest_addoption(parser):

    def add_cond_flag(name, default=False, help=""):
        parser.addoption(
            f"--run{name}", action="store_true", default=default, help=help)

    for k, v in FLAGS.items():
        add_cond_flag(k, default=v["default"], help=v["help"])


def pytest_configure(config):
    for k, v in FLAGS.items():
        config.addinivalue_line("markers", f"{k}: {v['mark_desc']}")


def pytest_collection_modifyitems(config, items):
    def skip_x(x):
        return pytest.mark.skip(reason=f"need --run{x} option to run")

    for marker in FLAGS.keys():
        if config.getoption(f"--run{marker}"):
            return
        for item in items:
            if marker in item.keywords:
                item.add_marker(skip_x(marker))
