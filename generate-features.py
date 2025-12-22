import sys

features = []
experimental_prefs = []

with open(sys.argv[2]) as f:
    in_pref_list = False
    for line in f.readlines():
        line = line.strip()
        if in_pref_list:
            if line == "];":
                break
            else:
                # format: "pref_name",
                experimental_prefs += [line[1:-2]]
        elif "static EXPERIMENTAL_PREFS" in line:
            in_pref_list = True

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
                'experimental': pref in experimental_prefs,
            }]
            feature = None
        elif ': true,' in line:
            for f in features:
                if f['pref'] in line:
                    f['enabled'] = True
                    break


template = """
# Experimental Web Platform Features

This is a list of web platform features that have a partial implementation in Servo and are gated behind an optional preference.

The following features are enabled by the [experimental rendering mode](https://servo.org/download/#:~:text=Enable%20experimental) or `--enable-experimental-web-platform-features` flag.

| Feature | Tracking issue | Preference |
| ------- | -------------- | ---------- |
{experimental-features}

The following features are disabled by default but can be toggled with a command line flag (e.g. `--pref dom_webgpu_enabled`).

| Feature | Tracking issue | Preference |
| ------- | -------------- | ---------- |
{incomplete-features}

# Enabled web platform features

This is a list of web platform features with an implementation that is complete enough to enable by default.
However, they can still be disabled with an optional preference (e.g. `--pref dom_webgpu_enabled=false`).

| Feature | Tracking issue | Preference |
| ------- | -------------- | ---------- |
{enabled-features}
"""

features = sorted(features, key=lambda feature: feature['name'])
disabled = list(filter(lambda feature: not feature['enabled'], features))
experimental = filter(lambda feature: feature['experimental'], disabled)
incomplete = filter(lambda feature: not feature['experimental'], disabled)
enabled = filter(lambda feature: feature['enabled'], features)

def feature_row(feature):
    cols = [
        f"[{feature['name']}]({feature['mdn']})",
        f"[{feature['issue']}](https://github.com/servo/servo/issues/{feature['issue'][1:]})",
        f"`{feature['pref']}`",
    ]
    return "|" + "|".join(cols) + "|"

experimental_table = "\n".join(map(feature_row, experimental))
incomplete_table = "\n".join(map(feature_row, incomplete))
enabled_table = "\n".join(map(feature_row, enabled))

contents = template.replace('{experimental-features}', experimental_table)
contents = contents.replace('{incomplete-features}', incomplete_table)
contents = contents.replace('{enabled-features}', enabled_table)
print(contents)
