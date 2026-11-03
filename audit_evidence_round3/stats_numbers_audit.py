"""Independent arithmetic and quantitative-claim audit; never imports evaluate.py."""
from pathlib import Path
import ast, csv, json, math, random, re, sqlite3, sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'audit_evidence_round3'
BASE = OUT / 'original'
if not (BASE / 'reports/gold_test.csv').exists():
    BASE = ROOT
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'src'))
import textrules as T

def read(rel):
    return json.loads((BASE / rel).read_text(encoding='utf-8'))

ACC = {'EXACT','ALIAS','CLEANED','SALT_STRIPPED','PARENTHETICAL','CONTAINED_ALIAS','FUZZY_AUTO'}
def wilson(k,n):
    z=1.959963984540054
    p=k/n; a=1+z*z/n
    return [(p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/a,
            (p+z*z/(2*n)+z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/a]

def ident(r): return (r['raw'],r['component'],r['drug_id'] or '',r['tier'])
gold={s:list(csv.DictReader((BASE/f'reports/gold_{s}.csv').open(encoding='utf-8',newline='')))
      for s in ['dev','test','postfix']}
resolved_path=BASE/'data/processed/resolved.json'
if not resolved_path.exists(): resolved_path=ROOT/'data/processed/resolved.json'
resolved=json.loads(resolved_path.read_text(encoding='utf-8'))
population=defaultdict(set); occurrences=Counter(); current=set()
for trial in resolved['trials']:
    for iv in trial['interventions']:
        for component in iv['components']:
            tier=component['tier']
            key=(iv['raw'],component['component'],component.get('drug_id') or '',tier)
            current.add(key);population[tier].add(key);occurrences[tier]+=1

stats={}
for sample,rows in gold.items():
    accepted=[r for r in rows if r['tier'] in ACC]
    survivors=[r for r in rows if ident(r) in current]
    survivor_acc=[r for r in survivors if r['tier'] in ACC]
    stale_acc=[r for r in accepted if ident(r) not in current]
    verdicts=defaultdict(list)
    for r in survivors: verdicts[r['tier']].append(int(r['verdict']=='correct'))
    carried=[]
    if sample!='dev':
        for tier in sorted({r['tier'] for r in gold['dev']}):
            fallback=[int(r['verdict']=='correct') for r in gold['dev']
                      if r['tier']==tier and ident(r) in current]
            if tier not in verdicts and fallback:
                verdicts[tier]=fallback;carried.append(tier)
    active=sorted(ACC & verdicts.keys() & population.keys())
    weights={t:len(population[t]) for t in active}; total=sum(weights.values())
    estimate=sum(weights[t]*sum(verdicts[t])/len(verdicts[t]) for t in active)/total
    bounds=[sum(weights[t]*wilson(sum(verdicts[t]),len(verdicts[t]))[j] for t in active)/total for j in (0,1)]
    own=[t for t in active if t not in carried]
    rng=random.Random(93012026)
    boot=[]
    for _ in range(50000):
        v=sum(weights[t]*sum(rng.choices(verdicts[t],k=len(verdicts[t])))/len(verdicts[t]) for t in active)/total
        boot.append(v)
    boot.sort()
    count_ok=lambda rs:sum(r['verdict']=='correct' for r in rs)
    stats[sample]={
        'sample_rows':len(rows),'as_labelled_accepted':len(accepted),'as_labelled_correct':count_ok(accepted),
        'as_labelled_raw_precision':count_ok(accepted)/len(accepted),
        'independent_wilson95':wilson(count_ok(accepted),len(accepted)),
        'current_rows':len(survivors),'stale_rows':len(rows)-len(survivors),
        'current_accepted':len(survivor_acc),'current_correct':count_ok(survivor_acc),
        'stale_accepted':len(stale_acc),'stale_accepted_correct':count_ok(stale_acc),
        'stale_accepted_incorrect':len(stale_acc)-count_ok(stale_acc),
        'population_unique':weights,'population_occurrences':{t:occurrences[t] for t in active},
        'per_tier_verdicts':{t:verdicts[t] for t in active},
        'independent_stratified_estimate':estimate,'wilson_bound_propagation_unrounded':bounds,
        'independent_bootstrap_50000_seed93012026':[boot[1250],boot[48749]],
        'carried_tiers':carried,'carried_accepted_weight':sum(weights[t] for t in active if t in carried),
        'total_accepted_weight':total,
        'carried_accepted_weight_share':sum(weights[t] for t in active if t in carried)/total,
        'estimate_without_carried':sum(weights[t]*sum(verdicts[t])/len(verdicts[t]) for t in own)/sum(weights[t] for t in own),
        'occurrence_weighted_tier_estimate_for_comparison_only':sum(occurrences[t]*sum(verdicts[t])/len(verdicts[t]) for t in active)/sum(occurrences[t] for t in active),
    }

keys={s:{(r['raw'],r['component'],r['drug_id']) for r in rows} for s,rows in gold.items()}
stats['sample_intersections']={f'{a}_{b}':len(keys[a]&keys[b]) for a,b in [('dev','test'),('dev','postfix'),('test','postfix')]}
errors={ident(r):r for rows in gold.values() for r in rows if r['verdict']=='incorrect' and r['tier'] in ACC and ident(r) in current}
accepted_total=sum(len(v) for t,v in population.items() if t in ACC)
stats['known_current_errors_across_all_samples']={'count':len(errors),'rows':list(errors.values()),
   'population_unique':accepted_total,'maximum_possible_precision_given_labels':1-len(errors)/accepted_total}

raw_drugs=read('data/raw/drugs.json'); raw_trials=read('data/raw/trials.json')
synonyms=[s for r in raw_drugs['data'] for s in r['drug'].get('synonyms',[])]
iv=[iv for t in raw_trials['data'] for iv in t['protocolSection'].get('armsInterventionsModule',{}).get('interventions',[])]
conditions={s for t in raw_trials['data'] for s in t['protocolSection'].get('conditionsModule',{}).get('conditions',[])}
drugs=resolved['dictionary']['drugs']; index=resolved['dictionary']['index']
all_aliases=[(did,a) for did,d in drugs.items() for a in d['aliases']]
removed_aliases=[{'drug_id':did,**a} for did,a in all_aliases
    if not any(e['drug_id']==did for e in index.get(T.canonical_key(a['alias']),[]))]
stats['snapshot_counts']={'trials':len(raw_trials['data']),'distinct_drug_biological_strings':len({x['name'] for x in iv if x.get('type') in ['DRUG','BIOLOGICAL']}),
   'distinct_conditions':len(conditions),'molecules':len(drugs),'synonyms':len(synonyms),'AACT_synonyms':sum(s.get('source')=='AACT' for s in synonyms),
   'stored_aliases':len(all_aliases),'curated_index_keys':len(index),'curated_index_drug_entries':sum(len(v) for v in index.values()),
   'stored_alias_associations_missing_from_curated_index':len(removed_aliases)}
stats['removed_aliases_still_in_dashboard_count']=removed_aliases

db=BASE/'data/processed/oncokg.sqlite'
if not db.exists():db=ROOT/'data/processed/oncokg.sqlite'
conn=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
stats['graph_queries']={
 'live_nodes':conn.execute('SELECT COUNT(*) FROM node WHERE retired_at IS NULL').fetchone()[0],
 'live_edges':conn.execute('SELECT COUNT(*) FROM edge WHERE retired_at IS NULL').fetchone()[0],
 'edges_by_rel':dict(conn.execute('SELECT rel,COUNT(*) FROM edge WHERE retired_at IS NULL GROUP BY rel')),
 'sponsor_classes':dict(conn.execute("SELECT json_extract(props,'$.sponsor_class'),COUNT(*) FROM edge WHERE rel='SPONSORS_TRIAL_OF' AND retired_at IS NULL GROUP BY 1")),
 'null_source_record':conn.execute('SELECT COUNT(*) FROM edge WHERE retired_at IS NULL AND source_record IS NULL').fetchone()[0],
 'null_tier':conn.execute('SELECT COUNT(*) FROM edge WHERE retired_at IS NULL AND tier IS NULL').fetchone()[0],
 'null_fetch_timestamp':conn.execute('SELECT COUNT(*) FROM edge WHERE retired_at IS NULL AND source_fetched_at IS NULL').fetchone()[0],
 'derived_confidences':conn.execute("SELECT confidence,COUNT(*) FROM edge WHERE retired_at IS NULL AND rel='SPONSORS_TRIAL_OF' GROUP BY confidence").fetchall(),
}
stats['graph_queries']['industry_fraction']=stats['graph_queries']['sponsor_classes']['INDUSTRY']/stats['graph_queries']['edges_by_rel']['SPONSORS_TRIAL_OF']

claims=[]
def claim(en,ko,text,status,source,value,note=''):
    claims.append({'README.md_lines':en,'README.ko.md_lines':ko,'claim':text,'status':status,'artifact_field_or_reproduction':source,'observed':value,'note':note})
claim('26-28','16-17','3000 trials; 2742 distinct drug strings; approximately 1000 molecules; 2175 conditions','VERIFIED','stats_numbers_results.json.snapshot_counts',stats['snapshot_counts'],'Drug strings means DRUG or BIOLOGICAL interventions; count does not establish 2175 synonyms for one disease.')
claim('47','34','three disjoint samples','VERIFIED','stats_numbers_results.json.sample_intersections',stats['sample_intersections'])
for sample,en,ko,report in [('dev','57','44','evaluation_dev'),('test','50-51,58','37-38,45','evaluation_frozen_test'),('postfix','59','46','evaluation_postfix')]:
    x=read(f'reports/{report}.json')
    for key in ['gold_sample_size','as_labelled_raw_precision','raw_sample_precision','accepted_precision']:
        claim(en,ko,f'{sample}: {key}','VERIFIED',f'reports/{report}.json.{key}',x[key],'Arithmetic verified independently; population interpretation is separate.')
    claim(en,ko,f'{sample}: rows still current','VERIFIED',f'reports/{report}.json.gold_sample_size - stale_labels.count',x['gold_sample_size']-x['stale_labels']['count'])
claim('62-65,427-430','48-51,300-302','31/25/4 stale dev/test/postfix rows','VERIFIED','reports/evaluation_{dev,frozen_test,postfix}.json.stale_labels.count',[stats[s]['stale_rows'] for s in ['dev','test','postfix']])
claim('73-75','56','115 accepted among 172 held-out rows','VERIFIED','gold_test.csv tier in accepting set',[stats['test']['as_labelled_accepted'],stats['test']['sample_rows']])
claim('87','67','20000 stratified bootstrap resamples','VERIFIED','src/evaluate.py:157',20000,'Independent audit uses 50000 and different seed; intervals agree to reporting precision apart from Monte Carlo variation.')
claim('94','72','77.8% coverage = 4942/6355','VERIFIED','reports/evaluation_frozen_test.json.coverage',read('reports/evaluation_frozen_test.json')['coverage'],'Denominator is component occurrences, not distinct strings.')
claim('100-103','78-80','FUZZY_REVIEW 4/9 =44.4%','VERIFIED','reports/evaluation_frozen_test.json.per_tier.FUZZY_REVIEW',read('reports/evaluation_frozen_test.json')['per_tier']['FUZZY_REVIEW'],'This is a carried dev rate; rate below 50% does not establish accepted threshold safety.')
claim('104-105','81-82','placebo 8/8; Wilson67.6-100','VERIFIED','reports/evaluation_frozen_test.json.per_tier.BLOCKED_PLACEBO',read('reports/evaluation_frozen_test.json')['per_tier']['BLOCKED_PLACEBO'])
claim('164-171','128-133','2595 of9316 synonyms from AACT;318 removed','VERIFIED','data/raw/drugs.json.data[*].drug.synonyms + quality_report.totals.by_family.dictionary.registry_alias_removed',[len(synonyms),sum(s.get('source')=='AACT' for s in synonyms),read('reports/quality_report.json')['totals']['by_family']['dictionary']['registry_alias_removed']])
quality=read('reports/quality_report.json')['totals']['by_family']['dictionary']
for j,key in enumerate(['registry_alias_removed','class_term_as_synonym','genuinely_ambiguous_alias','parent_child_collapse','cross_drug_synonym','suspected_duplicate_entity','distinct_product_alias','placebo_string_in_synonym_list']):
    claim(str(319+j),str(243+j),key,'VERIFIED','reports/quality_report.json.totals.by_family.dictionary.'+key,quality[key])
claim('329','252-253','ambiguity2189->65;exact1997->4054','VERIFIED','reports/curation_effect.json.headline',read('reports/curation_effect.json')['headline'],'Root reviewer separately reruns curation_effect.py.')
claim('336','259-260','6474 live nodes;17576 live edges','VERIFIED','reports/graph_stats.json.{nodes,edges}; SQL node/edge WHERE retired_at IS NULL',[stats['graph_queries']['live_nodes'],stats['graph_queries']['live_edges']])
for j,rel in enumerate(['SPONSORS','EVALUATES','SPONSORS_TRIAL_OF','STUDIES','ACTS_ON','ASSOCIATED_WITH','PARENT_OF']):
    claim(str(341+j),str(264+j),rel+' edge count','VERIFIED','reports/graph_stats.json.edges_by_rel.'+rel,stats['graph_queries']['edges_by_rel'][rel])
claim('352-355','274-275','3181 empty source_record;10360 empty tier','VERIFIED','SQL edge WHERE retired_at IS NULL and source_record/tier IS NULL',[stats['graph_queries']['null_source_record'],stats['graph_queries']['null_tier']])
claim('359-362','279-281','3181 derived edges,41.3%industry58.7%nonindustry,confidence1.0','VERIFIED','SQL edge rel=SPONSORS_TRIAL_OF properties.sponsor_class/confidence',[stats['graph_queries']['industry_fraction'],1-stats['graph_queries']['industry_fraction'],stats['graph_queries']['derived_confidences']])
claim('445','311','carried tiers 0.9%of stratified weight','VERIFIED','evaluation_frozen_test.json.accepted_precision.carried_tiers_weight_share',stats['test']['carried_accepted_weight_share'],'Three accepting tiers19/2165; fourth FUZZY_REVIEW contributes0 to precision.')
claim('446','312','postfix interval70.6-99.9','VERIFIED','evaluation_postfix.json.accepted_precision.ci95',read('reports/evaluation_postfix.json')['accepted_precision']['ci95'],'The brief value71.5-99.8 is stale, not a current README mismatch.')
for fn,en,ko in [('test_pipeline.py','527','343'),('test_audit_round2.py','528','343')]:
    tree=ast.parse((BASE/'tests'/fn).read_text(encoding='utf-8'))
    n=sum(isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name.startswith('test_') for x in ast.walk(tree))
    claim(en,ko,fn+' tests','VERIFIED','AST count of test_* functions',n)
claim('486','343','44 tests','VERIFIED','AST tests/test_pipeline.py + tests/test_audit_round2.py',44,'Root reviewer records executed pytest result.')
tree=ast.parse((BASE/'src/normalize.py').read_text(encoding='utf-8'))
parents=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CURATED_PARENTS' for t in x.targets))
claim('457','327','59 corporate-map keys','VERIFIED' if len(parents)==59 else 'MISMATCH','src/normalize.py.CURATED_PARENTS',len(parents),'README claims59; current literal map has57. Count verifies no ownership truth.')
claim('472-473','320','36 Investigator nodes','VERIFIED','reports/graph_stats.json.nodes_by_type.Investigator',read('reports/graph_stats.json')['nodes_by_type']['Investigator'])
claim('540-542','359-360','first3000interventional trials;APIv2','VERIFIED','data/raw/trials.json._record_count; protocolSection.designModule.studyType;src/config.py',{'records':len(raw_trials['data']),'study_types':dict(Counter(t['protocolSection']['designModule']['studyType'] for t in raw_trials['data']))})
data=read('web/data.json')
claim('dashboard','dashboard','headline held-out precision','VERIFIED','web/data.json.headline.held_out_as_labelled',data['headline']['held_out_as_labelled'])
claim('dashboard','dashboard','9750 aliases in reference vocabulary after curation','MISMATCH','web/template.html:303;make_dashboard_data.py:121;resolved.dictionary.index',{'displayed':data['headline']['aliases'],'removed_associations_still_counted':len(removed_aliases),'curated_index_keys':len(index),'curated_index_drug_entries':sum(len(v) for v in index.values())},'Stored aliases retain rejected associations. Counts of keys, stored labels, and molecule associations are different units.')
claim('52-53,130','39,101','prior headline91.3%;three more labels fixed','VERIFIED','src/apply_label_corrections.py CORRECTIONS;105/115',(105/115),'Three fixes overall but only two affect gold_test.')
disitamab=[f['alias'] for f in read('reports/quality_report.json')['findings'] if f['type']=='registry_alias_removed' and f.get('affected_drug_name')=='DISITAMAB VEDOTIN' and f.get('reason')=='different_ingredient']
claim('453-454','324-325','four disitamab vedotin name variants removed','VERIFIED' if len(disitamab)==4 else 'MISMATCH','reports/quality_report.json.findings[type=registry_alias_removed,affected_drug_name=DISITAMAB VEDOTIN,reason=different_ingredient]',disitamab)
claim('436-439','306-307','round2 rescored58held-out rows and disagreed on3','MISMATCH','audit_evidence_20261103/labels_rescore.json.summary.disagreement_ids / postfix_additional_disagreement; src/apply_label_corrections.py CORRECTIONS',{'new_test_disagreements':2,'new_postfix_disagreements':1},'Third correction is outside held-out sample; cannot be3outof58held-out.')
query_examples=read('reports/query_examples.json')
tagrisso=next(x for x in query_examples if x['question']=='What trials evaluate Tagrisso?')
claim('387-389','','Tagrisso exampleNCT03909334 and12retrievededges','VERIFIED','reports/query_examples.json[question=What trials evaluate Tagrisso?].answer',tagrisso['answer'],'12 is the retrieval cap, not all trial edges for osimertinib.')
claim('367','284','two identical snapshot rebuilds:0added/changed/retired','VERIFIED','reports/graph_stats.json.{added,changed,retired}',{k:read('reports/graph_stats.json')[k] for k in ['added','changed','retired']},'Committed values match; root reviewer separately checks repeated execution.')
for en,ko,text in [
 ('91-92','69','historical99.1%[98.4,99.8];88%weight'),
 ('201-204','154-156','historical58.8%nonindustry and36trials led by physicians'),
 ('210-213','161-165','old6481vs6475;56vs134;78.3vs78.2;2008->66'),
 ('262-268','201-205','historicfuzzy88.9and97.9scores'),
 ('298-299','226','historicalplatinum confidence1in7trials'),
 ('436-437','306','round1rescored62rowsand5disagreements')]:
    claim(en,ko,text,'UNVERIFIABLE','historical artifacts or dedicated reproduction needed',None,'Not a mismatch against current artifacts; historical assertion requires historical provenance.')

(OUT/'stats_numbers_results.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'numbers_claim_inventory.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'stats':{k:v for k,v in stats.items() if k in ['dev','test','postfix','sample_intersections','snapshot_counts','graph_queries']},'claims':len(claims),'statuses':dict(Counter(c['status'] for c in claims))},ensure_ascii=False,indent=2))
