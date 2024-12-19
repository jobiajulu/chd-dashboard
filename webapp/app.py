from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Hospital, MortalityData
import pandas as pd

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///hospitals.db')
Session = sessionmaker(bind=engine)

def parse_stat_category(category):
    """Convert category to database format"""
    if category == 'Overall':
        return category
    return f"STAT Mortality Category {category.split()[-1]}"

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/hospitals')
def get_hospitals():
    """Get list of all hospitals with their mortality data"""
    category = request.args.get('category', 'Overall')
    category = parse_stat_category(category)
    
    session = Session()
    query = session.query(
        Hospital,
        MortalityData
    ).join(
        MortalityData
    ).filter(
        MortalityData.category == category
    )
    
    results = query.all()
    hospitals_data = [{
        'id': hospital.id,
        'name': hospital.name,
        'total_cases': mortality.total_cases,
        'mortalities': mortality.mortalities,
        'observed_mortality_rate': round(mortality.observed_mortality_rate, 2),
        'expected_mortality_rate': round(mortality.expected_mortality_rate, 2),
        'oe_ratio': round(mortality.oe_ratio, 2),
        'ci': f"({mortality.oe_ratio_lower:.2f}, {mortality.oe_ratio_upper:.2f})"
    } for hospital, mortality in results]
    
    return jsonify(hospitals_data)

@app.route('/api/hospitals/list')
def get_hospitals_list():
    """Get list of all hospitals for autocomplete"""
    session = Session()
    hospitals = session.query(Hospital).all()
    return jsonify([{
        'id': h.id,
        'name': h.name
    } for h in hospitals])

@app.route('/api/compare')
def compare_hospitals():
    """Compare two hospitals"""
    hospital1_id = request.args.get('hospital1', type=int)
    hospital2_id = request.args.get('hospital2', type=int)
    category = request.args.get('category', 'Overall')
    category = parse_stat_category(category)
    
    if not hospital1_id or not hospital2_id:
        return jsonify({'error': 'Both hospitals must be specified'}), 400
    
    session = Session()
    
    def get_hospital_data(hospital_id):
        hospital = session.query(Hospital).get(hospital_id)
        mortality = session.query(MortalityData).filter_by(
            hospital_id=hospital_id,
            category=category
        ).first()
        
        if not hospital or not mortality:
            return None
            
        return {
            'name': hospital.name,
            'total_cases': mortality.total_cases,
            'mortalities': mortality.mortalities,
            'observed_mortality_rate': round(mortality.observed_mortality_rate, 2),
            'expected_mortality_rate': round(mortality.expected_mortality_rate, 2),
            'oe_ratio': round(mortality.oe_ratio, 2),
            'ci': f"({mortality.oe_ratio_lower:.2f}, {mortality.oe_ratio_upper:.2f})"
        }
    
    hospital1_data = get_hospital_data(hospital1_id)
    hospital2_data = get_hospital_data(hospital2_id)
    
    if not hospital1_data or not hospital2_data:
        return jsonify({'error': 'Hospital data not found'}), 404
    
    return jsonify({
        'hospital1': hospital1_data,
        'hospital2': hospital2_data
    })

@app.route('/api/visualization')
def get_visualization_data():
    """Get data for visualizations"""
    plot_type = request.args.get('type', 'single')
    metric1 = request.args.get('metric1', 'observed_mortality')
    metric2 = request.args.get('metric2', 'expected_mortality')
    category = request.args.get('category', 'Overall')
    category = parse_stat_category(category)
    
    # Get selected hospitals if any
    hospital_ids = request.args.getlist('hospitals[]', type=int)
    
    session = Session()
    query = session.query(
        Hospital,
        MortalityData
    ).join(
        MortalityData
    ).filter(
        MortalityData.category == category
    )
    
    # Filter by selected hospitals if specified
    if hospital_ids:
        query = query.filter(Hospital.id.in_(hospital_ids))
    
    results = query.all()
    
    # Map API parameter names to database column names
    metric_mapping = {
        'observed_mortality': 'observed_mortality_rate',
        'expected_mortality': 'expected_mortality_rate',
        'oe_ratio': 'oe_ratio',
        'total_cases': 'total_cases'
    }
    
    visualization_data = [{
        'name': hospital.name,
        'observed_mortality': round(mortality.observed_mortality_rate, 2),
        'expected_mortality': round(mortality.expected_mortality_rate, 2),
        'oe_ratio': round(mortality.oe_ratio, 2),
        'total_cases': mortality.total_cases
    } for hospital, mortality in results]
    
    return jsonify(visualization_data)

if __name__ == '__main__':
    app.run(debug=True)
