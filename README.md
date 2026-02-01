# Calendar

A small CLI to extract a course schedule from a PDF, normalize it to CSV, and upload per-course calendars to Google Calendar.

## Quickstart

1. Create and activate a virtual environment (recommended):

	```bash
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	```

2. Place your Google OAuth credentials at `credentials.json` (not checked into the repo).

3. Run the CLI via the `calendar` wrapper or directly:

	```bash
	# show help
	calendar -h

	# audit the CSV
	calendar audit --csv google_s4_fixed.csv

	# extract from PDF (delegates to `final_extractor.py`)
	calendar extract --pdf "Emploi du temps 2AS4 Cr-TD SP 2025-2026.pdf"

	# sync missing calendars (safe, retries on quota)
	calendar sync --csv google_s4_fixed.csv --pause 300
	```

## Files / Layout

- `bin/calendar` - executable wrapper to run the CLI.
- `src/gcal_cli.py` - main consolidated CLI implementation.
- `src/final_extractor.py` - timetable PDF extractor (produces `optimized_schedule.csv`).
- `data/` - canonical CSV files and produced CSVs.
- `artifacts/` - archived logs and intermediate files (ignored by git).

## Credentials & Safety

- Do NOT commit `credentials.json` or `token.json`. They are ignored by `.gitignore` and moved to `artifacts/` during cleanup.
- If Google API quota errors occur, use `calendar sync` with longer `--pause` values or retry later.

## Contributing

Open an issue or submit a PR. For quick tasks I can help prepare branches or CI.

---
Commit notes: improved README with usage and layout.
