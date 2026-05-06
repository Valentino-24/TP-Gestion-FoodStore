"""UsuarioRol association table for user-role M:N relationship."""

from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, func, Column
from sqlmodel import SQLModel, Field


class UsuarioRol(SQLModel, table=True):
    """Association table linking users to roles (M:N)."""

    __tablename__ = "usuario_rol"
    __table_args__ = (
        UniqueConstraint("usuario_id", "rol_id", name="uq_usuario_rol"),
    )

    id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))
    usuario_id: int = Field(
        sa_column=Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
    )
    rol_id: int = Field(
        sa_column=Column(Integer, ForeignKey("rol.id", ondelete="CASCADE"), nullable=False),
    )
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
