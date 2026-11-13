#!/bin/sh
# Rebuild ../PHYSICS.md from PHYSICS.tmpl.md and the tables of report.py
cd "$(dirname "$0")" && python3 report.py > /tmp/physics_tables.md && python3 - <<'PY'
import re
T = open('/tmp/physics_tables.md').read()
secs = {m.group(1): m.group(2).strip() for m in re.finditer(r'<!-- (\w+) -->\n(.*?)(?=\n<!-- |\Z)', T, re.S)}
s = open('PHYSICS.tmpl.md').read()
for k, v in secs.items():
    s = s.replace('{{%s}}' % k, v)
assert '{{' not in s
open('../PHYSICS.md', 'w').write(s)
PY
