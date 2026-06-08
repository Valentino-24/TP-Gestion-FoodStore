"""Add historial_estado_pedido, stock_cantidad, direccion_snapshot

Revision ID: a1b2c3d4e5f6
Revises: dfbff5817186
Create Date: 2026-05-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'dfbff5817186'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create historial_estado_pedido table
    op.create_table(
        'historial_estado_pedido',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pedido_id', sa.Integer(), sa.ForeignKey('pedido.id'), nullable=False, index=True),
        sa.Column('estado_desde', sa.String(50), nullable=True),
        sa.Column('estado_hasta', sa.String(50), nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuario.id'), nullable=True),
        sa.Column('observacion', sa.Text(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Add stock_cantidad to producto
    op.add_column(
        'producto',
        sa.Column('stock_cantidad', sa.Integer(), nullable=True, server_default='0'),
    )

    # Add direccion_snapshot to pedido
    op.add_column(
        'pedido',
        sa.Column('direccion_snapshot', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('pedido', 'direccion_snapshot')
    op.drop_column('producto', 'stock_cantidad')
    op.drop_table('historial_estado_pedido')
