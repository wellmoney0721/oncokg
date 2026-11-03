const fs = require('fs'), vm = require('vm');
const OUT = 'audit_evidence_claims/m3/';
const code = fs.readFileSync('web/try.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(), pending=[];
function el(id){if(!elements.has(id))elements.set(id,{innerHTML:'',value:'',events:{},addEventListener(n,f){this.events[n]=f;},requestSubmit(){return this.events.submit({preventDefault(){}});}});return elements.get(id);}
const ctx=vm.createContext({document:{getElementById:el},console,fetch:async(path,init)=>new Promise(resolve=>pending.push({path,body:JSON.parse(init.body),resolve}))});
vm.runInContext(code,ctx);
const run=c=>vm.runInContext(c,ctx);
const maps=JSON.parse(fs.readFileSync(OUT+'ui_real_maps.json','utf8'));
const result={precision:[],scoreTypeChecks:[],missingRoleChecks:[],markupChecks:{},pendingRootTrail:{}};
for(const input of ['EGFR','KRAS','MONDO_0005233']) {
  for(const group of maps[input].groups.filter(g=>g.rel==='ASSOCIATED_WITH')){
    for(const item of group.items){ctx.item=item;result.precision.push({input,edge_id:item.edge_id,stored_api_score:item.score,rendered:run('itemDetail(item,"ASSOCIATED_WITH")')});}
  }
}
for(const value of [true,false,null,0,0.8883707400322897]){
  ctx.item={type:'Target',label:'EGFR',score:value};
  try{result.scoreTypeChecks.push({score:value,detail:run('itemDetail(item,"ASSOCIATED_WITH")')});}
  catch(e){result.scoreTypeChecks.push({score:value,error:String(e)});}
}
for(const type of ['Company','Investigator','Other']){
  for(const direction of ['in','out']){
    for(const role of [null,'','not_a_known_role','lead_sponsor','collaborator']){
      ctx.g={type,dir:direction,rel:'SPONSORS',role};result.missingRoleChecks.push({group:ctx.g,heading:run('groupHead(g)')});
    }
  }
}
const h=JSON.parse(fs.readFileSync(OUT+'ui_harness_results.json','utf8'));
result.markupChecks={
  injectionHasRawImg:h.injectionHTML.includes('<img'),
  injectionHasRawScript:h.injectionHTML.includes('<script'),
  injectionHasJavascriptHref:h.injectionHTML.includes('href="javascript:'),
  escapedNodeId:h.injectionHTML.includes('data-id="x&quot; onclick=&quot;bad()"'),
  unknownTypeTooltipPreserved:h.unknownTypeHTML.includes('<title>Other: Other node'),
  unknownTypeNotUndefined:!h.unknownTypeHTML.includes('undefined'),
  oldButtonsGuardedWhilePending:!h.pendingNewLookup.oldButtonThrows,
  staleVisibleButtonsWhilePending:!!h.pendingNewLookup.trailHTML,
};
(async()=>{
  const r=structuredClone(maps.EGFR);
  r.groups.find(g=>g.rel==='ASSOCIATED_WITH').items[0].score=true;
  const p=run('explore("EGFR")');pending.shift().resolve({ok:true,json:async()=>r});
  try{await p;result.fullRenderBoolean={ok:true,html:el('o0').innerHTML};}
  catch(e){result.fullRenderBoolean={ok:false,error:String(e),html:el('o0').innerHTML,trail:JSON.parse(run('JSON.stringify(trail)'))};}
  fs.writeFileSync(OUT+'ui_regressions.json',JSON.stringify(result,null,2));
  console.log(JSON.stringify({precisionExamples:result.precision.slice(0,2),scoreTypeChecks:result.scoreTypeChecks,markupChecks:result.markupChecks,fullRenderBoolean:result.fullRenderBoolean},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
