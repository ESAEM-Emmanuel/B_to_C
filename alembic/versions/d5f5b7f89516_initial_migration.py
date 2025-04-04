"""Initial migration

Revision ID: d5f5b7f89516
Revises: 
Create Date: 2025-03-29 08:34:28.684138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5f5b7f89516'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article_states',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_article_states_id'), 'article_states', ['id'], unique=True)
    op.create_index(op.f('ix_article_states_name'), 'article_states', ['name'], unique=True)
    op.create_table('category_articles',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('image', sa.String(length=255), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_category_articles_id'), 'category_articles', ['id'], unique=True)
    op.create_index(op.f('ix_category_articles_name'), 'category_articles', ['name'], unique=True)
    op.create_table('countries',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_countries_id'), 'countries', ['id'], unique=True)
    op.create_index(op.f('ix_countries_name'), 'countries', ['name'], unique=True)
    op.create_table('privileges',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_privileges_id'), 'privileges', ['id'], unique=True)
    op.create_index(op.f('ix_privileges_name'), 'privileges', ['name'], unique=True)
    op.create_table('roles',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=True)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    op.create_table('sliding_scale_tariffs',
    sa.Column('days_min', sa.Integer(), nullable=False),
    sa.Column('max_days', sa.Integer(), nullable=False),
    sa.Column('rate', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('ACTIF', 'INACTIF', name='statusproposition'), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_sliding_scale_tariffs_id'), 'sliding_scale_tariffs', ['id'], unique=True)
    op.create_table('subscription_types',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('advertisements', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('price_max_article', sa.Float(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('ACTIF', 'INACTIF', name='statusproposition'), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_subscription_types_id'), 'subscription_types', ['id'], unique=True)
    op.create_index(op.f('ix_subscription_types_name'), 'subscription_types', ['name'], unique=True)
    op.create_table('tax_intervals',
    sa.Column('min_price', sa.Float(), nullable=True),
    sa.Column('max_price', sa.Float(), nullable=True),
    sa.Column('daily_rate', sa.Float(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_tax_intervals_id'), 'tax_intervals', ['id'], unique=True)
    op.create_table('volume_discounts',
    sa.Column('threshold', sa.Integer(), nullable=False),
    sa.Column('reduction', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('ACTIF', 'INACTIF', name='statusproposition'), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_volume_discounts_id'), 'volume_discounts', ['id'], unique=True)
    op.create_table('privilege_roles',
    sa.Column('role_id', sa.String(), nullable=False),
    sa.Column('privilege_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['privilege_id'], ['privileges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_privilege_roles_id'), 'privilege_roles', ['id'], unique=True)
    op.create_table('towns',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('country_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_towns_id'), 'towns', ['id'], unique=True)
    op.create_index(op.f('ix_towns_name'), 'towns', ['name'], unique=False)
    op.create_table('users',
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('gender', sa.Enum('M', 'F', name='gendertype'), nullable=True),
    sa.Column('image', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('is_staff', sa.Boolean(), nullable=True),
    sa.Column('town_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['town_id'], ['towns.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('articles',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('reception_place', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=True),
    sa.Column('phone_transaction', sa.String(length=15), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('main_image', sa.String(length=255), nullable=False),
    sa.Column('other_images', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('nb_visite', sa.Integer(), server_default=sa.text('0'), nullable=True),
    sa.Column('status', sa.Enum('EN_ATTENTE', 'PUBLIEE', 'EXPIRE', 'ABANDONNE', name='statusarticle'), nullable=True),
    sa.Column('daily_rate', sa.Float(), nullable=True),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('town_id', sa.String(), nullable=False),
    sa.Column('category_article_id', sa.String(), nullable=False),
    sa.Column('article_state_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_state_id'], ['article_states.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_article_id'], ['category_articles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['town_id'], ['towns.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_articles_id'), 'articles', ['id'], unique=True)
    op.create_index(op.f('ix_articles_name'), 'articles', ['name'], unique=True)
    op.create_index(op.f('ix_articles_phone'), 'articles', ['phone'], unique=False)
    op.create_index(op.f('ix_articles_phone_transaction'), 'articles', ['phone_transaction'], unique=False)
    op.create_table('privilege_users',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('privilege_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['privilege_id'], ['privileges.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_privilege_users_id'), 'privilege_users', ['id'], unique=True)
    op.create_table('subscriptions',
    sa.Column('subscription_type_id', sa.String(), nullable=False),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('remaining_advertisements', sa.Integer(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('status', sa.Enum('ACTIF', 'INACTIF', name='statusproposition'), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subscription_type_id'], ['subscription_types.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=True)
    op.create_table('user_roles',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('role_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=True)
    op.create_table('favorites',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=True)
    op.create_table('notifications',
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=True)
    op.create_table('payments',
    sa.Column('payment_number', sa.String(), nullable=True),
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('payment_number'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=True)
    op.create_table('signals',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('offender_id', sa.String(), nullable=False),
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('refnumber', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['offender_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refnumber')
    )
    op.create_index(op.f('ix_signals_id'), 'signals', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_signals_id'), table_name='signals')
    op.drop_table('signals')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_favorites_id'), table_name='favorites')
    op.drop_table('favorites')
    op.drop_index(op.f('ix_user_roles_id'), table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_privilege_users_id'), table_name='privilege_users')
    op.drop_table('privilege_users')
    op.drop_index(op.f('ix_articles_phone_transaction'), table_name='articles')
    op.drop_index(op.f('ix_articles_phone'), table_name='articles')
    op.drop_index(op.f('ix_articles_name'), table_name='articles')
    op.drop_index(op.f('ix_articles_id'), table_name='articles')
    op.drop_table('articles')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_towns_name'), table_name='towns')
    op.drop_index(op.f('ix_towns_id'), table_name='towns')
    op.drop_table('towns')
    op.drop_index(op.f('ix_privilege_roles_id'), table_name='privilege_roles')
    op.drop_table('privilege_roles')
    op.drop_index(op.f('ix_volume_discounts_id'), table_name='volume_discounts')
    op.drop_table('volume_discounts')
    op.drop_index(op.f('ix_tax_intervals_id'), table_name='tax_intervals')
    op.drop_table('tax_intervals')
    op.drop_index(op.f('ix_subscription_types_name'), table_name='subscription_types')
    op.drop_index(op.f('ix_subscription_types_id'), table_name='subscription_types')
    op.drop_table('subscription_types')
    op.drop_index(op.f('ix_sliding_scale_tariffs_id'), table_name='sliding_scale_tariffs')
    op.drop_table('sliding_scale_tariffs')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_privileges_name'), table_name='privileges')
    op.drop_index(op.f('ix_privileges_id'), table_name='privileges')
    op.drop_table('privileges')
    op.drop_index(op.f('ix_countries_name'), table_name='countries')
    op.drop_index(op.f('ix_countries_id'), table_name='countries')
    op.drop_table('countries')
    op.drop_index(op.f('ix_category_articles_name'), table_name='category_articles')
    op.drop_index(op.f('ix_category_articles_id'), table_name='category_articles')
    op.drop_table('category_articles')
    op.drop_index(op.f('ix_article_states_name'), table_name='article_states')
    op.drop_index(op.f('ix_article_states_id'), table_name='article_states')
    op.drop_table('article_states')
    # ### end Alembic commands ###
