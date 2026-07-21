import subprocess, sys
from pathlib import Path
base=Path(__file__).resolve().parent
scripts=[
 'clean_project_master.py',
 'clean_area_fields.py',
 'backfill_master_dates_and_names.py',
 'clean_planning_legal_fields.py',
 'clean_financial_fields.py',
 'audit_clean_master.py',
 'build_web_projects_data.py',
]
for s in scripts:
    print(f'==> {s}')
    subprocess.check_call([sys.executable,'-X','utf8',str(base/s)],cwd=str(base.parent.parent))
print('Clean pipeline complete')
