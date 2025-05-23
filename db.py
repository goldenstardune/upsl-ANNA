### 4. (Opcjonalny) Plik `db.py`

Jeśli chcesz mieć osobny plik do obsługi połączeń z bazą danych, możesz utworzyć `db.py`:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()
