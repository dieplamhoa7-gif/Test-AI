# Manual 10-Part Processing Protocol

User correction: do NOT treat rule-filtered output as final. The work must be split into 10 equal message blocks. For each block, inspect each message and manually/semantically extract real project data into the database.

Rules:
1. Total source rows split into 10 parts by original order.
2. Process one part at a time.
3. For every message in a part, decide:
   - project record candidate
   - update to existing project
   - comment/reply/no database data
   - ambiguous -> review
4. Extract only source-supported fields:
   - message date/time
   - source_file/chunk_id/sender
   - real project name
   - location/map link
   - area/scale/planning/legal/business notes
   - financial line items with label/value/source
5. Merge only if same project name AND same location/map/source context. If unsure, do not merge.
6. After finishing each part, write part_##_manual_records.json and update manifest status.
7. Only after all 10 parts are done, merge into final database and publish web final.

Current status: restarting from Part 1 manually/semantically per user request.
