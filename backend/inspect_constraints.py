from app.database import engine
import sqlalchemy as sa

with engine.connect() as conn:
    rows = conn.execute(sa.text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'patients'::regclass AND contype = 'u'"))
    for row in rows:
        print(row)
