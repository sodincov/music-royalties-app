"""add approval system and remove unique constraints

Revision ID: 54f43ed396f2
Revises: a2bb0e864b03
Create Date: 2025-04-05 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '54f43ed396f2'
down_revision = 'a2bb0e864b03'
branch_labels = None
depends_on = None


def upgrade():
    # Безопасное удаление уникальных ограничений (если они существуют)
    constraints_to_drop = [
        ('person', 'person_email_key'),
        ('artist', 'artist_isni_key'),
        ('album', 'album_upc_key'),
        ('album', 'album_isrc_key'),
        ('track', 'track_isrc_key'),
    ]
    conn = op.get_bind()
    for table, constraint_name in constraints_to_drop:
        result = conn.execute(
            sa.text("""
                SELECT conname FROM pg_constraint
                WHERE conname = :constraint_name
                AND conrelid = (SELECT oid FROM pg_class WHERE relname = :table_name)
            """),
            {"constraint_name": constraint_name, "table_name": table}
        )
        if result.fetchone():
            op.drop_constraint(constraint_name, table, type_='unique')

    # === Person ===
    op.add_column('person', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('person', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_person_user', 'person', 'user', ['created_by_user_id'], ['id'], ondelete='SET NULL')

    # === Artist ===
    op.add_column('artist', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('artist', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_artist_user', 'artist', 'user', ['created_by_user_id'], ['id'], ondelete='SET NULL')

    # === Album ===
    op.add_column('album', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('album', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_album_user', 'album', 'user', ['created_by_user_id'], ['id'], ondelete='SET NULL')

    # === Track ===
    op.add_column('track', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('track', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_track_user', 'track', 'user', ['created_by_user_id'], ['id'], ondelete='SET NULL')


def downgrade():
    # Удаляем внешние ключи
    op.drop_constraint('fk_track_user', 'track', type_='foreignkey')
    op.drop_constraint('fk_album_user', 'album', type_='foreignkey')
    op.drop_constraint('fk_artist_user', 'artist', type_='foreignkey')
    op.drop_constraint('fk_person_user', 'person', type_='foreignkey')

    # Удаляем колонки
    op.drop_column('track', 'created_by_user_id')
    op.drop_column('track', 'is_approved')
    op.drop_column('album', 'created_by_user_id')
    op.drop_column('album', 'is_approved')
    op.drop_column('artist', 'created_by_user_id')
    op.drop_column('artist', 'is_approved')
    op.drop_column('person', 'created_by_user_id')
    op.drop_column('person', 'is_approved')