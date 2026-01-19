"""safety: ensure alerts.last_triggered exists

Revision ID: 20260119_02_alerts_last_triggered_safety
Revises: 20260119_01_add_alerts_trigger_count
Create Date: 2026-01-19

"""

from alembic import op

revision = "20260119_02_alerts_last_triggered_safety"
down_revision = "20260119_01_add_alerts_trigger_count"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='alerts'
                  AND column_name='last_triggered'
            ) THEN
                ALTER TABLE alerts
                ADD COLUMN last_triggered TIMESTAMP;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    pass
