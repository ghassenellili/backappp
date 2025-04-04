from flask import Blueprint, request, jsonify
from models import db, Site, SiteSection, SensorReading, User
from datetime import datetime, timedelta
import random

site_bp = Blueprint('site', __name__)

@site_bp.route('/sites', methods=['GET', 'POST'])
def sites():
    if request.method == 'GET':
        user_email = request.args.get('email')
        if not user_email:
            return jsonify({'error': 'Email requis'}), 400
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
        sites = Site.query.filter_by(user_id=user.id).all()
        return jsonify([{
            'id': site.id,
            'name': site.name,
            'status': site.status,
            'last_update': site.last_update.strftime('%Y-%m-%d %H:%M:%S')
        } for site in sites]), 200
        
    elif request.method == 'POST':
        data = request.json
        user = User.query.filter_by(email=data['user_email']).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
        new_site = Site(
            name=data['name'],
            status=data['status'],
            user_id=user.id
        )
        db.session.add(new_site)
        db.session.commit()
        
        return jsonify({
            'id': new_site.id,
            'name': new_site.name,
            'status': new_site.status
        }), 201

@site_bp.route('/sites/<int:site_id>', methods=['GET'])
def get_site_detail(site_id):
    # Simuler les données d'un site
    site_data = {
        'id': site_id,
        'name': f'Site {"ABC"[site_id-1]}',
        'status': 'En fonctionnement' if site_id != 2 else 'En maintenance',
        'sections': []
    }
    
    # Générer les sections pour ce site
    for i in range(1, 3):
        section_name = f'{"ABC"[site_id-1]}{i}'
        is_active = not (site_id == 2 and i == 2)
        
        section = {
            'section_name': section_name,
            'status': 'En marche' if is_active else 'En maintenance',
            'volume': f'{random.randint(300, 600)} L',
            'temperature': f'{20 + random.random() * 8:.1f}°C',
            'ph_level': f'{6.5 + random.random() * 1:.1f}',
            'oxygen_level': f'{5 + random.random() * 3:.1f} mg/L',
            'is_active': is_active
        }
        
        site_data['sections'].append(section)
    
    return jsonify(site_data), 200

@site_bp.route('/sites/<int:site_id>/sections/<section_name>/readings', methods=['GET'])
def get_section_readings(site_id, section_name):
    # Simuler 7 jours de données pour un graphique
    reading_type = request.args.get('type', 'temperature')
    days = 7
    data = []
    
    base_values = {
        'temperature': 24,
        'ph': 7.0,
        'oxygen': 6.2
    }
    
    variation = {
        'temperature': 3,
        'ph': 0.5,
        'oxygen': 1.0
    }
    
    for i in range(days):
        value = base_values[reading_type] + (random.random() - 0.5) * variation[reading_type]
        data.append({
            'day': i,
            'value': round(value, 2),
            'date': (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        })
    
    return jsonify(data), 200

@site_bp.route('/sites/<int:site_id>/sections/<section_name>/toggle', methods=['POST'])
def toggle_section(site_id, section_name):
    # Simuler l'activation/désactivation d'une section
    action = request.json.get('action', 'toggle')
    
    return jsonify({
        'section_name': section_name,
        'is_active': action == 'start',
        'message': f"Section {section_name} {'démarrée' if action == 'start' else 'arrêtée'} avec succès"
    }), 200

@site_bp.route('/sites/<int:site_id>/sections/<section_name>/readings', methods=['POST'])
def add_sensor_reading(site_id, section_name):
    try:
        data = request.json
        if not data or not all(k in data for k in ['reading_type', 'value']):
            return jsonify({'error': 'Données manquantes'}), 400

        # Vérifier que la section existe
        section = SiteSection.query.filter_by(site_id=site_id, section_name=section_name).first()
        if not section:
            return jsonify({'error': 'Section non trouvée'}), 404

        # Valider le type de lecture
        valid_types = ['temperature', 'ph', 'oxygen']
        if data['reading_type'] not in valid_types:
            return jsonify({'error': 'Type de lecture invalide'}), 400

        # Valider la valeur
        try:
            value = float(data['value'])
            
            # Validation des plages de valeurs
            if data['reading_type'] == 'temperature':
                if not (15 <= value <= 35):
                    return jsonify({'error': 'Température doit être entre 15°C et 35°C'}), 400
            elif data['reading_type'] == 'ph':
                if not (0 <= value <= 14):
                    return jsonify({'error': 'pH doit être entre 0 et 14'}), 400
            elif data['reading_type'] == 'oxygen':
                if not (0 <= value <= 20):
                    return jsonify({'error': 'Oxygène doit être entre 0 et 20 mg/L'}), 400
                    
        except ValueError:
            return jsonify({'error': 'Valeur invalide'}), 400

        # Créer la nouvelle lecture
        new_reading = SensorReading(
            reading_type=data['reading_type'],
            value=value,
            section_id=section.id,
            timestamp=datetime.now()
        )
        
        db.session.add(new_reading)
        db.session.commit()

        # Mettre à jour les valeurs actuelles de la section
        if data['reading_type'] == 'temperature':
            section.temperature = f"{value}°C"
        elif data['reading_type'] == 'ph':
            section.ph_level = str(value)
        elif data['reading_type'] == 'oxygen':
            section.oxygen_level = f"{value} mg/L"
        
        db.session.commit()

        return jsonify({
            'message': 'Lecture enregistrée avec succès',
            'reading': {
                'type': data['reading_type'],
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@site_bp.route('/readings', methods=['POST'])
def add_reading():
    data = request.json
    try:
        section = SiteSection.query.filter_by(
            site_id=data['site_id'],
            section_name=data['section_name']
        ).first()
        
        if not section:
            return jsonify({'error': 'Section non trouvée'}), 404
            
        new_reading = SensorReading(
            section_id=section.id,
            reading_type=data['reading_type'],
            value=float(data['value']),
            timestamp=datetime.now()
        )
        
        db.session.add(new_reading)
        db.session.commit()
        
        return jsonify({
            'id': new_reading.id,
            'value': new_reading.value,
            'timestamp': new_reading.timestamp.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@site_bp.route('/history', methods=['POST'])
def add_history():
    data = request.json
    try:
        section = SiteSection.query.filter_by(
            site_id=data['site_id'],
            section_name=data['section_name']
        ).first()
        
        if not section:
            return jsonify({'error': 'Section non trouvée'}), 404
            
        readings = []
        for value_data in data['values']:
            reading = SensorReading(
                section_id=section.id,
                reading_type=data['reading_type'],
                value=float(value_data['value']),
                timestamp=datetime.fromisoformat(value_data['timestamp'])
            )
            readings.append(reading)
            
        db.session.bulk_save_objects(readings)
        db.session.commit()
        
        return jsonify({'message': 'Données historiques ajoutées avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@site_bp.route('/readings/latest', methods=['GET'])
def get_latest_readings():
    try:
        site_id = request.args.get('site_id', type=int)
        section_name = request.args.get('section_name')
        
        print(f"Received request for site_id: {site_id}, section_name: {section_name}")  # Debug log
        
        if not site_id or not section_name:
            print(f"Missing parameters - site_id: {site_id}, section_name: {section_name}")  # Debug log
            return jsonify({'error': 'site_id and section_name are required'}), 400
            
        # Get the section
        section = SiteSection.query.filter_by(
            site_id=site_id,
            section_name=section_name
        ).first()
        
        if not section:
            print(f"Section not found for site_id: {site_id}, section_name: {section_name}")  # Debug log
            return jsonify({'error': 'Section not found'}), 404
            
        # Get latest readings for each type
        latest_readings = {}
        for reading_type in ['temperature', 'ph', 'oxygen']:
            reading = SensorReading.query.filter_by(
                section_id=section.id,
                reading_type=reading_type
            ).order_by(SensorReading.timestamp.desc()).first()
            
            if reading:
                latest_readings[reading_type] = reading.value
        
        print(f"Found readings: {latest_readings}")  # Debug log
                
        if not latest_readings:
            print("No readings found")  # Debug log
            return jsonify({'error': 'No readings found'}), 404
            
        return jsonify(latest_readings), 200
        
    except Exception as e:
        print(f"Error in get_latest_readings: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@site_bp.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    try:
        # Get the latest readings for section A1 of site 1
        section = SiteSection.query.filter_by(site_id=1, section_name='A1').first()
        
        if not section:
            return jsonify({'error': 'Section not found'}), 404
            
        # Get latest readings for each type
        latest_readings = {}
        for reading_type in ['temperature', 'ph', 'oxygen']:
            reading = SensorReading.query.filter_by(
                section_id=section.id,
                reading_type=reading_type
            ).order_by(SensorReading.timestamp.desc()).first()
            
            if reading:
                latest_readings[reading_type] = reading.value
                
        if not latest_readings:
            return jsonify({'error': 'No readings found'}), 404
            
        return jsonify({
            'temperature': latest_readings.get('temperature', 25.0),
            'ph': latest_readings.get('ph', 7.0),
            'oxygen': latest_readings.get('oxygen', 6.5),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error in get_sensor_data: {str(e)}")
        return jsonify({'error': str(e)}), 500