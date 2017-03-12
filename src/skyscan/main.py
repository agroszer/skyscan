#
import csv
import datetime
import fire
import os
import requests

from skyscanner.skyscanner import FlightsCache


class OTA(object):
    pass


class SkyScanner(OTA):

    def __init__(self):
        from os.path import expanduser
        fname = os.path.join(expanduser("~"), '.skyscannerkey')
        with open(fname) as keyfile:
            self.key = keyfile.read().strip()

    def query(self, dateFrom, dateTo, frm, to, persons):
        flights_cache_service = FlightsCache(self.key)
        result = flights_cache_service.get_cheapest_quotes(
            market='UK',
            currency='USD',
            locale='en-US',
            originplace=frm,
            destinationplace=to,
            outbounddate=dateFrom.strftime("%Y-%m-%d"),
            #inbounddate=dateTo.strftime("%Y-%m-%d"),
            adults=persons).parsed

        carriers = dict([
            (carr['CarrierId'], carr['Name']) for carr in result['Carriers']])

        rv = dict(
            dateFrom=dateFrom, dateTo=dateTo, frm=frm, to=to, persons=persons,
            price=result['Quotes'][0]['MinPrice'],
            currency=result['Currencies'][0]['Code'],
            carrier=carriers[result['Quotes'][0]['OutboundLeg']['CarrierIds'][0]],
            timestamp=datetime.datetime.now()
            )

        print rv

        return rv


class SkyPicker(OTA):
    def query(self, dateFrom, dateTo, frm, to, persons):
        dateFromS = dateFrom.strftime("%d/%m/%Y")
        if dateTo is None:
            dateToS = ''
        else:
            dateToS = dateTo.strftime("%d/%m/%Y")

        payload = dict(
            v=2, locale='us',
            sort='price', asc=1,
            limit=3,
            daysInDestinationFrom='', daysInDestinationTo='', affilid='',
            children=0, infants=0,
            flyFrom=frm, to=to,
            featureName='aggregateResults',
            dateFrom=dateFromS, dateTo=dateToS,
            typeFlight='oneway', returnFrom='', returnTo='',
            one_per_date=0, oneforcity=0, wait_for_refresh=1, adults=1,
            )

        r = requests.get('https://api.skypicker.com/flights', params=payload)
        result = r.json()

        rv = dict(
            dateFrom=dateFrom, dateTo=dateTo, frm=frm, to=to, persons=persons,
            price=result['data'][0]['price'],
            currency=result['currency'],
            carrier=result['data'][0]['route'][0]['airline'],
            timestamp=datetime.datetime.now()
            )

        print rv

        return rv


class DataSource(object):
    pass


class CSVSource(DataSource):
    def load(self, fname):
        data = []
        with open(fname) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rw = row.copy()
                if rw['DateFrom']:
                    rw['DateFrom'] = datetime.datetime.strptime(
                        rw['DateFrom'], "%Y-%m-%d").date()
                else:
                    rw['DateFrom'] = None
                if rw['DateTo']:
                    rw['DateTo'] = datetime.datetime.strptime(
                        rw['DateTo'], "%Y-%m-%d").date()
                else:
                    rw['DateTo'] = None
                rw['persons'] = int(rw['persons'])
                data.append(rw)
        return data


class SheetSource(DataSource):
    pass


class DataResult(object):
    pass


class CSVResult(DataResult):
    def __init__(self, fname):
        self.fname = fname

    def write(self, result):
        with open(self.fname, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['timestamp', 'DateFrom', 'DateTo', 'from', 'to',
                             'price', 'currency', 'airline'])
            for row in result:
                writer.writerow([
                    row['timestamp'].strftime('%Y-%m-%d'),
                    row['dateFrom'].strftime('%Y-%m-%d'),
                    row['dateTo'].strftime('%Y-%m-%d') if row['dateTo'] else '',
                    row['frm'],
                    row['to'],
                    row['price'], row['currency'],
                    row['carrier']
                    ])

    def add(self, result):
        # add a new result instead of overwriting
        # by shifting columns
        pass


class SheetResult(DataResult):
    pass


class SkyScan(object):
    # SkyScanner seems to better fit...
    ota_class = SkyScanner

    def process(self, fname, outfname='/tmp/output.csv'):
        reader = CSVSource()
        rows = reader.load(fname)

        ota = self.ota_class()

        results = []
        for row in rows:
            res = ota.query(row['DateFrom'], row['DateTo'],
                            row['from'], row['to'],
                            row['persons'])
            results.append(res)

        writer = CSVResult(outfname)
        writer.write(results)

    def test(self):
        self.ota_class = SkyScanner
        self.process('./input.csv')

        self.ota_class = SkyPicker
        self.process('./input.csv')


def main():
    fire.Fire(SkyScan)

if __name__ == '__main__':
    fire.Fire(SkyScan)
