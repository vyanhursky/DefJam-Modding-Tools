"""Validated, source-only fighter inventory shared by decoder and review UI.

Legacy FIGHTERS/PILOT names remain compatible; no workspace records are migrated.
"""
import json
from pathlib import Path
import re


def validate_catalog(data):
    """Reject ambiguous aliases, identities, routes and unexplained omissions."""
    if not isinstance(data, dict) or set(data) != {'schema', 'entries', 'preview_omissions'} or type(data['schema']) is not int or data['schema'] != 1:
        raise ValueError('Expected fighter catalogue schema 1')
    if not isinstance(data['entries'], list) or not data['entries'] or not isinstance(data['preview_omissions'], list):
        raise ValueError('Expected catalogue entries and omissions')
    aliases, slugs, sources, orders = set(), set(), set(), set()
    for row in data['entries']:
        if not isinstance(row, dict) or set(row) not in ({'alias', 'fighter', 'variant', 'primary', 'preview'}, {'alias', 'fighter', 'variant', 'primary', 'preview_unavailable'}):
            raise ValueError('Expected one preview or an explicit unavailability reason')
        if not isinstance(row['alias'], str) or not re.fullmatch(r'v2ip_\d{3}[a-z]\.xsh', row['alias']) or row['alias'] in aliases:
            raise ValueError('Invalid or duplicate fighter alias')
        aliases.add(row['alias'])
        if any(not isinstance(row[k], str) or not row[k].strip() for k in ('fighter', 'variant')) or type(row['primary']) is not bool:
            raise ValueError('Invalid fighter label or primary flag')
        p = row.get('preview')
        if p is None:
            if not isinstance(row['preview_unavailable'], str) or not row['preview_unavailable'].strip():
                raise ValueError('Missing preview unavailability reason')
            continue
        if not isinstance(p, dict) or not {'slug', 'name', 'resource', 'source_id', 'order'} <= set(p) or set(p) - {'slug', 'name', 'resource', 'source_id', 'order', 'archive'}:
            raise ValueError('Invalid preview fields')
        if not isinstance(p['slug'], str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', p['slug']) or p['slug'] in slugs:
            raise ValueError('Invalid or duplicate preview slug')
        if not isinstance(p['source_id'], str) or not re.fullmatch(r'[a-f0-9]{64}', p['source_id']) or p['source_id'] in sources:
            raise ValueError('Invalid or duplicate preview source ID')
        if not isinstance(p['resource'], str) or p['resource'].lower()+'.xsh' != row['alias'] or not isinstance(p['name'], str) or not p['name'].strip():
            raise ValueError('Preview resource must match its alias')
        if type(p['order']) is not int or p['order'] < 0 or p['order'] in orders:
            raise ValueError('Invalid or duplicate preview order')
        if 'archive' in p and (not isinstance(p['archive'], list) or len(p['archive']) != 2 or any(not isinstance(v, str) or not re.fullmatch(r'assets/[A-Za-z0-9_]+\.viv', v) for v in p['archive'])):
            raise ValueError('Invalid nested archive route')
        slugs.add(p['slug']); sources.add(p['source_id']); orders.add(p['order'])
    if orders != set(range(len(orders))):
        raise ValueError('Preview order must be contiguous')
    seen = set()
    for rule in data['preview_omissions']:
        fields = {'group', 'texture_ref', 'reason', 'limitation'}
        if not isinstance(rule, dict) or not fields <= set(rule) or set(rule) - (fields | {'source_id'}) or any(not isinstance(v, str) or not v.strip() for v in rule.values()):
            raise ValueError('Every preview omission needs a reason and limitation')
        if rule.get('source_id') is not None and rule['source_id'] not in sources:
            raise ValueError('Omission source must identify a preview')
        key = (rule['group'], rule['texture_ref'], rule.get('source_id'))
        if key in seen or any(k[:2] == key[:2] and (k[2] is None or key[2] is None) for k in seen):
            raise ValueError('Ambiguous preview omission')
        seen.add(key)
    return data


CATALOG = validate_catalog(json.loads((Path(__file__).parent/'resources/profiles/fighters.json').read_text(encoding='utf8')))
_previews = sorted((row['preview'] for row in CATALOG['entries'] if 'preview' in row), key=lambda p: p['order'])
FIGHTERS = {p['slug']: (p['name'], p['resource'], p['source_id']) for p in _previews}
PILOT = {r['alias']: (r['fighter'], r['variant'], r['primary']) for r in CATALOG['entries']}
MODEL_ARCHIVES = {p['slug']: tuple(p['archive']) for p in _previews if 'archive' in p}
FIGHTER_NAMES = sorted({row['fighter'] for row in CATALOG['entries']}, key=str.casefold)


def preview_omission(group, textures, source_id):
    return next((r for r in CATALOG['preview_omissions'] if r['group'] == group and textures == {r['texture_ref']} and ('source_id' not in r or r['source_id'] == source_id)), None)
