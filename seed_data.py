from app import create_app
from models import db, User, Site, SiteSection, SensorReading
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    # Vider les tables existantes
    db.session.query(SensorReading).delete()
    db.session.query(SiteSection).delete()
    db.session.query(Site).delete()
    db.session.query(User).delete()
    
    # Créer un utilisateur test
    user = User(email='test@example.com', password_hash='firebase_auth')
    db.session.add(user)
    db.session.flush()
    
    # Créer des sites
    site_names = ['Site A', 'Site B', 'Site C']
    site_statuses = ['En fonctionnement', 'En maintenance', 'En fonctionnement']
    
    sites = []
    for i in range(3):
        site = Site(
            name=site_names[i],
            status=site_statuses[i],
            last_update=datetime.now() - timedelta(hours=i*8),
            user_id=user.id
        )
        sites.append(site)
        db.session.add(site)
    
    db.session.flush()
    
    # Créer des sections pour chaque site
    for i, site in enumerate(sites):
        for j in range(1, 3):
            section_name = f'{"ABC"[i]}{j}'
            is_active = not (i == 1 and j == 2)  # Site B, section 2 inactive
            
            section = SiteSection(
                section_name=section_name,
                status='En marche' if is_active else 'En maintenance',
                volume=f'{random.randint(300, 600)} L',
                temperature=f'{20 + random.random() * 8:.1f}°C',
                ph_level=f'{6.5 + random.random() * 1:.1f}',
                oxygen_level=f'{5 + random.random() * 3:.1f} mg/L',
                is_active=is_active,
                site_id=site.id
            )
            db.session.add(section)
            db.session.flush()
            
            # Ajouter des lectures de capteurs pour cette section
            for k in range(7):  # 7 jours de données
                for reading_type in ['temperature', 'ph', 'oxygen']:
                    base_values = {'temperature': 24, 'ph': 7.0, 'oxygen': 6.2}
                    variation = {'temperature': 3, 'ph': 0.5, 'oxygen': 1.0}
                    
                    value = base_values[reading_type] + (random.random() - 0.5) * variation[reading_type]
                    
                    reading = SensorReading(
                        reading_type=reading_type,
                        value=round(value, 2),
                        timestamp=datetime.now() - timedelta(days=6-k),
                        section_id=section.id
                    )
                    db.session.add(reading)
    
    db.session.commit()
    print("Données de test ajoutées avec succès")