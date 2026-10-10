"""Initial Amba schema.

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
revision="0001_initial"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("admin_users",sa.Column("id",sa.Integer,primary_key=True),sa.Column("email",sa.String(255),nullable=False),sa.Column("password_hash",sa.String(255),nullable=False),sa.Column("is_active",sa.Boolean,nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()")),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("now()")),sa.Column("last_login",sa.DateTime(timezone=True)));op.create_index("ix_admin_users_email","admin_users",["email"],unique=True)
 op.create_table("properties",sa.Column("id",sa.Integer,primary_key=True),sa.Column("title",sa.String(255),nullable=False),sa.Column("slug",sa.String(280),nullable=False),sa.Column("description",sa.Text),sa.Column("location",sa.String(255)),sa.Column("city",sa.String(100)),sa.Column("state",sa.String(100)),sa.Column("property_type",sa.String(40)),sa.Column("status",sa.String(20),nullable=False),sa.Column("price",sa.Numeric(14,2)),sa.Column("currency",sa.String(8)),sa.Column("area",sa.String(100)),sa.Column("bedrooms",sa.Integer),sa.Column("bathrooms",sa.Integer),sa.Column("featured",sa.Boolean,nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()")),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("now()")));op.create_index("ix_properties_slug","properties",["slug"],unique=True);op.create_index("ix_properties_status","properties",["status"])
 op.create_table("property_images",sa.Column("id",sa.Integer,primary_key=True),sa.Column("property_id",sa.Integer,sa.ForeignKey("properties.id",ondelete="CASCADE"),nullable=False),sa.Column("image_url",sa.String(1000),nullable=False),sa.Column("alt_text",sa.String(255)),sa.Column("sort_order",sa.Integer,nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()")))
 for table,consult in (("enquiries",False),("consultation_requests",True)):
  cols=[sa.Column("id",sa.Integer,primary_key=True),sa.Column("name",sa.String(120),nullable=False),sa.Column("email",sa.String(255),nullable=False),sa.Column("phone",sa.String(50)),sa.Column("requirement",sa.String(120)),sa.Column("message",sa.Text),sa.Column("status",sa.String(20),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"))]
  if consult: cols.insert(5,sa.Column("preferred_contact_method",sa.String(40)))
  else: cols.append(sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("now()")))
  op.create_table(table,*cols);op.create_index(f"ix_{table}_status",table,["status"])
 op.create_table("business_settings",sa.Column("id",sa.Integer,primary_key=True),sa.Column("business_name",sa.String(255),nullable=False),sa.Column("email",sa.String(255),nullable=False),sa.Column("phone",sa.String(50),nullable=False),sa.Column("address",sa.String(500),nullable=False),sa.Column("city",sa.String(100),nullable=False),sa.Column("state",sa.String(100),nullable=False),sa.Column("postal_code",sa.String(20),nullable=False),sa.Column("country",sa.String(100),nullable=False),sa.Column("website",sa.String(255),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.text("now()")))
def downgrade():
 for table in ["business_settings","consultation_requests","enquiries","property_images","properties","admin_users"]:op.drop_table(table)
