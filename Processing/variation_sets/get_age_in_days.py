import csv
import sys

import sqlalchemy as sa
import db_backend as db


engine = None
conn = None


def setup(url):
    global engine, conn
    engine = sa.create_engine(url)
    conn = engine.connect()


def main():
    url = 'sqlite:///' + sys.argv[1]
    setup(url)

    s = sa.select([db.Session.id, db.Session.corpus, db.Session.target_child_fk, db.Speaker]).where(sa.and_(
        db.Session.target_child_fk == db.Speaker.uniquespeaker_id_fk,
        db.Session.id == db.Speaker.session_id_fk
    )).order_by(db.Session.id)
    query = conn.execute(s)

    header = ['session_id', 'corpus', 'age_in_days', 'unique_speaker_id', 'speaker_label', 'macrorole']
    with open('age_in_days.csv', 'w') as csvout:
        out = csv.writer(csvout, dialect='unix')
        out.writerow(header)
        for row in query:
            print(row)
            out.writerow([row[0], row[1], str(row[12]), str(row[2]), row[8], row[17]])
            # print(row[0], str(row[11]))
            print(row)


if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print()
    print("%s seconds --- Finished" % (time.time() - start_time))
