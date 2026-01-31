"""
Clean up faculty_dblp_matched.json by removing score fields
"""
import json
import os


def clean_faculty_data(input_file: str, output_file: str):
    """
    Remove score and match_score fields from faculty data
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
    """
    # Load the data
    with open(input_file, 'r', encoding='utf-8') as f:
        faculty_data = json.load(f)
    
    # Clean each faculty entry
    for faculty in faculty_data:
        # Remove match_score from main entry
        if 'match_score' in faculty:
            del faculty['match_score']
        
        # Remove score from all_matches
        if 'all_matches' in faculty:
            for match in faculty['all_matches']:
                if 'score' in match:
                    del match['score']
    
    # Save cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(faculty_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Cleaned faculty data saved to {output_file}")
    print(f"  Total faculty: {len(faculty_data)}")
    print(f"  Matched: {sum(1 for f in faculty_data if f['dblp_matched'])}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'dblp', 'faculty_dblp_matched.json')
    output_file = os.path.join(current_dir, 'dblp', 'faculty_dblp_matched.json')
    
    clean_faculty_data(input_file, output_file)
