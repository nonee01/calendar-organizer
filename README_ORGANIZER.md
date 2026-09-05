# Calendar Organizer

Enhanced Python tool for managing and organizing Sec6 calendar CSV files with color coding, validation, and Google Calendar integration.

## Features

**Color Management**
- Automatically assigns Google Calendar colors to courses
- Supports 11 distinct colors for better visual organization
- Handles common typos and accent variations

**Statistics & Reporting**
- Shows event distribution by color, week, and course
- Displays date ranges and event counts
- Visual bar charts in terminal

**Validation**
- Validates date and time formats
- Checks for expected week ranges (S14-S26)
- Reports issues with row numbers for easy fixing

**File Operations**
- Automatic backup of existing files
- Sort by color and date
- Split into separate files by color
- UTF-8 encoding support

## Installation

```bash
# Clone or navigate to the Calendar project
cd /home/notadil/Projects/Calendar

# Activate virtual environment
source .venv/bin/activate

# The script is ready to use (no additional dependencies)
```

## Usage

### Basic Usage
Add colors and sort the calendar:
```bash
python3 calendar_organizer.py sec6.csv
```

This creates `sec6_colored.csv` with:
- Color column added
- Sorted by color then date
- Automatic backup of original

### Show Statistics
View detailed statistics about your calendar:
```bash
python3 calendar_organizer.py sec6.csv --stats
```

### Validate Only
Check for issues without modifying files:
```bash
python3 calendar_organizer.py sec6.csv --validate-only
```

### Split by Color
Create separate CSV files for each color:
```bash
python3 calendar_organizer.py sec6.csv --split-by-color output/
```

This creates files like:
- `output/sec6_Tomato.csv`
- `output/sec6_Blueberry.csv`
- etc.

### Custom Output
Specify a custom output filename:
```bash
python3 calendar_organizer.py sec6.csv -o my_calendar.csv
```

### No Backup
Skip creating backup files:
```bash
python3 calendar_organizer.py sec6.csv --no-backup
```

### No Sorting
Add colors but don't reorder rows:
```bash
python3 calendar_organizer.py sec6.csv --no-sort
```

## Color Mapping

| Course | Color | Calendar Display |
|--------|-------|------------------|
| Analyse 4 | Tomato | Red |
| Programmation Avancée | Flamingo | Pink |
| English for International | Tangerine | Orange |
| Développement Personnel | Banana | Yellow |
| Éléments de Machines | Sage | Green |
| Savoir être | Basil | Green |
| Électromagnétisme | Peacock | Blue |
| Algèbre 2 | Blueberry | Blue |
| Optique | Lavender | Purple |
| Méthodes Numériques | Grape | Purple |
| Techniques d'écriture | Citron | Yellow |

## Upload to Google Calendar

After organizing your calendar, upload it:

```bash
# Upload all courses
python3 src/gcal_cli.py upload --csv sec6_colored.csv

# Or use the smart sync
python3 src/gcal_cli.py sync --csv sec6_colored.csv
```

## File Structure

```
Calendar/
├── calendar_organizer.py      # Enhanced organizer tool
├── sec6.csv                    # Original calendar data
├── sec6_colored.csv           # Organized output
├── sec6_colored.csv.bak       # Automatic backup
└── src/
    └── gcal_cli.py            # Google Calendar uploader
```

## Examples

### Example 1: Quick Organization
```bash
# Add colors, sort, and show stats
python3 calendar_organizer.py sec6.csv --stats

# Upload to Google Calendar
python3 src/gcal_cli.py upload --csv sec6_colored.csv
```

### Example 2: Split by Course Color
```bash
# Create separate files for each color
python3 calendar_organizer.py sec6.csv --split-by-color by_color/

# Upload specific color
python3 src/gcal_cli.py upload --csv by_color/sec6_Tomato.csv
```

### Example 3: Validate Before Processing
```bash
# Check for issues first
python3 calendar_organizer.py sec6.csv --validate-only

# If validation passes, process the file
python3 calendar_organizer.py sec6.csv
```

## Validation Checks

The tool validates:
- Date format (MM/DD/YYYY)
- Time format (12-hour with AM/PM)
- Required fields (Subject, dates, times)
- Expected week ranges (S14-S26)
- Reports row numbers for easy fixing

## Tips

1. **Always check validation first** with `--validate-only`
2. **Backups are automatic** - restore with `mv sec6_colored.csv.bak sec6_colored.csv`
3. **Use `--stats`** to verify event distribution
4. **Split by color** for selective uploads to Google Calendar
5. **Color sorting** groups similar courses together for easier viewing

## Troubleshooting

### "Invalid date format"
Ensure dates are in MM/DD/YYYY format (e.g., 02/15/2026)

### "Unexpected week"
Week labels should be S14-S26. Edit the Description field to match.

### "Missing subject"
Every row must have a Subject field filled in.

### Upload fails
Check that you have:
1. Valid `credentials.json` in the project root
2. Run `python3 src/gcal_cli.py list` first to authenticate
3. Internet connection active

## Advanced Usage

### Help
```bash
python3 calendar_organizer.py --help
```

### Combine Multiple Options
```bash
python3 calendar_organizer.py sec6.csv \
  --stats \
  --split-by-color output/ \
  -o organized.csv
```

## Version History

- **v2.0** - Enhanced version with validation, stats, color splitting
- **v1.0** - Basic color assignment and sorting

## License

Part of the Calendar project for Sec6 schedule management.
