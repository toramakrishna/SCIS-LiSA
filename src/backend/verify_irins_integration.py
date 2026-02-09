#!/usr/bin/env python3
"""
Verify IRINS and Scopus data integration in the database
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db_models import Author
from config.db_config import SessionLocal
from services.ingestion_service import DatabaseIngestionService
import json

def check_faculty_mapping():
    """Check if faculty mapping loads IRINS fields"""
    print("="*80)
    print("TEST 1: Faculty Mapping Load")
    print("="*80)
    
    db = SessionLocal()
    try:
        service = DatabaseIngestionService(db)
        faculty_mapping = service.load_faculty_mapping('references/faculty_data.json')
        
        # Get first faculty from mapping
        if faculty_mapping['by_pid']:
            sample_pid = list(faculty_mapping['by_pid'].keys())[0]
            sample_faculty = faculty_mapping['by_pid'][sample_pid]
            
            print(f"\nSample Faculty PID: {sample_pid}")
            print(f"Faculty Name: {sample_faculty.get('faculty_name')}")
            print(f"\nIRINS Fields:")
            print(f"  irins_profile: {sample_faculty.get('irins_profile')}")
            print(f"  irins_url: {sample_faculty.get('irins_url')}")
            print(f"  irins_photo_url: {sample_faculty.get('irins_photo_url')}")
            print(f"  photo_path: {sample_faculty.get('photo_path')}")
            print(f"\nScopus Fields:")
            print(f"  scopus_author_id: {sample_faculty.get('scopus_author_id')}")
            print(f"  scopus_url: {sample_faculty.get('scopus_url')}")
            print(f"  h_index: {sample_faculty.get('h_index')}")
            
            # Check if fields are present
            required_fields = ['irins_profile', 'irins_url', 'scopus_author_id', 'h_index']
            has_fields = any(sample_faculty.get(field) for field in required_fields)
            
            if has_fields:
                print("\n✅ PASS: Faculty mapping contains IRINS/Scopus fields")
                return True
            else:
                print("\n❌ FAIL: Faculty mapping missing IRINS/Scopus fields")
                return False
        else:
            print("❌ FAIL: No faculty found in mapping")
            return False
            
    finally:
        db.close()

def check_database_records():
    """Check if database has IRINS fields populated"""
    print("\n" + "="*80)
    print("TEST 2: Database Records")
    print("="*80)
    
    db = SessionLocal()
    try:
        # Get faculty with IRINS data
        faculty_with_irins = db.query(Author).filter(
            Author.is_faculty == True,
            Author.irins_profile.isnot(None)
        ).all()
        
        total_faculty = db.query(Author).filter(Author.is_faculty == True).count()
        
        print(f"\nTotal Faculty: {total_faculty}")
        print(f"Faculty with IRINS data: {len(faculty_with_irins)}")
        
        if faculty_with_irins:
            sample = faculty_with_irins[0]
            print(f"\nSample Faculty: {sample.name}")
            print(f"  IRINS Profile: {sample.irins_profile}")
            print(f"  IRINS URL: {sample.irins_url}")
            print(f"  Photo Path: {sample.photo_path}")
            print(f"  Scopus ID: {sample.scopus_author_id}")
            print(f"  H-Index: {sample.h_index}")
            
            print(f"\n✅ PASS: {len(faculty_with_irins)}/{total_faculty} faculty have IRINS data")
            return True
        else:
            print("\n⚠️  WARNING: No faculty with IRINS data found in database")
            print("   This is expected if data hasn't been ingested yet.")
            print("   Run ingestion from Admin page or migration script.")
            return False
            
    finally:
        db.close()

def check_json_source():
    """Check faculty_data.json has IRINS fields"""
    print("\n" + "="*80)
    print("TEST 3: Source JSON File")
    print("="*80)
    
    try:
        with open('references/faculty_data.json', 'r') as f:
            faculty_data = json.load(f)
        
        # Count faculty with IRINS data
        with_irins = sum(1 for f in faculty_data if f.get('irins_profile'))
        with_scopus = sum(1 for f in faculty_data if f.get('scopus_author_id'))
        
        print(f"\nTotal Faculty in JSON: {len(faculty_data)}")
        print(f"Faculty with IRINS data: {with_irins}")
        print(f"Faculty with Scopus data: {with_scopus}")
        
        if with_irins > 0:
            # Show sample
            sample = next(f for f in faculty_data if f.get('irins_profile'))
            print(f"\nSample Faculty: {sample['name']}")
            print(f"  IRINS Profile: {sample.get('irins_profile')}")
            print(f"  IRINS URL: {sample.get('irins_url')}")
            print(f"  Photo Path: {sample.get('photo_path')}")
            print(f"  Scopus ID: {sample.get('scopus_author_id')}")
            print(f"  H-Index: {sample.get('h_index')}")
            
            print(f"\n✅ PASS: JSON source contains IRINS/Scopus data")
            return True
        else:
            print("\n❌ FAIL: JSON source missing IRINS data")
            return False
            
    except FileNotFoundError:
        print("\n❌ FAIL: faculty_data.json not found")
        return False

def main():
    """Run all verification tests"""
    print("\n" + "="*80)
    print("IRINS & SCOPUS DATA INTEGRATION VERIFICATION")
    print("="*80)
    
    results = []
    
    # Test 1: Check JSON source
    results.append(("JSON Source", check_json_source()))
    
    # Test 2: Check faculty mapping load
    results.append(("Faculty Mapping", check_faculty_mapping()))
    
    # Test 3: Check database records
    results.append(("Database Records", check_database_records()))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed! IRINS integration is working correctly.")
        print("\nNext steps:")
        print("  1. If database records test showed no IRINS data, run ingestion from Admin page")
        print("  2. Or run migration: python3 migrations/add_irins_profile_fields.py")
        print("  3. Verify frontend at http://localhost:5173/faculty")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        if not results[2][1]:  # Database test failed
            print("\nTo populate database with IRINS data, run:")
            print("  python3 migrations/add_irins_profile_fields.py")
    
    print("\n" + "="*80)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
