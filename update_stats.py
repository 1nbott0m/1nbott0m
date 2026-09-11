"""Generate a dependency-free SVG using public GitHub REST API data."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from html import escape

USER = '1nbott0m'
ROOT = Path(__file__).resolve().parent

def get(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-stats'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    with urlopen(Request('https://api.github.com/' + path, headers=headers), timeout=30) as response:
        return json.load(response)

def main():
    user = get(f'users/{USER}')
    repos = []
    page = 1
    while True:
        batch = get(f'users/{USER}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    owned = [r for r in repos if not r['fork']]
    langs = {}
    for repo in owned:
        for lang, count in get(f'repos/{USER}/{repo["name"]}/languages').items():
            langs[lang] = langs.get(lang, 0) + count
    stars = sum(r['stargazers_count'] for r in owned)
    total = sum(langs.values())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="270" viewBox="0 0 1100 270" role="img" aria-labelledby="title desc">',
           '<title id="title">Public GitHub statistics for 1nbott0m</title>',
           '<desc id="desc">Repository, star and follower counts; language percentages by bytes in public non-fork repositories.</desc>',
           '<rect x="1" y="1" width="1098" height="268" rx="16" fill="#0d0d12" stroke="#44313F"/>',
           '<g font-family="Menlo,DejaVu Sans Mono,monospace">']
    def txt(x,y,s,size=16,color='#F1E9EE'):
        svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{escape(str(s))}</text>')
    txt(34,38,'$ github --public',18,'#E8A0BF')
    for x, value, label in [(34,user['public_repos'],'REPOSITORIES'),(205,stars,'STARS'),(354,user['followers'],'FOLLOWERS')]:
        txt(x,106,value,40)
        txt(x,140,label,13,'#ACA0AD')
    svg.append('<path d="M530 65V198" stroke="#44313F"/>')
    txt(563,79,'CODE MIX / BYTES',16,'#E8A0BF')
    top = sorted(langs.items(), key=lambda pair: pair[1], reverse=True)
    shown = top[:3]
    if len(top)>3:
        shown.append(('Other', sum(n for _,n in top[3:])))
    if not total:
        txt(563,118,'No public language data yet.',15,'#ACA0AD')
    for i,(lang,n) in enumerate(shown):
        txt(563,110+26*i,f'{lang}  ' + ('<0.1%' if n/total < .001 else f'{n/total:.1%}'),15)
    txt(34,219,'Public data only. Languages describe code, not proficiency.',13,'#ACA0AD')
    txt(34,246,'UPDATED '+now,12,'#ACA0AD')
    svg.append('</g></svg>')
    out = ROOT/'stats.svg'
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(svg)+'\n')
    print(f'Updated {out}: {len(repos)} repositories, {len(langs)} languages')

if __name__ == '__main__':
    main()
