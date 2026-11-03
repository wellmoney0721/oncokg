const fs = require('fs');
const vm = require('vm');
const OUT = 'audit_evidence_claims/m14/db_ui/';
const page = fs.readFileSync('web/try.html', 'utf8');
const code = page.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements = new Map();
function el(id) {
  if (!elements.has(id)) elements.set(id, {innerHTML:'', value:'', events:{}, addEventListener(n,f){this.events[n]=f;}, requestSubmit(){return this.events.submit({preventDefault(){}});}});
  return elements.get(id);
}
const pending = [];
const ctx = vm.createContext({console, document:{getElementById:el}, fetch:async (path, init)=>new Promise((resolve,reject)=>pending.push({path,body:JSON.parse(init.body), text:JSON.parse(init.body).text,resolve,reject}))});
vm.runInContext(code, ctx);
const run = c=>vm.runInContext(c,ctx);
const result = {parsedEntirePage:true,initializedElements:[...elements.keys()]};
const maps = JSON.parse(fs.readFileSync(OUT+'ui_real_maps.json','utf8'));
const map = id=>({center:{id,type:'Drug',label:id,trials:1,props:{}},groups:[]});
async function tick(){await new Promise(setImmediate);}
async function reply(data){const q=pending.shift();q.resolve({ok:true,json:async()=>data});await tick();return q.text;}
async function load(id,data){const p=run(`explore(${JSON.stringify(id)})`);await reply(data||maps[id]||map(id));await p;return el('o0').innerHTML;}
function snap(){return {trail:JSON.parse(run('JSON.stringify(trail)')),trailHTML:el('trail0').innerHTML,output:el('o0').innerHTML};}
function clickBack(i){return el('trail0').events.click({target:{closest:()=>({dataset:{back:String(i)}})}});}
(async()=>{
  result.failureVariants={};
  for(const kind of ['refused','not_found','server_error','network_error']){
    run('trail.length=0');await load('osimertinib');await load('EGFR');
    el('t0').value=kind==='refused'?'Mvasi':kind==='not_found'?'unknown-m1-entity':kind;
    el('f0').events.submit({preventDefault(){}});
    if(kind==='refused')await reply({refused:'Mvasi',why:'distinct_product'});
    if(kind==='not_found')await reply({not_found:'unknown-m1-entity'});
    if(kind==='server_error'){pending.shift().resolve({ok:false,json:async()=>({error:'fixture error'})});await tick();}
    if(kind==='network_error'){pending.shift().reject(new Error('fixture network error'));await tick();}
    result.failureVariants[kind]=snap();
    try{clickBack(0);result.failureVariants[kind].oldButtonThrows=false;}catch(e){result.failureVariants[kind].oldButtonThrows=String(e);}
  }
  run('trail.length=0');
  const d1=run('explore("EGFR")'),d2=run('explore("EGFR")');await reply(maps.EGFR);await d1;await reply(maps.EGFR);await d2;
  result.doubleClick=snap();
  run('trail.length=0');
  const a=run('explore("EGFR")'),b=run('explore("KRAS")');
  const first=pending.shift(),second=pending.shift();second.resolve({ok:true,json:async()=>maps.KRAS});await b;first.resolve({ok:true,json:async()=>maps.EGFR});await a;
  result.reverseResponses=snap();
  run('trail.length=0');
  const a2=run('explore("EGFR")'),b2=run('explore("KRAS")');
  const first2=pending.shift(),second2=pending.shift();second2.resolve({ok:true,json:async()=>maps.KRAS});await b2;first2.reject(new Error('stale error'));await a2;
  result.staleError=snap();
  run('trail.length=0');await load('osimertinib');await load('EGFR');
  clickBack(0);await reply(maps.osimertinib);result.backAfterSuccess=snap();
  const injection={center:{id:'x" onload="bad',label:'<img src=x onerror=bad()>',type:'Trial',matched_text:'<img src=x onerror=bad()>',props:{url:'javascript:alert(document.domain)',title:'<svg onload=bad()>'}},also:[{id:'a" onclick="bad()',type:'UnknownType',label:'<svg onload=bad()>'},{refused:'<script>bad()</script>'}],groups:[{rel:'EVALUATES',dir:'out',type:'Trial',total:1,items:[{id:'x" onclick="bad()',type:'Trial',label:'<script>bad()</script>',edge_id:'e" onclick="bad()',url:'javascript:alert(document.domain)',title:'<img src=x onerror=bad()>',phases:['PHASE2'],weight:1}]}]};
  result.injectionHTML=await load('fixture',injection);
  result.urlChecks={};
  for(const u of ['javascript:alert(1)','data:text/html,<script>alert(1)</script>','https://evil.test/','https://clinicaltrials.gov.evil.test/','https://clinicaltrials.gov@evil.test/','https://clinicaltrials.gov\\@evil.test/','https://clinicaltrials.gov/study/NCT00200395','https://www.clinicaltrials.gov/study/NCT00200395']){ctx.u=u;result.urlChecks[u]=run('safeUrl(u)');}
  result.details={action:run('itemDetail({type:"Target",action:"AGONIST"},"ACTS_ON")'),binding:run('itemDetail({type:"Target",action:"BINDING AGENT"},"ACTS_ON")'),classes:{}};
  for(const c of ['INDUSTRY','NIH','FED','OTHER_GOV','NETWORK','OTHER','UNKNOWN']){ctx.c=c;result.details.classes[c]=run('itemDetail({type:"Company",weight:2,sponsor_class:c},"SPONSORS_TRIAL_OF")');}
  result.real={};
  for(const [input,r]of Object.entries(maps)){
    ctx.r=r;const svg=run('drawMap(r)');const html=await load(input,r);
    result.real[input]={center:r.center,also:r.also,groups:r.groups.map(g=>({rel:g.rel,dir:g.dir,type:g.type,role:g.role,total:g.total,returned:g.items.length})),drawn:(svg.match(/class="nd"/g)||[]).length,ringNotice:(svg.match(/<p class="note">(.*?)<\/p>/)||[])[1],groupLabels:run('r.groups.map(g=>({heading:groupHead(g),type:g.type,role:g.role,details:g.items.map(it=>({id:it.id,detail:itemDetail(it,g.rel)}))}))'),html};
  }
  const unknown={center:{id:'T',label:'Fixture trial',type:'Trial',props:{}},groups:[{rel:'SPONSORS',dir:'in',type:'Company',role:null,total:1,items:[{id:'C',label:'Unknown role',type:'Company',edge_id:'fixture',weight:0}]}]};
  result.missingRoleHTML=await load('missing role',unknown);
  const future={center:{id:'X',label:'Future',type:'Other',props:{}},groups:[{rel:'NEWREL',dir:'in',type:'Other',role:null,total:1,items:[{id:'Y',label:'Other node',type:'Other',edge_id:'fixture',weight:0}]}]};
  result.unknownTypeHTML=await load('unknown type',future);
  // Replaying an old trail button while a new root lookup is pending must not throw.
  run('trail.length=0');await load('osimertinib');await load('EGFR');el('t0').value='AstraZeneca';el('f0').events.submit({preventDefault(){}});
  result.pendingNewLookup={trailHTML:el('trail0').innerHTML,trail:JSON.parse(run('JSON.stringify(trail)'))};
  try{clickBack(0);result.pendingNewLookup.oldButtonThrows=false;}catch(e){result.pendingNewLookup.oldButtonThrows=String(e);}
  await reply(maps.AstraZeneca);
  fs.writeFileSync(OUT+'ui_harness_results.json',JSON.stringify(result,null,2));
  console.log(JSON.stringify({parsedEntirePage:result.parsedEntirePage,failures:Object.fromEntries(Object.entries(result.failureVariants).map(([k,v])=>[k,{trail:v.trail,trailHTML:v.trailHTML,oldButtonThrows:v.oldButtonThrows}])),doubleClickTrail:result.doubleClick.trail,reverseTrail:result.reverseResponses.trail,staleErrorTrail:result.staleError.trail,urlChecks:result.urlChecks,details:result.details,real:Object.fromEntries(Object.entries(result.real).map(([k,v])=>[k,{center:v.center.id,drawn:v.drawn,ringNotice:v.ringNotice}]))},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
