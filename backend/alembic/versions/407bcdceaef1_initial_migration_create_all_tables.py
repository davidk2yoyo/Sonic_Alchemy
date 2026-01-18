"""Initial migration - create all tables

Revision ID: 407bcdceaef1
Revises: 
Create Date: 2026-01-17 20:27:18.955405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '407bcdceaef1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table first (no dependencies)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create child tables without foreign keys to projects first
    op.create_table('canvases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=False),
    sa.Column('emotion_analysis', sa.JSON(), nullable=True),
    sa.Column('music_generation_prompt', sa.Text(), nullable=True),
    sa.Column('generated_music_url', sa.String(length=500), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_canvases_id'), 'canvases', ['id'], unique=False)
    op.create_index(op.f('ix_canvases_project_id'), 'canvases', ['project_id'], unique=False)
    
    op.create_table('lyrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('theme', sa.Text(), nullable=True),
    sa.Column('generated_lyrics', sa.Text(), nullable=False),
    sa.Column('edited_lyrics', sa.Text(), nullable=True),
    sa.Column('structure', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lyrics_id'), 'lyrics', ['id'], unique=False)
    op.create_index(op.f('ix_lyrics_project_id'), 'lyrics', ['project_id'], unique=False)
    
    op.create_table('voice_recordings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('raw_audio_url', sa.String(length=500), nullable=False),
    sa.Column('processed_audio_url', sa.String(length=500), nullable=True),
    sa.Column('style', sa.String(length=100), nullable=True),
    sa.Column('corrections_applied', sa.JSON(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('duration_seconds', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_voice_recordings_id'), 'voice_recordings', ['id'], unique=False)
    op.create_index(op.f('ix_voice_recordings_project_id'), 'voice_recordings', ['project_id'], unique=False)
    
    # Create projects table (depends on users and child tables)
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('canvas_id', sa.Integer(), nullable=True),
    sa.Column('voice_recording_id', sa.Integer(), nullable=True),
    sa.Column('lyrics_id', sa.Integer(), nullable=True),
    sa.Column('project_metadata', sa.JSON(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['canvas_id'], ['canvases.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['lyrics_id'], ['lyrics.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['voice_recording_id'], ['voice_recordings.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    
    # Add foreign keys from child tables to projects
    op.create_foreign_key('fk_canvases_project_id', 'canvases', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_lyrics_project_id', 'lyrics', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_voice_recordings_project_id', 'voice_recordings', 'projects', ['project_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign keys first
    op.drop_constraint('fk_voice_recordings_project_id', 'voice_recordings', type_='foreignkey')
    op.drop_constraint('fk_lyrics_project_id', 'lyrics', type_='foreignkey')
    op.drop_constraint('fk_canvases_project_id', 'canvases', type_='foreignkey')
    
    # Drop tables in reverse order
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    op.drop_index(op.f('ix_voice_recordings_project_id'), table_name='voice_recordings')
    op.drop_index(op.f('ix_voice_recordings_id'), table_name='voice_recordings')
    op.drop_table('voice_recordings')
    
    op.drop_index(op.f('ix_lyrics_project_id'), table_name='lyrics')
    op.drop_index(op.f('ix_lyrics_id'), table_name='lyrics')
    op.drop_table('lyrics')
    
    op.drop_index(op.f('ix_canvases_project_id'), table_name='canvases')
    op.drop_index(op.f('ix_canvases_id'), table_name='canvases')
    op.drop_table('canvases')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
