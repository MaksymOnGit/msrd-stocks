"""empty message

Revision ID: 29d84ec1fbc8
Revises: b71f398ad74b
Create Date: 2022-11-22 04:39:26.907585

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "29d84ec1fbc8"
down_revision = "b71f398ad74b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "document_statuses", sa.Column("created", sa.DateTime(), nullable=False)
    )
    op.add_column(
        "document_statuses", sa.Column("updated", sa.DateTime(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("document_statuses", "updated")
    op.drop_column("document_statuses", "created")
    # ### end Alembic commands ###
