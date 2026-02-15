#!/usr/bin/env python3
import time
import importlib.util
from pathlib import Path

LOG = Path('logs/aggressive_prune.txt')

# Load gcal_cli as a module without executing main
spec = importlib.util.spec_from_file_location('gcal_cli_mod', Path('src/gcal_cli.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

service = mod.get_service()
if not service:
    print('Failed to get Google service. Aborting.')
    raise SystemExit(1)

protected = ['tasks', 'task', 'birthday', 'birthdays', 'birth', 'none', 'primary', '@', 'holiday']

out = []
page_token = None
while True:
    resp = service.calendarList().list(pageToken=page_token).execute()
    for c in resp.get('items', []):
        name = c.get('summary','')
        lname = name.lower()
        cid = c.get('id')
        keep = False
        for p in protected:
            if p in lname:
                keep = True
                break
        if keep:
            out.append(f'SKIP: {name} ({cid})')
            continue
        try:
            service.calendars().delete(calendarId=cid).execute()
            out.append(f'DELETED: {name} ({cid})')
            time.sleep(0.2)
        except Exception as e:
            out.append(f'ERROR: {name} ({cid}) -> {e}')
    page_token = resp.get('nextPageToken')
    if not page_token:
        break

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text('\n'.join(out) + '\n')
print('Done. Wrote log to', LOG)
for l in out:
    print(l)
