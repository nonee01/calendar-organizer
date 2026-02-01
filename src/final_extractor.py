import pdfplumber
import re
import csv
import json
import sys
from datetime import datetime, timedelta

# Pattern for standard entry: "Subject Name PROFNAME 14-26"
# Improved Week Regex:
# - Matches ranges: 14-26, 8-10 (any digit-digit)
# - Matches single numbers: Only if >= 10 (matches 14, 25, but not 2 or 4)
#   This prevents matching "Algébre 2" or "Analyse 4" as weeks.
# - Allows comma/space separators.
WEEKS_PATTERN = re.compile(
    r'(\s'                                      # Start with whitespace
    r'(?:'                                      # Start Group
       r'(?:\d{1,2}-\d{1,2})'                   # Option A: Range (e.g. 14-26)
       r'|'                                     # OR
       r'(?:[1-9]\d)'                           # Option B: Two digits (10-99). Excludes 0-9.
    r')'                                        # End Group
    r'(?:[\s,]+'                                # Followed by separators + more weeks
       r'(?:'
          r'(?:\d{1,2}-\d{1,2})'
          r'|'
          r'(?:[1-9]\d)'
       r')'
    r')*'                                       # Repeat 0+ times
    r'\b)'                                      # Word boundary
)

def parse_line_entries(line):
    """
    Split a line like:
    'Electromagnétisme KHADIRI 14-26 Progr avancée AHMADI 14-25'
    into structured items.
    """
    # Find all week ranges (anchors)
    matches = list(WEEKS_PATTERN.finditer(line))
    if not matches:
        return []

    entries = []
    last_end = 0
    
    for i, match in enumerate(matches):
        week_str = match.group(1).strip()
        week_end_pos = match.end()
        content_chunk = line[last_end:match.start()].strip()
        
        prof_match = re.search(r'(\b[A-Z]{2,}(?:\s+[A-Z]{2,})*)$', content_chunk)
        
        if prof_match:
            prof = prof_match.group(1)
            subject = content_chunk[:prof_match.start()].strip()
        else:
            prof = "Unknown"
            subject = content_chunk
            
        entries.append({
            'subject': subject,
            'prof': prof,
            'weeks': week_str,
            'original_text': f"{content_chunk} {week_str}"
        })
        last_end = week_end_pos

    return entries

def extract_schedule(pdf_path):
    schedule_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Opened PDF with {len(pdf.pages)} pages")
            
            all_lines_map = {} # page -> lines
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                print(f"--- Processing Page {page_num} ---")
                lines = text.split('\n')
                all_lines_map[page_num] = lines
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            current_day_idx = 0
            
            # Iterate pages
            for pnum in sorted(all_lines_map.keys()):
                lines = all_lines_map[pnum]
                
                # Find indices of Sec6 lines
                sec6_indices = [i for i, ln in enumerate(lines) if 'Sec6' in ln or 'Sec 6' in ln]
                
                print(f"Page {pnum}: Found {len(sec6_indices)} Sec6 anchors at {sec6_indices}")
                
                for idx in sec6_indices:
                    if current_day_idx >= len(days):
                        break
                        
                    day_name = days[current_day_idx]
                    print(f"--> Parsing Block for {day_name} (Anchor L{idx})")
                    
                    line_primary = lines[idx - 1] if idx > 0 else ""
                    line_anchor = lines[idx]
                    line_post = lines[idx + 1] if idx + 1 < len(lines) else ""
                    
                    entries_primary = parse_line_entries(line_primary)
                    
                    clean_anchor = re.sub(r'Sec\s*6', '', line_anchor).strip()
                    entries_anchor = parse_line_entries(clean_anchor)
                    
                    if clean_anchor and not entries_anchor and parse_line_entries(line_post):
                         entries_anchor = parse_line_entries(clean_anchor + " " + line_post)

                    print(f"   Line-1: {entries_primary}")
                    print(f"   Line 0: {entries_anchor}")
                    
                    schedule_data.append({
                        'day': day_name,
                        'entries': entries_primary + entries_anchor
                    })
                    current_day_idx += 1
                    
    except Exception as e:
        print(f"Error reading PDF: {e}")
        import traceback
        traceback.print_exc()
        return []

    return schedule_data

def expand_weeks(weeks_str):
    """
    Parse "14-26", "14-19, 20-25" into a set of integers.
    """
    valid_weeks = set()
    parts = re.split(r'[\s,]+', weeks_str.strip())
    for p in parts:
        if '-' in p:
            try:
                s, e = map(int, p.split('-'))
                valid_weeks.update(range(s, e + 1))
            except: pass
        else:
            try:
                valid_weeks.add(int(p))
            except: pass
    return valid_weeks

def generate_csv(data, output_csv="optimized_schedule.csv"):
    rows = []
    fieldnames = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private']
    
    START_DATE = datetime(2026, 2, 2)
    S14 = 14
    
    days_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5
    }
    
    slots = [
        ("8:30 AM", "10:30 AM"),
        ("10:30 AM", "12:30 PM"),
        ("2:30 PM", "4:30 PM"),
        ("4:30 PM", "6:30 PM")
    ]
    
    for block in data:
        day_str = block['day']
        day_offset = days_map.get(day_str, 0)
        all_entries = block['entries']
        
        for i, entry in enumerate(all_entries):
            slot_idx = i
            
            # Logic for overlays (Tuesday case)
            if day_str == 'Tuesday' and i >= 4:
                slot_idx = i - 2
            
            if day_str == 'Friday':
                if i == 3:
                     slot_idx = 1
            
            if slot_idx >= len(slots):
                continue
                
            start_t, end_t = slots[slot_idx]
            weeks = expand_weeks(entry['weeks'])
            subj = entry['subject']
            prof = entry['prof']
            if prof == 'Unknown': prof = ''
            
            for w in weeks:
                if w < 14 or w > 26: continue
                
                delta_days = (w - S14) * 7 + day_offset
                evt_date = START_DATE + timedelta(days=delta_days)
                date_str = evt_date.strftime('%m/%d/%Y')
                
                full_subj = f"{subj}"
                if prof: full_subj += f" ({prof})"
                full_subj += f" - Sec 6 - S{w}"
                
                desc = f"Week: S{w}\nProfessor: {prof if prof else 'N/A'}"
                
                rows.append({
                    'Subject': full_subj,
                    'Start Date': date_str,
                    'Start Time': start_t,
                    'End Date': date_str,
                    'End Time': end_t,
                    'All Day Event': 'False',
                    'Description': desc,
                    'Location': '',
                    'Private': 'False'
                })

    rows.sort(key=lambda x: (datetime.strptime(x['Start Date'], '%m/%d/%Y'), datetime.strptime(x['Start Time'], '%I:%M %p')))

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {output_csv} with {len(rows)} events.")

def main():
    pdf_path = "Emploi du temps 2AS4 Cr-TD SP 2025-2026.pdf"
    data = extract_schedule(pdf_path)
    
    with open('optimized_extraction.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved structured data to optimized_extraction.json with {len(data)} lines found.")
    generate_csv(data, "optimized_schedule.csv")

if __name__ == "__main__":
    main()
