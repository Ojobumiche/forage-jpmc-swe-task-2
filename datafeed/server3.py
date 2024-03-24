class App(object):
    """ The trading game server application. """

    def __init__(self):
        self._book_1 = dict()
        self._book_2 = dict()
        self._data_1 = order_book(read_csv(), self._book_1, 'ABC')
        self._data_2 = order_book(read_csv(), self._book_2, 'DEF')
        self._rt_start = datetime.now()
        self.read_10_first_lines()

    def read_10_first_lines(self):
        for _ in iter(range(10)):
            next(self._data_1)
            next(self._data_2)

    @property
    def _current_book_1(self):
        while True:
            try:
                t, bids, asks = next(self._data_1)
                if REALTIME:
                    while t > self._sim_start + (datetime.now() - self._rt_start):
                        yield t, bids, asks
                else:
                    yield t, bids, asks
            except StopIteration:
                # Reinitialize the application if the end of iteration is reached
                print("End of data for stock 'ABC'. Reinitializing...")
                self.__init__()
                continue

    @property
    def _current_book_2(self):
        while True:
            try:
                t, bids, asks = next(self._data_2)
                if REALTIME:
                    while t > self._sim_start + (datetime.now() - self._rt_start):
                        yield t, bids, asks
                else:
                    yield t, bids, asks
            except StopIteration:
                # Reinitialize the application if the end of iteration is reached
                print("End of data for stock 'DEF'. Reinitializing...")
                self.__init__()
                continue

    @route('/query')
    def handle_query(self, x):
        """ Takes no arguments, and yields the current top of the book;
            the best bid and ask and their sizes
        """
        try:
            t1, bids1, asks1 = next(self._current_book_1)
            t2, bids2, asks2 = next(self._current_book_2)
        except Exception as e:
            print("Error getting stocks:", e)
            return []

        t = max(t1, t2)
        print('Query received @ t%s' % t)
        return [
            {
                'id': x and x.get('id', None),
                'stock': 'ABC',
                'timestamp': str(t),
                'top_bid': bids1 and {'price': bids1[0][0], 'size': bids1[0][1]},
                'top_ask': asks1 and {'price': asks1[0][0], 'size': asks1[0][1]}
            },
            {
                'id': x and x.get('id', None),
                'stock': 'DEF',
                'timestamp': str(t),
                'top_bid': bids2 and {'price': bids2[0][0], 'size': bids2[0][1]},
                'top_ask': asks2 and {'price': asks2[0][0], 'size': asks2[0][1]}
            }
        ]
