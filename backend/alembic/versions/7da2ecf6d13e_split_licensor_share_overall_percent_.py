"""Split licensor_share_overall_percent into separate author and neighboring rights percentages

Revision ID: ваш_новый_id
Revises: ваш_предыдущий_id
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ваш_новый_id'
down_revision = "00d7bd4fb44d"
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем новые столбцы
    op.add_column('usage_report', sa.Column('licensor_share_author_licensor_percent', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('usage_report', sa.Column('licensor_share_neighboring_licensor_percent', sa.Float(), nullable=False, server_default='0.0'))

    # Удаляем старый столбец
    op.drop_column('usage_report', 'licensor_share_overall_percent')

def downgrade():
    # Возвращаем старый столбец
    op.add_column('usage_report', sa.Column('licensor_share_overall_percent', sa.Float(), nullable=True))

    # Удаляем новые столбцы
    op.drop_column('usage_report', 'licensor_share_neighboring_licensor_percent')
    op.drop_column('usage_report', 'licensor_share_author_licensor_percent')