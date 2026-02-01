"""
DBLP PID Matcher
Matches faculty names with DBLP author PIDs from dblp_author_details.csv
"""
import csv
import json
import os
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


def load_faculty_data(faculty_json_path: str) -> List[Dict]:
    """
    Load faculty data from JSON file
    
    Args:
        faculty_json_path: Path to faculty JSON file
        
    Returns:
        List of faculty dictionaries
    """
    with open(faculty_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_dblp_authors(csv_path: str) -> List[Dict[str, str]]:
    """
    Load DBLP author data from CSV file
    
    Args:
        csv_path: Path to DBLP CSV file
        
    Returns:
        List of dictionaries with pid and author name
    """
    dblp_authors = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dblp_authors.append({
                'pid': row['@pid'],
                'name': row['text']
            })
    
    return dblp_authors


def normalize_name(name: str) -> str:
    """
    Normalize name for comparison
    Removes titles, extra spaces, and converts to lowercase
    
    Args:
        name: Original name
        
    Returns:
        Normalized name
    """
    # Remove common titles
    titles = ['Dr.', 'Prof.', 'Dr', 'Prof', 'Mr.', 'Ms.', 'Mrs.', 'Mr', 'Ms', 'Mrs']
    normalized = name
    
    for title in titles:
        normalized = normalized.replace(title, '')
    
    # Remove extra spaces and convert to lowercase
    normalized = ' '.join(normalized.split()).strip().lower()
    
    return normalized


def similarity_score(str1: str, str2: str) -> float:
    """
    Calculate similarity score between two strings
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Similarity score between 0 and 1
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def match_faculty_with_dblp(faculty_list: List[Dict], dblp_authors: List[Dict], 
                            threshold: float = 0.7) -> List[Dict]:
    """
    Match faculty members with DBLP authors
    
    Args:
        faculty_list: List of faculty dictionaries
        dblp_authors: List of DBLP author dictionaries
        threshold: Minimum similarity score for matching (0-1)
        
    Returns:
        List of matched faculty with DBLP PIDs
    """
    matched_faculty = []
    
    for faculty in faculty_list:
        faculty_name_normalized = normalize_name(faculty['name'])
        
        best_match = None
        best_score = 0.0
        all_matches = []
        
        # Find all potential matches above threshold
        for dblp_author in dblp_authors:
            dblp_name_normalized = normalize_name(dblp_author['name'])
            score = similarity_score(faculty_name_normalized, dblp_name_normalized)
            
            if score >= threshold:
                all_matches.append({
                    'dblp_name': dblp_author['name'],
                    'dblp_pid': dblp_author['pid'],
                    'score': score
                })
                
                if score > best_score:
                    best_score = score
                    best_match = dblp_author
        
        # Sort matches by score
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        matched_entry = {
            'faculty_name': faculty['name'],
            'designation': faculty['designation'],
            'email': faculty['email'],
            'phone': faculty['phone'],
            'department': faculty['department'],
            'dblp_matched': best_match is not None,
            'match_score': best_score if best_match else 0.0,
            'dblp_pid': best_match['pid'] if best_match else None,
            'dblp_name': best_match['name'] if best_match else None,
            'all_matches': all_matches
        }
        
        matched_faculty.append(matched_entry)
    
    return matched_faculty


def save_matched_data(matched_faculty: List[Dict], output_file: str):
    """
    Save matched faculty data to JSON file
    
    Args:
        matched_faculty: List of matched faculty dictionaries
        output_file: Path to output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(matched_faculty, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved matched data to {output_file}")


def print_match_summary(matched_faculty: List[Dict]):
    """
    Print summary of matching results
    
    Args:
        matched_faculty: List of matched faculty dictionaries
    """
    total = len(matched_faculty)
    matched = sum(1 for f in matched_faculty if f['dblp_matched'])
    unmatched = total - matched
    
    print("\n" + "="*80)
    print("MATCHING SUMMARY")
    print("="*80)
    print(f"Total Faculty Members: {total}")
    print(f"Matched with DBLP: {matched}")
    print(f"Unmatched: {unmatched}")
    print("="*80)
    
    print("\n\nMATCHED FACULTY:")
    print("-"*80)
    for i, faculty in enumerate(matched_faculty, 1):
        if faculty['dblp_matched']:
            print(f"\n{i}. {faculty['faculty_name']}")
            print(f"   DBLP Name: {faculty['dblp_name']}")
            print(f"   DBLP PID: {faculty['dblp_pid']}")
            print(f"   Match Score: {faculty['match_score']:.2f}")
            
            if len(faculty['all_matches']) > 1:
                print(f"   Alternative matches:")
                for alt in faculty['all_matches'][1:4]:  # Show up to 3 alternatives
                    print(f"      - {alt['dblp_name']} (PID: {alt['dblp_pid']}, Score: {alt['score']:.2f})")
    
    if unmatched > 0:
        print("\n\nUNMATCHED FACULTY:")
        print("-"*80)
        for i, faculty in enumerate(matched_faculty, 1):
            if not faculty['dblp_matched']:
                print(f"{i}. {faculty['faculty_name']} ({faculty['designation']})")


if __name__ == "__main__":
    # Get file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    faculty_json = os.path.join(current_dir, 'faculty_data.json')
    dblp_csv = os.path.join(current_dir, 'dblp', 'dblp_author_details.csv')
    output_file = os.path.join(current_dir, 'dblp', 'faculty_dblp_matched.json')
    
    # Load data
    print("Loading faculty data...")
    faculty_list = load_faculty_data(faculty_json)
    
    print("Loading DBLP author data...")
    dblp_authors = load_dblp_authors(dblp_csv)
    print(f"Loaded {len(dblp_authors)} DBLP authors")
    
    # Match faculty with DBLP authors
    print("\nMatching faculty with DBLP authors...")
    matched_faculty = match_faculty_with_dblp(faculty_list, dblp_authors, threshold=0.6)
    
    # Print summary
    print_match_summary(matched_faculty)
    
    # Save results
    save_matched_data(matched_faculty, output_file)
