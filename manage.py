#!/usr/bin/env python3
"""
Management script for the Smart Dispute Canada application.
Provides CLI commands for database initialization and other tasks.
"""
import os
import click

from main import create_app
from utils.db import db
from models.user import User
# Import all models to ensure they are registered with SQLAlchemy
from models.case import Case
from models.evidence import Evidence
from models.court_form import CourtForm, FormField, FormSubmission
from models.legal_journey import LegalJourney, JourneyStep
from models.notification import Notification
from models.payment import Payment

# Secure password generation for production
import secrets
import string

def generate_secure_password(length=16):
    """Generates a secure, random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))

@click.group()
def cli():
    """Management commands for the Smart Dispute application."""
    pass

@click.command(name='init-db')
@click.option('--env', type=click.Choice(['development', 'production']), required=True, help='The environment to initialize the database for.')
def init_db_command(env):
    """Initializes the database with tables and seed data."""
    # Manually create the app and app_context.
    # This is necessary because we are not using the Flask CLI runner.
    app = create_app()
    with app.app_context():
        click.echo(f"Initializing database for {env} environment...")

        # Create all tables based on models
        db.create_all()
        click.echo("✅ Database tables created successfully.")

        if env == 'production':
            # Production: Create only a secure admin user
            admin_user = User.query.filter_by(email='admin@smartdispute.ca').first()
            if not admin_user:
                click.echo("Creating admin user for production...")
                admin_user = User(
                    email='admin@smartdispute.ca',
                    is_admin=True,
                    is_active=True
                )
                admin_password = generate_secure_password()
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                click.echo("✅ Admin user created successfully.")
                click.echo("\n" + "="*50)
                click.echo("🚨 IMPORTANT: SECURE ADMIN PASSWORD GENERATED 🚨")
                click.echo("="*50)
                click.echo("Please save the following admin credentials in a secure location.")
                click.echo("This password will only be displayed once.")
                click.echo(f"  => Email:    admin@smartdispute.ca")
                click.echo(f"  => Password: {admin_password}")
                click.echo("="*50 + "\n")
            else:
                click.echo("ℹ️ Admin user already exists. Password not changed.")

        elif env == 'development':
            # For development, you can add test users or other seed data here.
            # For now, we'll just confirm it's ready for development.
            click.echo("✅ Development database is ready.")

        click.echo(f"\n🎉 Database initialization for {env} complete!")

cli.add_command(init_db_command)

if __name__ == '__main__':
    cli()