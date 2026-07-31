import os

dest_file = 'frontend/src/app/components/Dashboard.tsx'
with open(dest_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.strip() == '"use client";' or line.strip() == "'use client';":
        continue
    
    if line.startswith('const DashboardIcon = () => ('):
        skip = True
    elif line.startswith('const GmailIcon = () => ('):
        skip = True
    elif line.startswith('const CheckCircleIcon = () => ('):
        skip = True
    elif line.startswith('const KeyIcon = () => ('):
        skip = True
    elif line.startswith('const UserIcon = () => ('):
        skip = True
    elif line.startswith('const SparklesIcon = () => ('):
        skip = True
    elif line.startswith('const UploadIcon = () => ('):
        skip = True
    elif line.startswith('const CalendarIcon = () => ('):
        skip = True
    elif line.startswith('const GlobeIcon = () => ('):
        skip = True
    elif line.startswith('const LockIcon = () => ('):
        skip = True
    elif line.startswith('const TargetIcon = () => ('):
        skip = True
    elif line.startswith('const ALL_WORLD_COUNTRIES = ['):
        skip = True
    elif line.startswith('const EMPLOYMENT_TYPE_OPTIONS = ['):
        skip = True
    elif line.startswith('const WORK_MODE_OPTIONS = ['):
        skip = True
    elif line.startswith('const SALARY_RANGE_OPTIONS = ['):
        skip = True
    elif line.startswith('const EXPERIENCE_LEVEL_OPTIONS = ['):
        skip = True
    elif line.startswith('const VISA_SPONSORSHIP_OPTIONS = ['):
        skip = True

    if skip:
        if line.strip() == ');' or line.strip() == '];':
            skip = False
        continue

    new_lines.append(line)

new_lines.insert(0, '"use client";\n')

with open(dest_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
