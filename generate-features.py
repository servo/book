import sys

features = []

with open(sys.argv[1]) as f:
    feature = None
    for line in f.readlines():
        line = line.strip()
        if line.startswith('// feature:'):
            line = line.removeprefix('// feature:')
            feature = line.split('|')
        elif feature:
            pref = line.split(' ')[1][:-1]
            features += [{
                'name': feature[0].strip(),
                'issue': feature[1].strip(),
                'mdn': 'https://developer.mozilla.org/en-US/docs/' + feature[2].strip(),
                'pref': pref,
                'enabled': False,
            }]
            feature = None
        elif ': true,' in line:
            for f in features:
                if f['pref'] in line:
                    f['enabled'] = True
                    break


template = """
# Incomplete web platform features

This is a list of web platform features that have a partial implementation
in Servo and gated behind an optional preference.

| Feature | Tracking issue | Preference |
| ------- | -------------- | ---------- |
{incomplete-features}

# Enabled web platform features

This is a list of web platform features with an implementation that is complete
enough to enable by default.
However, they can still be disabled with an optional preference.

| Feature | Tracking issue | Preference |
| ------- | -------------- | ---------- |
{enabled-features}
"""

features = sorted(features, key=lambda feature: feature['name'])
incomplete = filter(lambda feature: not feature['enabled'], features)
enabled = filter(lambda feature: feature['enabled'], features)

def feature_row(feature):
    cols = [
        f"[{feature['name']}]({feature['mdn']})",
        f"[{feature['issue']}](https://github.com/servo/servo/issues/{feature['issue'][1:]})",
        f"`{feature['pref']}`",
    ]
    return "|" + "|".join(cols) + "|"

incomplete_table = "\n".join(map(feature_row, incomplete))
enabled_table = "\n".join(map(feature_row, enabled))

contents = template.replace('{incomplete-features}', incomplete_table)
contents = contents.replace('{enabled-features}', enabled_table)
print(contents)
