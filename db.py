### 4. Plik `db.py` (jeśli potrzebny osobno)

Możesz zdecydować się na oddzielny plik `db.py`, jeśli chcesz oddzielić logikę bazy danych. Oto przykładowa zawartość:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()