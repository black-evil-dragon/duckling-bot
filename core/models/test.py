from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.db import BaseModel



class Product(BaseModel):
    # - Optional
    class Meta:
        table_name = "products"
    # -


    # - Fields
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    # -