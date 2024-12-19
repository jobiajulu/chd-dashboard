import json
from pathlib import Path
from datetime import datetime
from database.models import init_db, Hospital, MortalityData
from sqlalchemy.orm import sessionmaker

def load_latest_data():
    """Load the most recent data file into the database"""
    # Find the latest data file
    data_dir = Path(__file__).parent.parent / "data"
    data_files = list(data_dir.glob("hospitals_data_*.json"))
    if not data_files:
        raise FileNotFoundError("No data files found")
    
    latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
    print(f"Loading data from {latest_file}")
    
    # Initialize database
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Clear existing data
    session.query(MortalityData).delete()
    session.query(Hospital).delete()
    
    # Load new data
    with open(latest_file) as f:
        data = json.load(f)
    
    hospitals_added = 0
    for hospital_data in data['hospitals']:
        if not hospital_data.get('mortality_data'):
            continue
            
        hospital = Hospital(
            name=hospital_data['hospital_name'],
            url_id=hospital_data['url'].split('/')[-1],
            last_updated=datetime.fromisoformat(hospital_data['scraped_at'])
        )
        session.add(hospital)
        session.flush()  # Get the hospital ID
        
        # There should be only one mortality table per hospital
        mortality_table = hospital_data['mortality_data'][0]
        
        # Process each row
        for row in mortality_table['rows']:
            # Extract category (first column)
            category = row[0]
            
            # Extract mortalities and total cases (second column)
            cases_str = row[1].strip()
            mortalities, total = map(int, cases_str.split('/'))
            
            # Extract observed and expected rates (third and fourth columns)
            observed_rate = float(row[2].rstrip('%'))
            expected_rate = float(row[3].rstrip('%'))
            
            # Extract O/E ratio and CI (fifth column)
            oe_str = row[4]
            oe_ratio = float(oe_str.split()[0])
            ci_parts = oe_str.split('(')[1].rstrip(')').split(',')
            oe_lower, oe_upper = map(float, ci_parts)
            
            mortality_data = MortalityData(
                hospital_id=hospital.id,
                category=category,
                total_cases=total,
                mortalities=mortalities,
                observed_mortality_rate=observed_rate,
                expected_mortality_rate=expected_rate,
                oe_ratio=oe_ratio,
                oe_ratio_lower=oe_lower,
                oe_ratio_upper=oe_upper
            )
            session.add(mortality_data)
        
        hospitals_added += 1
    
    session.commit()
    print(f"Successfully loaded {hospitals_added} hospitals into database")

if __name__ == '__main__':
    load_latest_data()
