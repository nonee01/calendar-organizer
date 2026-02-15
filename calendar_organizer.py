#!/usr/bin/env python3
"""Enhanced Calendar Organizer - Add colors, sort, validate, and organize calendar CSV files

Features:
- Add color tags based on course names
- Sort by color with customizable order
- Validate dates, times, and week ranges
- Generate statistics and reports
- Split by color into separate files
- Backup original files
- Export to multiple formats
"""

import csv
import argparse
import sys
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Course name to color mapping (Google Calendar colors)
COLOR_MAP = {
    'Algèbre 2': 'Blueberry',
    'Algébre 2': 'Blueberry',  # Handle typo
    'Analyse 4': 'Tomato',
    'Electromagnétisme': 'Peacock',
    'Électromagnétisme': 'Peacock',  # Handle accents
    'Méthodes numérique': 'Grape',
    'Méthodes Numériques': 'Grape',
    'Elément de mach': 'Sage',
    'Éléments de Machines': 'Sage',
    'Optique': 'Lavender',
    'développement personnel': 'Banana',
    'Développement Personnel': 'Banana',
    'Progr avancée': 'Flamingo',
    'Programmation Avancée': 'Flamingo',
    'English for International': 'Tangerine',
    "Techniques d'écriture": 'Citron',
    "Savoir être": 'Basil',
}

# Google Calendar color order
COLOR_ORDER = [
    'Tomato', 'Flamingo', 'Tangerine', 'Banana', 
    'Sage', 'Basil', 'Peacock', 'Blueberry', 
    'Lavender', 'Grape', 'Graphite', 'Citron'
]

# Expected week labels for validation
EXPECTED_WEEKS = [
    'S14', 'S15', 'S16', 'S17', 'S18', 'S19', 
    'S20', 'S21', 'S22', 'S23', 'S24', 'S25', 'S26'
]

# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

class Color:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def ok(msg): print(f"{Color.GREEN}✓{Color.END} {msg}")
def warn(msg): print(f"{Color.YELLOW}⚠{Color.END} {msg}")
def err(msg): print(f"{Color.RED}✗{Color.END} {msg}")
def info(msg): print(f"{Color.CYAN}ℹ{Color.END} {msg}")
def header(msg): print(f"\n{Color.BOLD}{Color.HEADER}{'═'*60}{Color.END}\n{Color.BOLD}{msg}{Color.END}\n{Color.HEADER}{'═'*60}{Color.END}")

def get_color(subject: str) -> str:
    """Extract color from subject line"""
    subject_lower = subject.lower()
    for key, color in COLOR_MAP.items():
        if key.lower() in subject_lower:
            return color
    return 'Graphite'  # Default

def parse_date(date_str: str) -> datetime | None:
    """Parse date string in MM/DD/YYYY format"""
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except:
        return None

def parse_time(time_str: str) -> datetime | None:
    """Parse time string in 12-hour format"""
    try:
        return datetime.strptime(time_str, '%I:%M %p')
    except:
        return None

def extract_week(description: str) -> str | None:
    """Extract week label from description (e.g., 'Section 6 - Week 14' -> 'S14')"""
    import re
    match = re.search(r'Week (\d+)', description)
    if match:
        return f"S{match.group(1)}"
    return None

def normalize_professor(subject: str) -> str:
    """Normalize professor name in subject"""
    return subject.strip()

# ═══════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_row(row: Dict, row_num: int, issues: List[str]) -> bool:
    """Validate a single row and log issues"""
    valid = True
    
    # Check required fields
    if not row.get('Subject'):
        issues.append(f"Row {row_num}: Missing subject")
        valid = False
    
    # Validate dates
    start_date = parse_date(row.get('Start Date', ''))
    end_date = parse_date(row.get('End Date', ''))
    if not start_date:
        issues.append(f"Row {row_num}: Invalid start date '{row.get('Start Date')}'")
        valid = False
    if not end_date:
        issues.append(f"Row {row_num}: Invalid end date '{row.get('End Date')}'")
        valid = False
    
    # Validate times
    start_time = parse_time(row.get('Start Time', ''))
    end_time = parse_time(row.get('End Time', ''))
    if not start_time and row.get('Start Time'):
        issues.append(f"Row {row_num}: Invalid start time '{row.get('Start Time')}'")
        valid = False
    if not end_time and row.get('End Time'):
        issues.append(f"Row {row_num}: Invalid end time '{row.get('End Time')}'")
        valid = False
    
    # Validate week
    week = extract_week(row.get('Description', ''))
    if week and week not in EXPECTED_WEEKS:
        issues.append(f"Row {row_num}: Unexpected week '{week}' (expected one of {EXPECTED_WEEKS})")
    
    return valid

# ═══════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load_csv(path: Path) -> List[Dict]:
    """Load CSV file and return list of rows"""
    if not path.exists():
        err(f"File not found: {path}")
        return []
    
    rows = []
    try:
        with path.open('r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        ok(f"Loaded {len(rows)} rows from {path.name}")
    except Exception as e:
        err(f"Failed to read {path}: {e}")
        return []
    
    return rows

def save_csv(rows: List[Dict], path: Path, backup: bool = True):
    """Save rows to CSV file with optional backup"""
    if not rows:
        warn("No rows to save")
        return
    
    # Create backup
    if backup and path.exists():
        backup_path = path.with_suffix('.csv.bak')
        shutil.copy2(path, backup_path)
        info(f"Created backup: {backup_path.name}")
    
    # Write CSV
    try:
        fieldnames = list(rows[0].keys())
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        ok(f"Saved {len(rows)} rows to {path.name}")
    except Exception as e:
        err(f"Failed to write {path}: {e}")

def add_colors(rows: List[Dict]) -> List[Dict]:
    """Add Color column to each row"""
    for row in rows:
        if 'Color' not in row or not row['Color']:
            row['Color'] = get_color(row['Subject'])
    return rows

def sort_by_color(rows: List[Dict]) -> List[Dict]:
    """Sort rows by color, then by date/time"""
    def sort_key(r):
        color_idx = COLOR_ORDER.index(r['Color']) if r['Color'] in COLOR_ORDER else 99
        return (color_idx, r.get('Start Date', ''), r.get('Start Time', ''))
    
    return sorted(rows, key=sort_key)

def generate_statistics(rows: List[Dict]) -> Dict:
    """Generate statistics about the calendar data"""
    stats = {
        'total_events': len(rows),
        'by_color': Counter(r['Color'] for r in rows),
        'by_course': Counter(r['Subject'].split(' - ')[0] if ' - ' in r['Subject'] else r['Subject'] for r in rows),
        'by_week': Counter(extract_week(r.get('Description', '')) for r in rows if extract_week(r.get('Description', ''))),
        'date_range': None
    }
    
    # Calculate date range
    dates = [parse_date(r['Start Date']) for r in rows if parse_date(r['Start Date'])]
    if dates:
        stats['date_range'] = (min(dates), max(dates))
    
    return stats

def print_statistics(stats: Dict):
    """Print formatted statistics"""
    header("CALENDAR STATISTICS")
    
    print(f"\n{Color.BOLD}Total Events:{Color.END} {stats['total_events']}")
    
    if stats['date_range']:
        start, end = stats['date_range']
        print(f"{Color.BOLD}Date Range:{Color.END} {start.strftime('%Y-%m-%d')} -> {end.strftime('%Y-%m-%d')}")
    
    print(f"\n{Color.BOLD}Events by Color:{Color.END}")
    for color in COLOR_ORDER:
        if color in stats['by_color']:
            count = stats['by_color'][color]
            bar = '█' * (count // 2)
            print(f"  {color:<12} {count:3} {bar}")
    
    print(f"\n{Color.BOLD}Events by Week:{Color.END}")
    for week in sorted(stats['by_week'].keys()):
        print(f"  {week}: {stats['by_week'][week]:3} events")
    
    print(f"\n{Color.BOLD}Top 5 Courses:{Color.END}")
    for course, count in stats['by_course'].most_common(5):
        print(f"  {course[:40]:<40} {count:3}")

def split_by_color(rows: List[Dict], output_dir: Path):
    """Split events into separate CSV files by color"""
    output_dir.mkdir(exist_ok=True)
    
    by_color = defaultdict(list)
    for row in rows:
        by_color[row['Color']].append(row)
    
    for color, color_rows in by_color.items():
        output_file = output_dir / f"sec6_{color}.csv"
        save_csv(color_rows, output_file, backup=False)
    
    ok(f"Split into {len(by_color)} files in {output_dir}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Calendar Organizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - add colors and sort
  %(prog)s sec6.csv
  
  # Validate only
  %(prog)s sec6.csv --validate-only
  
  # Split by color into separate files
  %(prog)s sec6.csv --split-by-color output/
  
  # Show statistics
  %(prog)s sec6.csv --stats
        """
    )
    
    parser.add_argument('input', type=Path, help='Input CSV file')
    parser.add_argument('-o', '--output', type=Path, help='Output file (default: <input>_colored.csv)')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, don\'t modify')
    parser.add_argument('--no-backup', action='store_true', help='Don\'t create backup files')
    parser.add_argument('--split-by-color', type=Path, metavar='DIR', help='Split into separate files by color')
    parser.add_argument('--stats', action='store_true', help='Show detailed statistics')
    parser.add_argument('--no-sort', action='store_true', help='Don\'t sort by color')
    
    args = parser.parse_args()
    
    # Set default output
    if not args.output:
        args.output = args.input.with_stem(f"{args.input.stem}_colored")
    
    header(f"CALENDAR ORGANIZER: {args.input.name}")
    
    # Load CSV
    rows = load_csv(args.input)
    if not rows:
        sys.exit(1)
    
    # Validate
    issues = []
    valid_count = 0
    for i, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
        if validate_row(row, i, issues):
            valid_count += 1
    
    if issues:
        warn(f"Found {len(issues)} validation issues:")
        for issue in issues[:10]:
            print(f"  • {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        ok("All rows passed validation")
    
    if args.validate_only:
        info("Validation complete (no files modified)")
        sys.exit(0)
    
    # Add colors
    rows = add_colors(rows)
    ok("Added color tags")
    
    # Sort
    if not args.no_sort:
        rows = sort_by_color(rows)
        ok("Sorted by color and date")
    
    # Generate statistics
    if args.stats:
        stats = generate_statistics(rows)
        print_statistics(stats)
    
    # Save main output
    save_csv(rows, args.output, backup=not args.no_backup)
    
    # Split by color if requested
    if args.split_by_color:
        split_by_color(rows, args.split_by_color)
    
    # Summary
    header("COMPLETE")
    ok(f"Processed {len(rows)} events")
    ok(f"Output: {args.output}")
    
    if args.split_by_color:
        info(f"Split files: {args.split_by_color}/")

if __name__ == '__main__':
    main()
