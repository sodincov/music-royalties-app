"""rename Yoga column to yoga in album table

Revision ID: 00d7bd4fb44d
Revises: 550facfb6d88
Create Date: 2025-11-21 08:11:01.926155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00d7bd4fb44d'
down_revision: Union[str, Sequence[str], None] = '550facfb6d88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('album', 'Yoga', new_column_name='yoga')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
