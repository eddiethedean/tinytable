import csv
from typing import List, Generator

def combine_names_rows(column_names, rows) -> dict[str, List]:
    return dict(zip(column_names, map(list, zip(*rows))))


CsvChunk = Generator[dict[str, List], None, None]

def csv_chunks(f,
               chunk_size: int,
               dialect='excel',
               delimiter=','
) -> CsvChunk:
    if chunk_size < 1:
        raise ValueError('chunk_size must bee at least 1')
    #iterator = iter(csv.reader(f, dialect))
    iterator = iter(csv.reader(f,
                               dialect,
                               #quoting=csv.QUOTE_NONNUMERIC,
                               delimiter=delimiter))
    end_chunk = chunk_size
    column_names = []
    rows = []
    first = True
    i = 0
    while True:
        try:
            row = next(iterator)
            if first:
                column_names = row
                first = False
            else:
                rows.append(row)
                if i == end_chunk - 1:
                    end_chunk = end_chunk + chunk_size
                    yield combine_names_rows(column_names, rows)
                    rows = []
                i += 1
        except StopIteration:
            if len(rows) > 0:
                yield combine_names_rows(column_names, rows)
            break


if __name__ == '__main__':      
    with open('notebooks/ex_test.csv', 'r', newline='') as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        for chunk in csv_chunks(f, 3, dialect):
            print(chunk)