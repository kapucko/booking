import horetu

"""
To run wsgi app:
$ uwsgi --wsgi-file cli_horetu.py --plugin python3 --http-socket :9090
"""


def run(src, dst, date, cheapest, shortest, is_return):

    value = (src, dst, date, cheapest, shortest, is_return)
    print(value)
    # this function has to return str value
    return str(value)

application = horetu.wsgi_form(run)

if __name__ == '__main__':
    horetu.cli(run)