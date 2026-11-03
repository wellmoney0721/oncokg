// Actual page form callbacks fed the independently captured original-CLI HTTP bodies.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const OUT='audit_evidence_claims/m19/db_ui/';
const source='audit_evidence_claims/m19/root_checks/independent_m19_http.json';
const page=fs.readFileSync('web/try.html','utf8');
const code=page.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(),pending=[];
function el(id){if(!elements.has(id))elements.set(id,{innerHTML:'',value:'',events:{},addEventListener(n,f){this.events[n]=f;}});return elements.get(id);}
const ctx=vm.createContext({console,document:{getElementById:el},fetch:async(path,init)=>new Promise((resolve,reject)=>pending.push({path,body:JSON.parse(init.body),resolve,reject}))});
vm.runInContext(code,ctx);
const rows=JSON.parse(fs.readFileSync(source,'utf8')).filter(x=>x.endpoint==='explore');
const tick=()=>new Promise(setImmediate);
const out={http_source:source,method:'Actual page form submission callback and exploreSafe, captured HTTP bodies via controlled fetch; Node VM, not a browser',rows:[]};
(async()=>{
 for(const row of rows){
  el('t0').value=row.input;
  el('f0').events.submit({preventDefault(){}});
  const request=pending.shift();assert(request);
  assert.strictEqual(request.path,'/api/explore');
  assert.deepStrictEqual(request.body,{text:row.input});
  request.resolve({ok:row.status===200,json:async()=>row.response});
  await tick();
  const html=el('o0').innerHTML;
  const trail=JSON.parse(vm.runInContext('JSON.stringify(trail)',ctx));
  const rec={input:row.input,http_status:row.status,center:row.response.center?.id||null,center_label:row.response.center?.label||null,
    has_refusal:html.includes('연결하지 않음'),has_svg:html.includes('<svg '),has_render_error:html.includes('그리지 못했습니다'),trail,html};
  assert(!rec.has_render_error);
  if(row.response.refused){assert(rec.has_refusal);assert(!rec.has_svg);assert.strictEqual(trail.length,0);}
  if(row.response.center){assert(rec.has_svg);assert.strictEqual(trail[0][0],row.response.center.id);}
  out.rows.push(rec);
 }
 fs.writeFileSync(OUT+'ui_m19_http.json',JSON.stringify(out,null,2));
 console.log(JSON.stringify(out.rows.map(({html,...rest})=>rest),null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
