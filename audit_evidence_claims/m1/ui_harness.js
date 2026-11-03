const fs = require('fs');
const vm = require('vm');
const page = fs.readFileSync('web/try.html', 'utf8');
const code = page.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements = new Map();
function el(id) {
  if (!elements.has(id)) elements.set(id, {innerHTML:'', value:'', events:{}, addEventListener(n,f){this.events[n]=f;}, requestSubmit(){return this.events.submit({preventDefault(){}});}});
  return elements.get(id);
}
const pending = [];
const ctx = vm.createContext({console, document:{getElementById:el}, fetch:async (path, init)=>new Promise(resolve=>pending.push({text:JSON.parse(init.body).text, resolve}))});
vm.runInContext(code, ctx);
const run = c=>vm.runInContext(c, ctx);
const result = {};
const maps=JSON.parse(fs.readFileSync('audit_evidence_claims/m1/ui_real_maps.json','utf8'));
const map = (id)=>({center:{id,type:'Drug',label:id,trials:1,props:{}},groups:[]});
async function reply(data) { const q=pending.shift(); q.resolve({ok:true,json:async()=>data}); await new Promise(setImmediate); return q.text; }
async function load(id) { const done=run(`explore(${JSON.stringify(id)})`); await reply(maps[id]||map(id)); await done; }
(async()=>{
  await load('osimertinib'); await load('EGFR');
  result.beforeFailure={trail:run('JSON.stringify(trail)'),html:el('trail0').innerHTML};
  el('t0').value='Mvasi'; el('f0').events.submit({preventDefault(){}});
  await reply({refused:'Mvasi',why:'distinct_product'});
  result.afterRefusal={trail:run('JSON.stringify(trail)'),trailHTML:el('trail0').innerHTML,output:el('o0').innerHTML};
  try { el('trail0').events.click({target:{closest:()=>({dataset:{back:'0'}})}}); } catch(e) {result.oldBackButtonError=e.toString();}
  result.failureVariants={};
  for(const kind of ['not_found','server_error']){
    run('trail.length=0'); await load('osimertinib'); await load('EGFR');
    el('t0').value=kind==='not_found'?'unknown-m1-entity':'server-error-fixture';
    el('f0').events.submit({preventDefault(){}});
    if(kind==='not_found') await reply({not_found:'unknown-m1-entity'});
    else {const q=pending.shift();q.resolve({ok:false,json:async()=>({error:'fixture error'})});await new Promise(setImmediate);}
    result.failureVariants[kind]={trail:run('JSON.stringify(trail)'),html:el('trail0').innerHTML,output:el('o0').innerHTML};
    try{el('trail0').events.click({target:{closest:()=>({dataset:{back:'0'}})}});}catch(e){result.failureVariants[kind].backError=e.toString();}
  }
  run('trail.length=0');
  const d1=run('explore("EGFR")'),d2=run('explore("EGFR")');
  await reply(maps.EGFR);await d1;await reply(maps.EGFR);await d2;
  result.doubleClick={trail:run('JSON.stringify(trail)'),html:el('trail0').innerHTML};
  run('trail.length=0');
  const a=run('explore("EGFR")'), b=run('explore("KRAS")');
  const first=pending.shift(),second=pending.shift();
  second.resolve({ok:true,json:async()=>maps.KRAS}); await b;
  first.resolve({ok:true,json:async()=>maps.EGFR}); await a;
  result.reverseResponses={trail:run('JSON.stringify(trail)'),finalOutput:el('o0').innerHTML};
  const injection={center:{id:'x" onload="bad',label:'<img src=x onerror=bad()>',type:'Trial',props:{url:'javascript:alert(document.domain)',title:'<svg onload=bad()>'}},groups:[{rel:'EVALUATES',dir:'out',type:'Trial',total:1,items:[{id:'x" onclick="bad()',type:'Trial',label:'<script>bad()</script>',edge_id:'e" onclick="bad()',url:'javascript:alert(document.domain)',title:'<img src=x onerror=bad()>',phases:['PHASE2'],weight:1}]}]};
  const inj=run('explore("fixture")'); await reply(injection); await inj;
  result.injectionHTML=el('o0').innerHTML;
  result.action=run('itemDetail({type:"Target",action:"AGONIST"},"ACTS_ON")');
  result.binding=run('itemDetail({type:"Target",action:"BINDING AGENT"},"ACTS_ON")');
  result.unknownSponsorClass=run('itemDetail({type:"Company",weight:2,sponsor_class:"UNKNOWN"},"SPONSORS_TRIAL_OF")');
  result.real = {};
  for(const [input,r] of Object.entries(maps)) {
    ctx.r=r;
    const svg=run('drawMap(r)');
    result.real[input]={center:r.center,groups:r.groups.map(g=>({rel:g.rel,dir:g.dir,type:g.type,total:g.total,returned:g.items.length})),drawn:(svg.match(/class="nd"/g)||[]).length};
    if(['NCT00754364','NCT00200395'].includes(input)) result.real[input].groupLabels=run('r.groups.map(g=>({label:GKO[g.rel+"|"+g.dir],type:g.type,items:g.items}))');
  }
  fs.writeFileSync('audit_evidence_claims/m1/ui_harness_results.json',JSON.stringify(result,null,2));
  console.log(JSON.stringify({trailError:result.oldBackButtonError,action:result.action,binding:result.binding,real:result.real},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
