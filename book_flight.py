#!/usr/bin/env python
import argparse
import datetime

import requests

SEARCH_URL = 'https://api.skypicker.com/flights'
BOOKING_URL = 'http://37.139.6.125:8080/booking'


class ApiException(Exception):
    pass


def convert_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError('Date {0} is in invalid format'.format(date_str))


def book_flight(token):
    data = {'booking_token': token,
            'currency': 'EUR',
            'passengers': [{'title': 'Mr',
                            'email': 'test@example.com',
                            'documentID': 'XY123456',
                            'firstName': 'Johny',
                            'lastName': 'Cash',
                            'birthday': '1951-01-01',
                            'nationality': 'SK',
                            }]
            }

    response = requests.post(BOOKING_URL, json=data)
    if response.status_code == 200:
        return response.json()['pnr']

    raise ApiException('Unable to book flight. Reason: {0}'.format(response.reason))


def main(flight_date, flight_from, flight_to, flight_return, sort):

    date = flight_date.strftime('%d/%m/%Y')
    query_params = {
        'dateFrom': date,
        'dateTo': date,
        'flyFrom': flight_from,
        'to': flight_to,
        'typeFlight': 'return' if flight_return else 'one-way',
        'sort': sort,
        'limit': 1,
    }

    if flight_return:
        query_params['daysInDestinationFrom'] = flight_return
        query_params['daysInDestinationTo'] = flight_return

    response = requests.get(SEARCH_URL, query_params)
    if response.status_code != 200:
        raise ApiException('Error when searching API, reason: {0}'.format(response.reason))
    data = response.json()
    if not data.get('_results'):
        raise ApiException('No results for your filter.')

    result = data.get('data')[0]
    pnr = book_flight(result['booking_token'])
    print(pnr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Book flight')
    parser.add_argument('-d', '--date', dest='date', required=True, action='store', type=convert_date,
                        help='Departure date YYYY-MM-DD')
    parser.add_argument('-f', '--from', dest='flight_from', required=True, action='store', help='Departure destination')
    parser.add_argument('-t', '--to', dest='flight_to', required=True, action='store', help='Arrival destination')
    # one way or return ticket
    ticket_type_group = parser.add_mutually_exclusive_group()
    ticket_type_group.add_argument('-r', '--return', dest='flight_return', action='store', type=int,
                                   help='Book return ticket')
    ticket_type_group.add_argument('-o', '--one-way', dest='flight_one_way', action='store_true',
                                   help='Book one way ticket')
    # flight preference
    flight_preference_group = parser.add_mutually_exclusive_group()
    flight_preference_group.add_argument('-c', '--cheapest', dest='cheapest', action='store_true',
                                         help='Book cheapest ticket')
    flight_preference_group.add_argument('-s', '--shortest', dest='shortest', action='store_true',
                                         help='Book ticket with shortest duration')
    args = parser.parse_args()
    try:
        main(args.date, args.flight_from, args.flight_to, args.flight_return, 'duration' if args.shortest else 'price')
    except ApiException as e:
        print(e)
        exit(1)
