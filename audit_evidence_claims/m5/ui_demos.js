const fs = require('fs'), vm = require('vm');
const OUT='audit_evidence_claims/m5/';
const code=fs.readFileSync('web/try.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(), pending=[];
function el(id){if(!elements.has(id))elements.set(id,{innerHTML:'',value:'',events:{},addEventListener(n,f){this.events[n]=f;},requestSubmit(){return this.events.submit({preventDefault(){}});}});return elements.get(id);}
const ctx=vm.createContext({console,document:{getElementById:el},fetch:async(path,init)=>new Promise(resolve=>pending.push({path,body:JSON.parse(init.body),resolve}))});
vm.runInContext(code,ctx);
const run=c=>vm.runInContext(c,ctx);
const inputs=JSON.parse(run('JSON.stringify({EX1,EX2,EX3,EX4})'));
fs.writeFileSync(OUT+'ui_demos_inputs.json',JSON.stringify(inputs,null,2));
if(process.argv[2]==='export')process.exit(0);
const responses=JSON.parse(fs.readFileSync(OUT+'ui_demos_responses.json','utf8'));
(async()=>{
  const results=[];
  for(const test of responses){
    const ids=test.kind==='EX1'?['t1']:test.kind==='EX2'?['t2']:test.kind==='EX3'?['q3','a3']:['q4','a4'];
    el(ids[0]).value=test.request.text;
    if(ids[1])el(ids[1]).value=test.request.answer;
    const f=test.kind==='EX1'?'f1':test.kind==='EX2'?'f2':test.kind==='EX3'?'f3':'f4';
    const promise=el(f).requestSubmit();
    const q=pending.shift();
    q.resolve({ok:!test.error,json:async()=>test.response||{error:test.error}});
    await promise;
    const html=el('o'+f.slice(1)).innerHTML;
    results.push({kind:test.kind,index:test.index,input:test.request,requested:q.body,path:q.path,hasUiError:html.includes('class="err"'),html});
  }
  fs.writeFileSync(OUT+'ui_demos_results.json',JSON.stringify(results,null,2));
  console.log(JSON.stringify({total:results.length,byKind:Object.fromEntries(Object.keys(inputs).map(k=>[k,results.filter(r=>r.kind===k).length])),errors:results.filter(r=>r.hasUiError).map(r=>({kind:r.kind,index:r.index,input:r.input}))},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
