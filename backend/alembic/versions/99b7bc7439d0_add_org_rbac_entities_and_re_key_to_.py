"""add org rbac entities and re-key to organization_id

Revision ID: 99b7bc7439d0
Revises: f46e9b10ec7a
Create Date: 2026-08-29 09:29:39.741860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column
import secrets
import slugify

# revision identifiers, used by Alembic.
revision: str = '99b7bc7439d0'
down_revision: Union[str, Sequence[str], None] = 'f46e9b10ec7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _generate_slug(name: str, existing_slugs: set) -> str:
    """Generate a unique slug from organization name."""
    base = slugify.slugify(name) or "clinic"
    slug = base
    counter = 1
    while slug in existing_slugs:
        counter += 1
        slug = f"{base}-{counter}"
    existing_slugs.add(slug)
    return slug


def upgrade() -> None:
    """Upgrade schema."""
    # ### Create new tables ###
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('before', sa.Text(), nullable=True),
        sa.Column('after', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_actor_user_id'), 'audit_logs', ['actor_user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_organization_id'), 'audit_logs', ['organization_id'], unique=False)

    op.create_table('doctor_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('specialty', sa.String(), nullable=True),
        sa.Column('registration_number', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_doctor_profiles_id'), 'doctor_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_doctor_profiles_organization_id'), 'doctor_profiles', ['organization_id'], unique=False)
    op.create_index(op.f('ix_doctor_profiles_user_id'), 'doctor_profiles', ['user_id'], unique=True)

    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)

    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_code'), 'roles', ['code'], unique=False)
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_organization_id'), 'roles', ['organization_id'], unique=False)

    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
    )
    op.create_index(op.f('ix_role_permissions_id'), 'role_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_role_permissions_permission_id'), 'role_permissions', ['permission_id'], unique=False)
    op.create_index(op.f('ix_role_permissions_role_id'), 'role_permissions', ['role_id'], unique=False)

    op.create_table('user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', 'organization_id', name='uq_user_role_org')
    )
    op.create_index(op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=False)
    op.create_index(op.f('ix_user_roles_organization_id'), 'user_roles', ['organization_id'], unique=False)
    op.create_index(op.f('ix_user_roles_role_id'), 'user_roles', ['role_id'], unique=False)
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'], unique=False)

    # ### Seed permissions ###
    permissions_table = table('permissions',
        column('id', sa.Integer),
        column('code', sa.String),
        column('description', sa.String),
        column('created_at', sa.DateTime),
    )
    op.bulk_insert(permissions_table, [
        {'code': 'patient:view', 'description': 'View patient records'},
        {'code': 'patient:create', 'description': 'Create patient records'},
        {'code': 'patient:edit', 'description': 'Edit patient records'},
        {'code': 'patient:delete', 'description': 'Delete patient records'},
        {'code': 'patient:merge', 'description': 'Merge duplicate patients'},
        {'code': 'appointment:view', 'description': 'View appointments'},
        {'code': 'appointment:create', 'description': 'Create appointments'},
        {'code': 'appointment:edit', 'description': 'Edit appointments'},
        {'code': 'appointment:delete', 'description': 'Delete appointments'},
        {'code': 'appointment:checkin', 'description': 'Check-in patients'},
        {'code': 'treatment:view', 'description': 'View treatments'},
        {'code': 'treatment:create', 'description': 'Create treatments'},
        {'code': 'treatment:edit', 'description': 'Edit treatments'},
        {'code': 'treatment:delete', 'description': 'Delete treatments'},
        {'code': 'bill:view', 'description': 'View bills'},
        {'code': 'bill:create', 'description': 'Create bills'},
        {'code': 'bill:edit', 'description': 'Edit bills'},
        {'code': 'bill:delete', 'description': 'Delete bills'},
        {'code': 'bill:refund', 'description': 'Process refunds'},
        {'code': 'dashboard:view', 'description': 'View dashboard'},
        {'code': 'attachment:view', 'description': 'View attachments'},
        {'code': 'attachment:upload', 'description': 'Upload attachments'},
        {'code': 'attachment:delete', 'description': 'Delete attachments'},
        {'code': 'role:manage', 'description': 'Manage roles and permissions'},
        {'code': 'user:manage', 'description': 'Manage users'},
        {'code': 'org:manage', 'description': 'Manage organization settings'},
    ])

    # ### Seed system-level roles (organization_id = NULL) ###
    roles_table = table('roles',
        column('id', sa.Integer),
        column('name', sa.String),
        column('code', sa.String),
        column('organization_id', sa.Integer),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime),
    )
    op.bulk_insert(roles_table, [
        {'name': 'Admin', 'code': 'admin', 'organization_id': None},
        {'name': 'Doctor', 'code': 'doctor', 'organization_id': None},
        {'name': 'Receptionist', 'code': 'receptionist', 'organization_id': None},
    ])

    # ### Migrate existing doctors to organizations + users + doctor_profiles ###
    conn = op.get_bind()

    # Get existing doctors
    doctors = conn.execute(sa.text("SELECT id, name, email, hashed_password, clinic_name FROM doctors")).fetchall()

    # Map old doctor_id -> new organization_id, user_id, doctor_profile_id
    doctor_migration_map = {}

    existing_slugs = set()
    for doc in doctors:
        old_doctor_id, name, email, hashed_password, clinic_name = doc
        org_name = clinic_name or f"{name}'s Clinic"
        slug = _generate_slug(org_name, existing_slugs)

        # Create organization
        result = conn.execute(
            sa.text("""
                INSERT INTO organizations (name, slug, created_at, updated_at)
                VALUES (:name, :slug, now(), now())
                RETURNING id
            """),
            {'name': org_name, 'slug': slug}
        )
        org_id = result.scalar()

        # Create user
        result = conn.execute(
            sa.text("""
                INSERT INTO users (email, hashed_password, name, is_active, created_at, updated_at)
                VALUES (:email, :hashed_password, :name, true, now(), now())
                RETURNING id
            """),
            {'email': email, 'hashed_password': hashed_password, 'name': name}
        )
        user_id = result.scalar()

        # Create doctor_profile
        result = conn.execute(
            sa.text("""
                INSERT INTO doctor_profiles (user_id, organization_id, name, is_active, color, created_at, updated_at)
                VALUES (:user_id, :org_id, :name, true, '#3B82F6', now(), now())
                RETURNING id
            """),
            {'user_id': user_id, 'org_id': org_id, 'name': name}
        )
        doctor_profile_id = result.scalar()

        # Assign Admin role to this user in this organization
        admin_role = conn.execute(
            sa.text("SELECT id FROM roles WHERE code = 'admin' AND organization_id IS NULL")
        ).scalar()
        conn.execute(
            sa.text("""
                INSERT INTO user_roles (user_id, role_id, organization_id, created_at)
                VALUES (:user_id, :role_id, :org_id, now())
            """),
            {'user_id': user_id, 'role_id': admin_role, 'org_id': org_id}
        )

        doctor_migration_map[old_doctor_id] = {
            'org_id': org_id,
            'user_id': user_id,
            'doctor_profile_id': doctor_profile_id,
        }

    # ### Now add organization_id columns (nullable=True initially) and populate them ###
    # Patients
    op.add_column('patients', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('patients', sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=True))

    for old_doctor_id, mapping in doctor_migration_map.items():
        conn.execute(
            sa.text("UPDATE patients SET organization_id = :org_id WHERE doctor_id = :old_doctor_id"),
            {'org_id': mapping['org_id'], 'old_doctor_id': old_doctor_id}
        )

    # Appointments
    op.add_column('appointments', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('appointments', sa.Column('start_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('appointments', sa.Column('end_at', sa.DateTime(timezone=True), nullable=True))

    for old_doctor_id, mapping in doctor_migration_map.items():
        conn.execute(
            sa.text("UPDATE appointments SET organization_id = :org_id WHERE doctor_id = :old_doctor_id"),
            {'org_id': mapping['org_id'], 'old_doctor_id': old_doctor_id}
        )

    # Treatments
    op.add_column('treatments', sa.Column('organization_id', sa.Integer(), nullable=True))

    for old_doctor_id, mapping in doctor_migration_map.items():
        conn.execute(
            sa.text("UPDATE treatments SET organization_id = :org_id WHERE doctor_id = :old_doctor_id"),
            {'org_id': mapping['org_id'], 'old_doctor_id': old_doctor_id}
        )

    # Bills
    op.add_column('bills', sa.Column('organization_id', sa.Integer(), nullable=True))

    for old_doctor_id, mapping in doctor_migration_map.items():
        conn.execute(
            sa.text("UPDATE bills SET organization_id = :org_id WHERE doctor_id = :old_doctor_id"),
            {'org_id': mapping['org_id'], 'old_doctor_id': old_doctor_id}
        )

    # Patient Attachments
    op.add_column('patient_attachments', sa.Column('organization_id', sa.Integer(), nullable=True))

    for old_doctor_id, mapping in doctor_migration_map.items():
        conn.execute(
            sa.text("UPDATE patient_attachments SET organization_id = :org_id WHERE doctor_id = :old_doctor_id"),
            {'org_id': mapping['org_id'], 'old_doctor_id': old_doctor_id}
        )

    # ### Migrate appointment_date (string) to start_at/end_at (datetime) ###
    # Parse the string dates and set start_at/end_at (assume 30 min duration if only date)
    appointments = conn.execute(sa.text("SELECT id, appointment_date FROM appointments WHERE start_at IS NULL")).fetchall()
    for appt_id, appt_date_str in appointments:
        try:
            # Try parsing as datetime first
            if 'T' in appt_date_str or ' ' in appt_date_str:
                start_dt = sa.text(f"'{appt_date_str}'::timestamptz")
            else:
                # Just a date, assume 9:00 AM
                start_dt = sa.text(f"('{appt_date_str} 09:00:00')::timestamptz")
            end_dt = sa.text(f"({start_dt} + interval '30 minutes')")
            conn.execute(
                sa.text(f"UPDATE appointments SET start_at = {start_dt}, end_at = {end_dt} WHERE id = :id"),
                {'id': appt_id}
            )
        except Exception:
            # Fallback to now
            conn.execute(
                sa.text("UPDATE appointments SET start_at = now(), end_at = now() + interval '30 minutes' WHERE id = :id"),
                {'id': appt_id}
            )

    # ### Now make organization_id NOT NULL and add FKs ###
    # Patients
    op.create_index(op.f('ix_patients_organization_id'), 'patients', ['organization_id'], unique=False)
    op.drop_constraint(op.f('uq_patient_doctor_email'), 'patients', type_='unique')
    op.drop_constraint(op.f('uq_patient_doctor_phone'), 'patients', type_='unique')
    op.create_unique_constraint('uq_patient_org_email', 'patients', ['organization_id', 'email'])
    op.create_unique_constraint('uq_patient_org_phone', 'patients', ['organization_id', 'phone'])
    op.create_foreign_key(None, 'patients', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'patients', 'doctor_profiles', ['doctor_id'], ['id'], ondelete='SET NULL')
    op.alter_column('patients', 'organization_id', nullable=False)
    op.drop_column('patients', 'age')
    op.drop_column('patients', 'address')
    op.alter_column('patients', 'blood_group', existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=True)
    op.alter_column('patients', 'medical_history', existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=True)

    # Appointments
    op.create_index(op.f('ix_appointments_organization_id'), 'appointments', ['organization_id'], unique=False)
    op.create_index(op.f('ix_appointments_start_at'), 'appointments', ['start_at'], unique=False)
    op.create_index(op.f('ix_appointments_end_at'), 'appointments', ['end_at'], unique=False)
    op.drop_constraint(op.f('appointments_patient_id_fkey'), 'appointments', type_='foreignkey')
    op.create_foreign_key(None, 'appointments', 'patients', ['patient_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'appointments', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'appointments', 'doctor_profiles', ['doctor_id'], ['id'], ondelete='CASCADE')
    op.alter_column('appointments', 'organization_id', nullable=False)
    op.alter_column('appointments', 'start_at', nullable=False)
    op.alter_column('appointments', 'end_at', nullable=False)
    op.drop_column('appointments', 'appointment_date')

    # Treatments
    op.create_index(op.f('ix_treatments_organization_id'), 'treatments', ['organization_id'], unique=False)
    op.drop_constraint(op.f('treatments_patient_id_fkey'), 'treatments', type_='foreignkey')
    op.create_foreign_key(None, 'treatments', 'patients', ['patient_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'treatments', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'treatments', 'doctor_profiles', ['doctor_id'], ['id'], ondelete='CASCADE')
    op.alter_column('treatments', 'organization_id', nullable=False)

    # Bills
    op.create_index(op.f('ix_bills_organization_id'), 'bills', ['organization_id'], unique=False)
    op.drop_constraint(op.f('bills_patient_id_fkey'), 'bills', type_='foreignkey')
    op.create_foreign_key(None, 'bills', 'patients', ['patient_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'bills', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'bills', 'doctor_profiles', ['doctor_id'], ['id'], ondelete='CASCADE')
    op.alter_column('bills', 'organization_id', nullable=False)

    # Patient Attachments
    op.create_index(op.f('ix_patient_attachments_organization_id'), 'patient_attachments', ['organization_id'], unique=False)
    op.drop_constraint(op.f('patient_attachments_doctor_id_fkey'), 'patient_attachments', type_='foreignkey')
    op.create_foreign_key(None, 'patient_attachments', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'patient_attachments', 'doctor_profiles', ['doctor_id'], ['id'], ondelete='CASCADE')
    op.alter_column('patient_attachments', 'organization_id', nullable=False)

    # Doctors table - keep for backward compat but mark clinic_name as NOT NULL
    # First populate NULL created_at/updated_at
    conn.execute(sa.text("UPDATE doctors SET created_at = now() WHERE created_at IS NULL"))
    conn.execute(sa.text("UPDATE doctors SET updated_at = now() WHERE updated_at IS NULL"))
    op.alter_column('doctors', 'clinic_name', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('doctors', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=False)
    op.alter_column('doctors', 'updated_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=False)

    # ### Seed role_permissions for system roles ###
    # Admin gets all permissions
    admin_role_id = conn.execute(sa.text("SELECT id FROM roles WHERE code = 'admin' AND organization_id IS NULL")).scalar()
    all_perm_ids = [row[0] for row in conn.execute(sa.text("SELECT id FROM permissions")).fetchall()]
    for perm_id in all_perm_ids:
        conn.execute(
            sa.text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id) ON CONFLICT DO NOTHING"),
            {'role_id': admin_role_id, 'perm_id': perm_id}
        )

    # Doctor role permissions
    doctor_role_id = conn.execute(sa.text("SELECT id FROM roles WHERE code = 'doctor' AND organization_id IS NULL")).scalar()
    doctor_perms = [
        'patient:view', 'patient:create', 'patient:edit',
        'appointment:view', 'appointment:create', 'appointment:edit', 'appointment:checkin',
        'treatment:view', 'treatment:create', 'treatment:edit',
        'bill:view', 'bill:create', 'bill:edit',
        'dashboard:view',
        'attachment:view', 'attachment:upload', 'attachment:delete',
    ]
    for perm_code in doctor_perms:
        perm_id = conn.execute(sa.text("SELECT id FROM permissions WHERE code = :code"), {'code': perm_code}).scalar()
        if perm_id:
            conn.execute(
                sa.text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id) ON CONFLICT DO NOTHING"),
                {'role_id': doctor_role_id, 'perm_id': perm_id}
            )

    # Receptionist role permissions
    reception_role_id = conn.execute(sa.text("SELECT id FROM roles WHERE code = 'receptionist' AND organization_id IS NULL")).scalar()
    reception_perms = [
        'patient:view', 'patient:create', 'patient:edit',
        'appointment:view', 'appointment:create', 'appointment:edit', 'appointment:checkin',
        'bill:view', 'bill:create', 'bill:edit',
        'dashboard:view',
        'attachment:view', 'attachment:upload',
    ]
    for perm_code in reception_perms:
        perm_id = conn.execute(sa.text("SELECT id FROM permissions WHERE code = :code"), {'code': perm_code}).scalar()
        if perm_id:
            conn.execute(
                sa.text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id) ON CONFLICT DO NOTHING"),
                {'role_id': reception_role_id, 'perm_id': perm_id}
            )


def downgrade() -> None:
    """Downgrade schema."""
    # ### Drop new tables ###
    op.drop_constraint(None, 'treatments', type_='foreignkey')
    op.drop_constraint(None, 'treatments', type_='foreignkey')
    op.drop_constraint(None, 'treatments', type_='foreignkey')
    op.create_foreign_key(op.f('treatments_patient_id_fkey'), 'treatments', 'patients', ['patient_id'], ['id'])
    op.drop_index(op.f('ix_treatments_patient_id'), table_name='treatments')
    op.drop_index(op.f('ix_treatments_organization_id'), table_name='treatments')
    op.drop_index(op.f('ix_treatments_doctor_id'), table_name='treatments')
    op.alter_column('treatments', 'updated_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('treatments', 'created_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('treatments', 'status',
                existing_type=sa.VARCHAR(),
                nullable=True)
    op.alter_column('treatments', 'doctor_id',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.alter_column('treatments', 'patient_id',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.drop_column('treatments', 'organization_id')

    op.add_column('patients', sa.Column('address', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('patients', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'patients', type_='foreignkey')
    op.drop_constraint(None, 'patients', type_='foreignkey')
    op.drop_constraint('uq_patient_org_phone', 'patients', type_='unique')
    op.drop_constraint('uq_patient_org_email', 'patients', type_='unique')
    op.drop_index(op.f('ix_patients_organization_id'), table_name='patients')
    op.drop_index(op.f('ix_patients_doctor_id'), table_name='patients')
    op.create_unique_constraint(op.f('uq_patient_doctor_phone'), 'patients', ['doctor_id', 'phone'])
    op.create_unique_constraint(op.f('uq_patient_doctor_email'), 'patients', ['doctor_id', 'email'])
    op.alter_column('patients', 'updated_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('patients', 'created_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('patients', 'medical_history',
                existing_type=sa.String(),
                type_=sa.TEXT(),
                existing_nullable=True)
    op.alter_column('patients', 'blood_group',
                existing_type=sa.String(),
                type_=sa.TEXT(),
                existing_nullable=True)
    op.drop_column('patients', 'date_of_birth')
    op.drop_column('patients', 'organization_id')

    op.drop_constraint(None, 'patient_attachments', type_='foreignkey')
    op.drop_constraint(None, 'patient_attachments', type_='foreignkey')
    op.create_foreign_key(op.f('patient_attachments_doctor_id_fkey'), 'patient_attachments', 'doctors', ['doctor_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_patient_attachments_patient_id'), table_name='patient_attachments')
    op.drop_index(op.f('ix_patient_attachments_organization_id'), table_name='patient_attachments')
    op.drop_index(op.f('ix_patient_attachments_doctor_id'), table_name='patient_attachments')
    op.drop_column('patient_attachments', 'organization_id')

    op.alter_column('doctors', 'updated_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('doctors', 'created_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('doctors', 'clinic_name',
                existing_type=sa.VARCHAR(),
                nullable=True)

    op.drop_constraint(None, 'bills', type_='foreignkey')
    op.drop_constraint(None, 'bills', type_='foreignkey')
    op.drop_constraint(None, 'bills', type_='foreignkey')
    op.create_foreign_key(op.f('bills_patient_id_fkey'), 'bills', 'patients', ['patient_id'], ['id'])
    op.drop_index(op.f('ix_bills_patient_id'), table_name='bills')
    op.drop_index(op.f('ix_bills_organization_id'), table_name='bills')
    op.drop_index(op.f('ix_bills_doctor_id'), table_name='bills')
    op.alter_column('bills', 'updated_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('bills', 'created_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('bills', 'payment_status',
                existing_type=sa.VARCHAR(),
                nullable=True)
    op.alter_column('bills', 'amount',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.alter_column('bills', 'doctor_id',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.alter_column('bills', 'patient_id',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.drop_column('bills', 'organization_id')

    op.add_column('appointments', sa.Column('appointment_date', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.create_foreign_key(op.f('appointments_patient_id_fkey'), 'appointments', 'patients', ['patient_id'], ['id'])
    op.drop_index(op.f('ix_appointments_start_at'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_patient_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_organization_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_end_at'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_doctor_id'), table_name='appointments')
    op.alter_column('appointments', 'updated_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('appointments', 'created_at',
                existing_type=postgresql.TIMESTAMP(timezone=True),
                nullable=True)
    op.alter_column('appointments', 'status',
                existing_type=sa.VARCHAR(),
                nullable=True)
    op.alter_column('appointments', 'doctor_id',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.alter_column('appointments', 'patient_id',
                existing_type=sa.INTEGER(),
                nullable=True)
    op.drop_column('appointments', 'end_at')
    op.drop_column('appointments', 'start_at')
    op.drop_column('appointments', 'organization_id')

    op.drop_index(op.f('ix_user_roles_user_id'), table_name='user_roles')
    op.drop_index(op.f('ix_user_roles_role_id'), table_name='user_roles')
    op.drop_index(op.f('ix_user_roles_organization_id'), table_name='user_roles')
    op.drop_index(op.f('ix_user_roles_id'), table_name='user_roles')
    op.drop_table('user_roles')

    op.drop_index(op.f('ix_role_permissions_role_id'), table_name='role_permissions')
    op.drop_index(op.f('ix_role_permissions_permission_id'), table_name='role_permissions')
    op.drop_index(op.f('ix_role_permissions_id'), table_name='role_permissions')
    op.drop_table('role_permissions')

    op.drop_index(op.f('ix_roles_organization_id'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_index(op.f('ix_roles_code'), table_name='roles')
    op.drop_table('roles')

    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.drop_index(op.f('ix_doctor_profiles_user_id'), table_name='doctor_profiles')
    op.drop_index(op.f('ix_doctor_profiles_organization_id'), table_name='doctor_profiles')
    op.drop_index(op.f('ix_doctor_profiles_id'), table_name='doctor_profiles')
    op.drop_table('doctor_profiles')

    op.drop_index(op.f('ix_audit_logs_organization_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_actor_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
    op.drop_table('permissions')

    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')