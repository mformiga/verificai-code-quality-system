"""
Update uploaded_files table to store relative paths only

Revision ID: update_file_paths
Revises: initial
Create Date: 2025-11-12 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_file_paths'
down_revision = 'initial'
branch_labels = None
depends_on = None


def upgrade():
    """Update database to store relative paths only"""

    # First, backup existing data
    op.execute("""
        CREATE TABLE uploaded_files_backup AS
        SELECT * FROM uploaded_files
    """)

    # Update storage_path to be relative to backend/uploads
    op.execute("""
        UPDATE uploaded_files
        SET storage_path = REPLACE(
            storage_path,
            REPLACE(storage_path, SUBSTRING_INDEX(storage_path, 'uploads', -1), ''),
            'backend/uploads/'
        )
        WHERE storage_path LIKE '%uploads%'
    """)

    # Remove file_id prefix from file paths if they exist
    op.execute("""
        UPDATE uploaded_files
        SET file_path = REPLACE(
            file_path,
            CONCAT(SUBSTRING_INDEX(file_id, '_', 2), '_'),
            ''
        )
        WHERE file_path LIKE CONCAT(SUBSTRING_INDEX(file_id, '_', 2), '_%')
    """)


def downgrade():
    """Revert the changes"""

    # Restore from backup
    op.execute("""
        DELETE FROM uploaded_files
    """)

    op.execute("""
        INSERT INTO uploaded_files
        SELECT * FROM uploaded_files_backup
    """)

    # Drop backup table
    op.execute("DROP TABLE uploaded_files_backup")