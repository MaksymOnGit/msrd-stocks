"""empty message

Revision ID: b71f398ad74b
Revises:
Create Date: 2022-11-22 03:28:07.571934

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b71f398ad74b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "document_statuses",
        sa.Column("document_id", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("document_id"),
    )
    op.create_table(
        "stock_records",
        sa.Column("stock_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.String(length=24), nullable=False),
        sa.Column("change_source_id", sa.String(length=100), nullable=True),
        sa.Column(
            "quantity_change", sa.Float(precision=2, asdecimal=True), nullable=False
        ),
        sa.Column("quantity_change_direction", sa.Integer(), nullable=False),
        sa.Column(
            "quantity_before", sa.Float(precision=2, asdecimal=True), nullable=False
        ),
        sa.Column(
            "quantity_actual", sa.Float(precision=2, asdecimal=True), nullable=False
        ),
        sa.Column("change_datetime", sa.DateTime(), nullable=False),
        sa.Column(
            "previous_stock_record_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["change_source_id"],
            ["document_statuses.document_id"],
        ),
        sa.ForeignKeyConstraint(
            ["previous_stock_record_id"],
            ["stock_records.stock_record_id"],
        ),
        sa.PrimaryKeyConstraint("stock_record_id"),
        sa.UniqueConstraint("previous_stock_record_id"),
    )

    op.execute("ALTER TABLE stock_records ADD CONSTRAINT product_id__change_source_id_uniqe UNIQUE NULLS NOT DISTINCT (product_id, change_source_id);")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("stock_records")
    op.drop_table("document_statuses")
    # ### end Alembic commands ###
