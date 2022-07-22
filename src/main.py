import sys

from corona_info.models import CoronaModel


def main(*args):
    model = CoronaModel(*args)
    data = model.get_data()

    for country in data:
        print(country)


if __name__ == "__main__":
    sys_args = sys.argv[1:]
    main(*sys_args)
