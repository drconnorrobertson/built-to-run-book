"""Review a local action log; never changes assignments or source data."""
import argparse
import csv
from datetime import date
import json
import re

FIELDS = ['action_id', 'action', 'owner', 'status', 'due_date', 'closure_evidence']

def iso_date(value):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('expected YYYY-MM-DD')
    return date.fromisoformat(value)

def audit(path, as_of):
    today = iso_date(as_of)
    issues = []
    seen = set()
    count = 0
    with open(path, encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != FIELDS:
            raise ValueError('headers must be exactly: ' + ','.join(FIELDS))
        for number, raw in enumerate(reader, 2):
            count += 1
            if None in raw or any(v is None for v in raw.values()):
                raise ValueError('wrong number of fields at record ' + str(number))
            row = {k: v.strip() for k, v in raw.items()}
            codes = []
            key = row['action_id']
            if not key: codes.append('missing_id')
            elif key in seen: codes.append('duplicate_id')
            seen.add(key)
            if not row['action']: codes.append('missing_action')
            status = row['status']
            if status not in ('open', 'closed', 'cancelled'): codes.append('invalid_status')
            if status == 'open' and not row['owner']: codes.append('missing_owner')
            if status in ('closed', 'cancelled') and not row['closure_evidence']:
                codes.append('missing_closure_evidence')
            due = None
            if row['due_date']:
                try: due = iso_date(row['due_date'])
                except ValueError: codes.append('invalid_due_date')
            elif status == 'open': codes.append('missing_due_date')
            if status == 'open' and due and due < today: codes.append('past_due')
            if codes: issues.append({'record': number, 'action_id': key, 'issues': codes})
    if count == 0: raise ValueError('no data records')
    return {'as_of': as_of, 'records': count, 'flagged_records': len(issues), 'issues': issues}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_file'); p.add_argument('--as-of', required=True)
    args = p.parse_args()
    try: result = audit(args.csv_file, args.as_of)
    except (ValueError, OSError, csv.Error) as error: p.exit(2, 'Input error: ' + str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == '__main__': main()
