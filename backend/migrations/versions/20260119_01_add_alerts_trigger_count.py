"""add alerts.trigger_count

Revision ID: 20260119_01_add_alerts_trigger_count
Revises: 
Create Date: 2026-01-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260119_01_add_alerts_trigger_count"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add column if it does not exist (safe for already-migrated envs)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='alerts'
                  AND column_name='trigger_count'
            ) THEN
                ALTER TABLE alerts
                ADD COLUMN trigger_count INTEGER NOT NULL DEFAULT 0;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # Drop column if exists
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='alerts'
                  AND column_name='trigger_count'
            ) THEN
                ALTER TABLE alerts
                DROP COLUMN trigger_count;
            END IF;
        END $$;
        """
    )
