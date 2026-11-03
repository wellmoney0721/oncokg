const fs=require('fs'),vm=require('vm');
const OUT='audit_evidence_claims/m9/db_ui_cost/';
const code=fs.readFileSync('web/try.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(),pending=[];
function el(id){if(!elements.has(id))elements.set(id,{innerHTML:'',value:'',events:{},addEventListener(n,f){this.events[n]=f;}});return elements.get(id);}
const ctx=vm.createContext({document:{getElementById:el},console,fetch:async(path,init)=>new Promise(resolve=>pending.push({path,body:JSON.parse(init.body),resolve}))});
vm.runInContext(code,ctx);
const run=c=>vm.runInContext(c,ctx);
const fixture=JSON.parse(fs.readFileSync(OUT+'db_missing_sponsor_count.json','utf8'));
(async()=>{
  const results=[];
  for(const test of fixture.HEAD){
    for(const request of test.requests){
      const p=run(`explore(${JSON.stringify(request.input)})`);
      pending.shift().resolve({ok:request.status===200,json:async()=>request.body});
      await p;
      const details=request.matched_edge_items.map(({group,item})=>{
        ctx.item=item;ctx.rel=group.rel;
        return {id:item.id,edge_id:item.edge_id,weight:item.weight,detail:run('itemDetail(item,rel)')};
      });
      results.push({stored_props:test.stored_props,input:request.input,status:request.status,details,
        displayedZero:el('o0').innerHTML.includes('책임 주관한 임상 0건'),html:el('o0').innerHTML});
    }
  }
  fs.writeFileSync(OUT+'ui_missing_sponsor_count.json',JSON.stringify({edge_id:fixture.edge_id,results},null,2));
  console.log(JSON.stringify(results.map(({html,...record})=>record),null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
