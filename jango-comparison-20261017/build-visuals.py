"""Present the frozen exploratory results without changing scores or selection."""
import hashlib
import html
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BASE = Path(__file__).resolve().parents[2]
SRC = Path(os.environ.get('DISCOVERY_SOURCE', BASE / 'outputs/strength-discovery-20261017'))
OUT = Path(os.environ.get('DISCOVERY_PRESENTATION', BASE / 'outputs/jango-comparison-20261017'))
OUT.mkdir(parents=True, exist_ok=True)
raw = (SRC / 'results.json').read_bytes()
data = json.loads(raw)
assert data['status'] == 'complete' and len(data['rows']) == 6
products = ['Jango · Astra', 'Codex · Astra']
cases = ['D01', 'D02', 'D03']
titles = ['Filing reconciliation', 'Portfolio ledger replay', 'Backtest mechanics']
colors = ['#275943', '#647897']
ink, muted, paper, line = '#1d2d24', '#5b675f', '#faf9f5', '#d5dbd2'
sha = lambda b: hashlib.sha256(b).hexdigest()
rows = {(r['case'], r['product']): r for r in data['rows']}
provenance = []
details = []
for tid in cases:
    for product in products:
        row = rows[tid, product]
        numeric_path = SRC / row['directory'] / 'numeric-checks.json'
        review_path = SRC / row['directory'] / 'task-review.json'
        numeric = json.loads(numeric_path.read_text())
        review = json.loads(review_path.read_text())
        assert row['task_success'] == review['full_task_success']
        assert row['passed_checks'] == numeric['passed']
        assert row['total_checks'] == len(numeric['checks'])
        assert all(c['pass'] for c in numeric['checks']) == numeric['all_numeric_decision_checks_pass']
        assert row['task_success'] == all(review['checks'].values())
        response = SRC / row['directory'] / 'response.txt'
        assert sha(response.read_bytes()) == numeric['response_sha256']
        details.append({'case': tid, 'product': product, 'required_checks': review['checks'],
                        'numeric_checks': numeric['checks'], 'response_sha256': numeric['response_sha256']})
        for p in [numeric_path, review_path, response]:
            provenance.append({'source': p.relative_to(SRC).as_posix(), 'bytes': p.stat().st_size,
                               'sha256': sha(p.read_bytes())})
study = json.loads((SRC / 'study-manifest.json').read_text())
for tid in cases:
    assert sha((SRC / tid / 'prompt.txt').read_bytes()) == study['prompt_hashes'][tid]
assert sha((SRC / 'answer-keys.json').read_bytes()) == study['answer_key_sha256']

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

(OUT / 'results.json').write_bytes(raw)
dump('check-breakdown.json', details)
dump('provenance.json', {'source_cohort': SRC.name, 'results_sha256': sha(raw),
     'source_manifest_sha256': sha((SRC / 'manifest.json').read_bytes()),
     'input_prompt_sha256': study['prompt_hashes'], 'answer_key_sha256': study['answer_key_sha256'],
     'files': provenance, 'raw_responses_and_traces': 'Retained in the original local and Desktop archive; not republished by this visual update.'})

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'text.color': ink,
    'axes.labelcolor': muted, 'xtick.color': muted, 'ytick.color': ink,
    'svg.fonttype': 'none', 'axes.edgecolor': line})

def frame(title, subtitle, height=6.3):
    fig = plt.figure(figsize=(12, height), facecolor=paper)
    fig.text(.055, .95, 'TRADING AGENT EVALUATIONS   /   EXPLORATORY PILOT', fontsize=10, color=muted)
    fig.text(.055, .875, title, fontsize=25, weight='bold')
    fig.text(.055, .817, subtitle, fontsize=12, color=muted)
    return fig

def save(fig, name):
    fig.savefig(OUT / f'{name}.png', dpi=180, facecolor=paper)
    fig.savefig(OUT / f'{name}.svg', facecolor=paper)
    plt.close(fig)

scores = [100 * sum(rows[t, p]['task_success'] for t in cases) / len(cases) for p in products]
fig = frame('Jango and Codex tie on the three tested tasks.', 'All required checks passed · 3 selected tasks · 1 trial per task and product')
ax = fig.add_axes([.21, .25, .69, .43], facecolor=paper)
for y, (p, score, color) in enumerate(zip(products, scores, colors)):
    ax.barh(1-y, score, height=.34, color=color, zorder=3)
    ax.text(score-3, 1-y, f'{score:.0f}%  ·  3 / 3 tasks', ha='right', va='center', color='white', weight='bold', fontsize=14)
ax.set_yticks([1, 0], products)
ax.set_xlim(0, 100); ax.set_ylim(-.55, 1.55)
ax.set_xticks([0,25,50,75,100], ['0%','25%','50%','75%','100%'])
ax.grid(axis='x', color=line, zorder=0)
ax.spines[['top','right','left']].set_visible(False); ax.tick_params(axis='y', length=0, pad=16)
ax.set_xlabel('Observed task success', labelpad=12)
fig.text(.055,.105,'Same score. No measured lead in this pilot.',fontsize=14,weight='bold')
fig.text(.055,.055,'These three tasks do not establish the best overall trading agent or investment performance.',fontsize=11,color=muted)
save(fig,'01-task-results')

fig = frame('Every category. Every checked field.', 'Counts are diagnostic checks within tasks, not independent trials.', 7.1)
ax = fig.add_axes([.055,.22,.89,.51]); ax.set_axis_off()
ax.set_xlim(0,1); ax.set_ylim(0,1)
for i,p in enumerate(products):
    ax.text(.59+.265*i, .94, p, ha='center', va='center', fontsize=14, weight='bold', color=colors[i])
descs = ['Periods, cash flow, capex, FCF and ranking',
         'Partial fills, duplicates, split and saved state',
         'Next-open execution, fees and missing prices']
for k,(tid,title,desc) in enumerate(zip(cases,titles,descs)):
    y=.69-.27*k
    ax.text(0,y+.025,f'{tid}  {title}',fontsize=14,weight='bold',va='center')
    ax.text(0,y-.055,desc,fontsize=10,color=muted,va='center')
    for i,p in enumerate(products):
        r=rows[tid,p]; x=.48+.265*i
        ax.add_patch(Rectangle((x,y-.09),.225,.20,facecolor='#e7eee5',edgecolor=line,lw=.8))
        ax.text(x+.1125,y+.025,'PASS',ha='center',va='center',fontsize=16,weight='bold',color=ink)
        ax.text(x+.1125,y-.045,f"{r['passed_checks']} / {r['total_checks']} checks",ha='center',va='center',fontsize=11,color=muted)
fig.text(.055,.12,'143 / 143 mechanical checks for each product, plus the required evidence reviews.',fontsize=12,weight='bold')
fig.text(.055,.065,'The ledger restart used a saved checkpoint and a fresh object. Actual process-crash recovery was not tested.',fontsize=10,color=muted)
save(fig,'02-category-results')

fig = frame('Observed response intervals', 'Every completed run shown · seconds · setup and artifact retrieval excluded',7.2)
ax=fig.add_axes([.235,.24,.66,.49],facecolor=paper)
for i,(p,color) in enumerate(zip(products,colors)):
    ys=[2-k+(.16 if i==0 else -.16) for k in range(3)]
    vals=[rows[t,p]['seconds'] for t in cases]
    ax.barh(ys,vals,height=.25,color=color,label=p,zorder=3)
    for y,v in zip(ys,vals):ax.text(v+5,y,f'{v:.1f}s',va='center',fontsize=11)
ax.set_xlim(0,350); ax.set_yticks([2,1,0],titles); ax.set_xticks([0,60,120,180,240,300])
ax.grid(axis='x',color=line,zorder=0);ax.spines[['top','right','left']].set_visible(False)
ax.tick_params(axis='y',length=0,pad=16);ax.set_xlabel('Seconds',labelpad=10)
ax.legend(frameon=False,ncol=2,loc='lower left',bbox_to_anchor=(0,1.02))
fig.text(.055,.12,'Jango: Deploy → first observed complete answer; includes UI polling delay.',fontsize=11)
fig.text(.055,.08,'Codex: CLI process start → exit. Different clocks; no model-speed ratio claimed.',fontsize=11)
fig.text(.055,.04,'All six observed intervals were within the 600-second response budget.',fontsize=11,color=muted)
save(fig,'03-observed-time')

e=html.escape
cards=''
for tid,title,desc in zip(cases,titles,descs):
    d=[v for v in details if v['case']==tid]
    check_rows=''.join(f'<tr><td>{e(key.replace("_"," "))}</td><td>{"Pass" if d[0]["required_checks"][key] else "Fail"}</td><td>{"Pass" if d[1]["required_checks"].get(key) else "Fail"}</td></tr>' for key in d[0]['required_checks'])
    cards+=f'<details><summary><span>{tid} · {title}</span><span class="pass">Both pass</span></summary><p>{desc}.</p><div class="table-wrap"><table><thead><tr><th>Required evidence check</th><th>Jango</th><th>Codex</th></tr></thead><tbody>{check_rows}</tbody></table></div></details>'

page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Jango & Codex — verified pilot results</title><style>
:root{--ink:#1d2d24;--muted:#5b675f;--line:#d5dbd2;--paper:#faf9f5;--green:#275943;--blue:#647897}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:20px}body{margin:0;color:var(--ink);background:var(--paper);font:17px/1.6 Arial,Helvetica,sans-serif}a{color:inherit;text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid var(--blue);outline-offset:5px}header,main,footer{max-width:1180px;padding:24px 32px;margin:auto}header{display:flex;justify-content:space-between;gap:20px;border-bottom:1px solid var(--line);font:12px/1.5 ui-monospace,monospace;text-transform:uppercase}nav{display:flex;gap:22px;flex-wrap:wrap}h1,h2{font-family:Georgia,'Times New Roman',serif;font-weight:400;letter-spacing:-.035em}h1{font-size:64px;line-height:1.04;max-width:920px;margin:30px 0 22px}h2{font-size:38px;line-height:1.15;margin:0 0 18px}p{max-width:880px}.lead{font-size:23px;line-height:1.4;max-width:850px}.eyebrow,.meta,.small{font:12px/1.6 ui-monospace,monospace;color:var(--muted)}.eyebrow{text-transform:uppercase;letter-spacing:.1em;margin-top:24px}.callout{padding:18px 22px;border:1px solid #bdcbbc;background:#edf1e9;max-width:960px;margin:26px 0}.stats{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);margin:30px 0 44px}.stat{padding:26px 30px}.stat+.stat{border-left:1px solid var(--line)}.name{font-size:18px;font-weight:700}.value{font:60px/1.25 Georgia,serif}.sub{color:var(--muted);font-size:15px}.swatch{display:inline-block;width:12px;height:12px;margin-right:9px}.section{padding:36px 0;border-top:1px solid var(--line)}figure{margin:24px 0 12px;border:1px solid var(--line);background:var(--paper)}figure img{display:block;width:100%;height:auto}figcaption{border-top:1px solid var(--line);padding:13px 18px;font-size:13px;color:var(--muted);display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}.download{white-space:nowrap}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:12px 14px;text-align:left;border-bottom:1px solid var(--line)}th{font:12px ui-monospace,monospace;color:var(--muted)}details{border:1px solid var(--line);margin:12px 0;background:#fffefa}summary{cursor:pointer;padding:19px 20px;display:flex;justify-content:space-between;gap:16px;font-weight:700}summary::before{content:'+';font-weight:400}details[open] summary::before{content:'−'}summary span:first-child{flex:1}.pass{color:var(--green);font:12px ui-monospace,monospace;align-self:center;white-space:nowrap}details>p,.table-wrap{margin:0 20px 18px}li{margin:10px 0}.split{display:grid;grid-template-columns:1fr 1fr;gap:38px}.split h3{font-size:18px}footer{border-top:1px solid var(--line);font-size:13px;color:var(--muted)}.mobile-results{display:none}@media(max-width:700px){header,main,footer{padding:20px}header{display:block}nav{margin-top:12px;gap:16px}h1{font-size:43px}h2{font-size:30px}.lead{font-size:20px}.stat{padding:20px 16px}.value{font-size:43px}.name{font-size:15px}.split{display:block}.section{padding:30px 0}summary{font-size:15px;padding:16px 12px}.mobile-results{display:block}.mobile-results table{font-size:13px}th,td{padding:10px 6px}.small{font-size:11px}}@media print{details{break-inside:avoid}figure{break-inside:avoid}header{position:static}a{text-decoration:none}.download,nav{display:none}}
</style></head><body><header><a href="https://wheel-is.github.io/trading-agent-evals/">Trading agent evaluations</a><nav><a href="#results">Results</a><a href="#categories">Tests</a><a href="#timing">Timing</a><a href="#method">Methodology</a></nav></header><main>
<div class="eyebrow">Exploratory pilot · 17 October 2026 · Astra configurations</div><h1>Jango and Codex tie on the three tested tasks.</h1><p class="lead">Both completed filing reconciliation, portfolio ledger replay and backtest mechanics with all required checks passing.</p><div class="callout"><strong>100% here means 3 out of 3 selected tasks.</strong> This small pilot found no difference in task success. It does not establish a best overall trading agent.</div>
<div class="stats"><div class="stat"><div class="name"><i class="swatch" style="background:var(--green)"></i>Jango · Astra</div><div class="value">100%</div><div class="sub">3 / 3 tasks · equal highest observed score</div></div><div class="stat"><div class="name"><i class="swatch" style="background:var(--blue)"></i>Codex · Astra</div><div class="value">100%</div><div class="sub">3 / 3 tasks · equal highest observed score</div></div></div>
<section class="section" id="results"><div class="eyebrow">01 / Task results</div><h2>Same score. No measured lead.</h2><p>Each task counts once. A pass requires the requested answer, supporting evidence and timely completion. Scores and case selection are unchanged from the frozen study.</p>FIG1</section>
<section class="section" id="categories"><div class="eyebrow">02 / Test breakdown</div><h2>What each product got right</h2><p>All three planned probes are shown. The check counts help locate mistakes; they are not additional independent trials.</p>FIG2<div class="mobile-results"><table><thead><tr><th>Task</th><th>Jango</th><th>Codex</th></tr></thead><tbody><tr><td>Filing reconciliation</td><td>23 / 23</td><td>23 / 23</td></tr><tr><td>Ledger replay</td><td>87 / 87</td><td>87 / 87</td></tr><tr><td>Backtest mechanics</td><td>33 / 33</td><td>33 / 33</td></tr></tbody></table></div>CARDS<p class="small">Expand a test to see the required evidence checks. <a href="check-breakdown.json">Download every expected and observed field ↗</a></p></section>
<section class="section" id="timing"><div class="eyebrow">03 / Observed time</div><h2>Response intervals, shown separately</h2><p>Codex had shorter recorded intervals in these runs. Jango was measured from Deploy to the first observed complete answer; Codex was measured by CLI process wall time. Polling delay and product setup differ, so these are not exact model-speed comparisons.</p>FIG3</section>
<section class="section" id="method"><div class="eyebrow">Methodology</div><h2>How the results were checked</h2><ol><li><strong>Freeze the task.</strong> Three prompts, numerical answer keys, tolerances, two configurations, one trial each and a 600-second response budget were recorded before execution.</li><li><strong>Check the answer.</strong> Every requested numerical and decision field was compared with the same frozen key. Tolerances were 0.000001 for money or units and 0.01 percentage points.</li><li><strong>Verify the evidence.</strong> Filing figures and periods were checked in original official reports. Replay and backtest source files were inspected and independently executed. Required outputs and checkpoint contents were checked separately.</li><li><strong>Count complete tasks.</strong> A task passes only when every required answer and evidence check passes within the response window. The primary score is tasks passed divided by the three tasks. Individual field counts do not change task weights.</li><li><strong>Keep the full record.</strong> All planned tasks remain. Codex D01 had one failure before prompt delivery, followed by the first delivered attempt; Jango D01 had two empty, non-running drafts. These setup failures and all later traces remain in the archive.</li></ol><p>The parser was implemented during collection, using the frozen keys and equivalent JSON representations for both products. No subjective model judge assigned these pilot scores. The original archive passes 591 integrity checks; nine behavioral grader tests cover malformed output and incorrect calculations.</p><div class="split"><div><h3>What this pilot supports</h3><p>Both tested configurations solved these three selected tasks. They retained reproducible programs for the two synthetic computation tasks. This is evidence of capability on these cases.</p></div><div><h3>What remains untested</h3><p>Continuous monitoring, actual process-crash recovery, broker execution, live or paper investment returns and overall superiority. Saving and reloading an object is a narrower test than surviving a process crash.</p></div></div><p><strong>Why no confidence interval?</strong> These are three deliberately selected discovery cases with one trial each, not a representative random sample. Treating the 143 fields as 143 independent experiments would overstate the evidence.</p><p>Both requested or displayed Astra. Identical provider snapshots are unverified. Jango had native delegation and financial integrations; Codex used the recorded CLI web and local-computation profile. This is a product-configuration comparison, not an isolated model experiment. Native UI captures preserve rendered text, not verified backend bytes.</p><p><strong>Difficulty:</strong> both products passed everything, so this pilot has a ceiling effect. Harder, fresh tasks must be fixed before another run; existing scores should not be capped or reweighted to manufacture a separation.</p></section>
<section class="section"><h2>Downloads and earlier results</h2><p><a href="results.json">Results JSON</a> · <a href="check-breakdown.json">Full field breakdown</a> · <a href="provenance.json">Evidence hashes</a> · <a href="manifest.json">Visual package hashes</a></p><p><a href="https://wheel-is.github.io/trading-agent-evals/index.html#performance-index">Open the earlier multi-product evaluation ↗</a></p><p class="small">This is a separate exploratory cohort. It does not replace the earlier results or pool different models, prompts and tool access into a new overall ranking. Raw responses, tool traces, programs, source checks and frozen prompts remain in the complete local and Desktop archive.</p></section></main><footer>Independent evaluation. No affiliation with Vals or endorsement by the evaluated products. Visual update only; no new target runs or revised grades.</footer></body></html>'''
for n,stem,alt,caption in [
    (1,'01-task-results','Jango and Codex each pass three of three selected tasks; both score 100 percent.','Three selected tasks; one trial per configuration and task.'),
    (2,'02-category-results','Both products pass 23 of 23 filing checks, 87 of 87 ledger checks and 33 of 33 backtest checks.','Same frozen keys and required evidence checks for both configurations.'),
    (3,'03-observed-time','Jango intervals: 279.6, 287.9, 263.0 seconds. Codex intervals: 76.1, 80.2, 52.5 seconds. Clock definitions differ.','Different clock definitions; setup and artifact retrieval excluded.')]:
    figure=f'<figure><img src="{stem}.svg" alt="{alt}" width="2160" height="{1134 if n==1 else 1278 if n==2 else 1296}" loading="{"eager" if n==1 else "lazy"}"><figcaption><span>{caption}</span><span class="download"><a href="{stem}.png" download>PNG ↓</a> · <a href="{stem}.svg" download>SVG ↓</a></span></figcaption></figure>'
    page=page.replace('FIG'+str(n),figure)
page=page.replace('CARDS',cards)
(OUT/'index.html').write_text(page)
shutil.copy2(__file__,OUT/'build-visuals.py')
(OUT/'REPRODUCE.txt').write_text('This folder is a visual presentation of strength-discovery-20261017. No new target runs or grade changes.\nTo rebuild: install matplotlib 3.9.4, set DISCOVERY_SOURCE to the full original cohort and DISCOVERY_PRESENTATION to a new output directory, then run build-visuals.py.\nThe complete source cohort and raw traces are retained beside this folder in the Desktop archive.\n')
dump('validation.json', {'pass': True, 'rows_matched_to_source': 6, 'numeric_checks_verified': sum(r['total_checks'] for r in data['rows']), 'source_response_hashes_verified': 6, 'frozen_prompt_hashes_verified': 3, 'frozen_answer_key_verified': True, 'changed_scores': 0, 'new_target_runs': 0, 'original_archive_audit': {'checks':591,'pass':True}, 'generated_at':datetime.now(timezone.utc).isoformat()})
files=[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['manifest.json','publication-receipt.json','desktop-export-receipt.json','visual-qa.json']]
dump('manifest.json',{'files':files,'scope':'Visual presentation and aggregate result/check data only. Original raw archive unchanged.'})
print(json.dumps({'output':str(OUT),'files':len(files),'scores':dict(zip(products,scores))}))
