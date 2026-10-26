"""Local teaching calculator; no network calls or task-board changes."""
import csv,json,sys
from datetime import datetime

def instant(value):
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.utcoffset() is None: raise ValueError("Explicit offset required")
    return d

def calculate(path,start,end):
    start,end=instant(start),instant(end)
    if end<=start: raise ValueError("End must follow start")
    states={}; opening=set(); counts={"starts":0,"finishes":0,"cancellations":0};previous=None
    with open(path,newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=["timestamp","item","event"]: raise ValueError("Expected timestamp,item,event")
        for row in reader:
            at=instant(row["timestamp"]);item=row["item"].strip();event=row["event"]
            if not item or (previous is not None and at<previous): raise ValueError("Blank item or unsorted events")
            previous=at
            if event=="start":
                if item in states: raise ValueError("Duplicate start or reopening unsupported")
                states[item]="open"
            elif event in ("finish","cancel"):
                if states.get(item)!="open": raise ValueError("Terminal event requires open item")
                states[item]=event
            else: raise ValueError("Unknown event")
            if at<=start:
                if event=="start": opening.add(item)
                else: opening.remove(item)
            if start<at<=end: counts[{"start":"starts","finish":"finishes","cancel":"cancellations"}[event]]+=1
    closing=len(opening)+counts["starts"]-counts["finishes"]-counts["cancellations"]
    return {"opening_wip":len(opening),**counts,"closing_wip":closing,"interval_hours":(end-start).total_seconds()/3600}

if __name__=="__main__":
    if len(sys.argv)!=4: raise SystemExit("Usage: flow_counts.py events.csv START END")
    print(json.dumps(calculate(*sys.argv[1:]),indent=2))
