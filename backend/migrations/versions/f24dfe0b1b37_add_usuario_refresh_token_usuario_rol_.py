"""add usuario, refresh_token, and usuario_rol tables

Revision ID: f24dfe0b1b37
Revises:
Create Date: 2026-05-05 19:22:24.054679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f24dfe0b1b37'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'usuario',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellido', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('eliminado_en', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('usuario_pkey')),
    )
    op.create_index(op.f('ix_usuario_email'), 'usuario', ['email'], unique=True)

    op.create_table(
        'refresh_token',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('family_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['usuario.id'], name=op.f('refresh_token_user_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('refresh_token_pkey')),
    )
    op.create_index(op.f('ix_refresh_token_token_hash'), 'refresh_token', ['token_hash'], unique=True)
    op.create_index(op.f('ix_refresh_token_family_id'), 'refresh_token', ['family_id'])

    op.create_table(
        'usuario_rol',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], name=op.f('usuario_rol_usuario_id_fkey'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rol_id'], ['rol.id'], name=op.f('usuario_rol_rol_id_fkey'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('usuario_rol_pkey')),
        sa.UniqueConstraint('usuario_id', 'rol_id', name=op.f('uq_usuario_rol')),
    )


def downgrade() -> None:
    op.drop_table('usuario_rol')
    op.drop_table('refresh_token')
    op.drop_table('usuario')
