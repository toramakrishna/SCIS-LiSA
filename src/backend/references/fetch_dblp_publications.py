"""
DBLP Publication Fetcher
Downloads .bib files for each faculty member from DBLP API
"""
import requests
import json
import os
import time
from typing import List, Dict, Optional
from pathlib import Path


def load_matched_faculty(json_path: str) -> List[Dict]:
    """
    Load matched faculty data from JSON file
    
    Args:
        json_path: Path to matched faculty JSON file
        
    Returns:
        List of matched faculty dictionaries
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def sanitize_pid_for_filename(pid: str) -> str:
    """
    Replace '/' in PID with '_' for use in filenames
    
    Args:
        pid: DBLP PID
        
    Returns:
        Sanitized PID safe for filenames
    """
    return pid.replace('/', '_')


def fetch_dblp_bib(pid: str, max_retries: int = 3) -> Optional[str]:
    """
    Fetch BibTeX data for a given DBLP PID with retry logic
    
    Args:
        pid: DBLP PID
        max_retries: Maximum number of retry attempts
        
    Returns:
        BibTeX content as string, or None if fetch failed
    """
    url = f"https://dblp.org/pid/{pid}.bib"
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = 5 * (attempt + 1)  # Exponential backoff
                print(f"  ⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print(f"  ⚠ Rate limited (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                else:
                    print(f"  ✗ Failed after {max_retries} attempts")
                    return None
            else:
                print(f"  ✗ Failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ✗ Error fetching data: {e}")
            if attempt < max_retries - 1:
                continue
            return None
    
    return None


def save_bib_file(pid: str, bib_content: str, output_dir: str, suffix: str = "") -> bool:
    """
    Save BibTeX content to a file
    
    Args:
        pid: DBLP PID
        bib_content: BibTeX content
        output_dir: Directory to save the file
        suffix: Optional suffix to add to filename (e.g., "_1", "_2" for multiple PIDs)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Sanitize PID for filename
        safe_pid = sanitize_pid_for_filename(pid)
        filename = f"{safe_pid}{suffix}.bib"
        filepath = os.path.join(output_dir, filename)
        
        # Save the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        
        print(f"  ✓ Saved to: {filename}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error saving file: {e}")
        return False


def fetch_all_publications(matched_faculty: List[Dict], output_dir: str, 
                          delay: float = 1.0) -> Dict[str, int]:
    """
    Fetch publications for all matched faculty members
    
    Args:
        matched_faculty: List of matched faculty dictionaries
        output_dir: Directory to save .bib files
        delay: Delay between requests in seconds (to be polite to DBLP)
        
    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_faculty': 0,
        'matched_faculty': 0,
        'successful_downloads': 0,
        'failed_downloads': 0,
        'unmatched_faculty': 0,
        'total_pids_fetched': 0
    }
    
    stats['total_faculty'] = len(matched_faculty)
    
    print(f"\n{'='*80}")
    print(f"FETCHING DBLP PUBLICATIONS")
    print(f"{'='*80}\n")
    
    for i, faculty in enumerate(matched_faculty, 1):
        faculty_name = faculty['faculty_name']
        dblp_matched = faculty['dblp_matched']
        
        print(f"{i}. {faculty_name}")
        
        if not dblp_matched:
            print(f"  ⊘ No DBLP match found - skipping")
            stats['unmatched_faculty'] += 1
            continue
        
        stats['matched_faculty'] += 1
        
        # Get all matches (primary + alternatives)
        all_matches = faculty.get('all_matches', [])
        
        # If no all_matches, use the primary dblp_pid
        if not all_matches:
            dblp_pid = faculty.get('dblp_pid')
            dblp_name = faculty.get('dblp_name')
            if dblp_pid:
                all_matches = [{'dblp_pid': dblp_pid, 'dblp_name': dblp_name}]
        
        # Process each PID for this faculty
        for idx, match in enumerate(all_matches, 1):
            dblp_pid = match.get('dblp_pid')
            dblp_name = match.get('dblp_name', 'Unknown')
            
            if not dblp_pid:
                continue
            
            # Add suffix if multiple PIDs
            suffix = f"_{idx}" if len(all_matches) > 1 else ""
            
            print(f"  [{idx}/{len(all_matches)}] DBLP: {dblp_name} (PID: {dblp_pid})")
            
            # Fetch BibTeX data
            bib_content = fetch_dblp_bib(dblp_pid)
            
            if bib_content:
                # Save to file
                if save_bib_file(dblp_pid, bib_content, output_dir, suffix):
                    stats['successful_downloads'] += 1
                    stats['total_pids_fetched'] += 1
                else:
                    stats['failed_downloads'] += 1
            else:
                stats['failed_downloads'] += 1
            
            # Be polite - add delay between requests
            time.sleep(delay)
        
        print()  # Empty line between faculty members
    
    return stats


def print_statistics(stats: Dict[str, int]):
    """
    Print fetch statistics
    
    Args:
        stats: Statistics dictionary
    """
    print(f"\n{'='*80}")
    print(f"FETCH STATISTICS")
    print(f"{'='*80}")
    print(f"Total Faculty Members: {stats['total_faculty']}")
    print(f"Matched with DBLP: {stats['matched_faculty']}")
    print(f"Unmatched: {stats['unmatched_faculty']}")
    print(f"Successful Downloads: {stats['successful_downloads']}")
    print(f"Failed Downloads: {stats['failed_downloads']}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Get file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    matched_faculty_json = os.path.join(current_dir, 'dblp', 'faculty_dblp_matched.json')
    output_dir = os.path.join(project_root, 'dataset', 'dblp')
    
    # Load matched faculty data
    print("Loading matched faculty data...")
    matched_faculty = load_matched_faculty(matched_faculty_json)
    
    # Fetch all publications
    stats = fetch_all_publications(matched_faculty, output_dir, delay=2.5)
    
    # Print statistics
    print_statistics(stats)
    
    print(f"BibTeX files saved to: {output_dir}")
