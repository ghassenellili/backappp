from models import db, Site, SiteSection, User
from datetime import datetime

_initialized = False

def init_demo_data():
    global _initialized
    if _initialized:
        return
        
    try:
        # Check if test user already exists
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(
                email='test@example.com',
                password_hash='test123',
                name='Test User'
            )
            db.session.add(test_user)
            db.session.flush()
        
        # Clear existing sites and sections for this user
        Site.query.filter_by(user_id=test_user.id).delete()
        db.session.commit()
        
        # Create sites
        sites = [
            Site(name='Site A', status='En fonctionnement', user_id=test_user.id),
            Site(name='Site B', status='En maintenance', user_id=test_user.id),
            Site(name='Site C', status='En fonctionnement', user_id=test_user.id)
        ]
        
        for site in sites:
            db.session.add(site)
        
        db.session.flush()  # Get the site IDs before committing
        
        # Create sections for each site
        for site in sites:
            for i in range(1, 3):
                section_name = f"{chr(64 + site.id)}{i}"
                section = SiteSection(
                    site_id=site.id,
                    section_name=section_name,
                    status='En marche',
                    temperature='24.0°C',
                    ph_level='7.0',
                    oxygen_level='6.0 mg/L'
                )
                db.session.add(section)
        
        db.session.commit()
        _initialized = True
        print("Données de démonstration initialisées avec succès")
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'initialisation des données: {e}")
        raise  # Re-raise the exception for debugging
