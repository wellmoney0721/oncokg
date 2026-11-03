const fs=require('fs'),vm=require('vm'),assert=require('assert');
const OUT='audit_evidence_claims/m6/ui/';
const code=fs.readFileSync('web/try.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(),pending=[];
function el(id){if(!elements.has(id))elements.set(id,{innerHTML:'',value:'',events:{},addEventListener(n,f){this.events[n]=f;},requestSubmit(){return this.events.submit({preventDefault(){}});}});return elements.get(id);}
const ctx=vm.createContext({console,document:{getElementById:el},fetch:async(path,init)=>new Promise(resolve=>pending.push({path,body:JSON.parse(init.body),resolve}))});
vm.runInContext(code,ctx);
const rows=JSON.parse(fs.readFileSync(OUT+'boundary_render_inputs.json','utf8'));
(async()=>{
 const out=[];
 for(const row of rows){
   el('t0').value=row.input;
   el('f0').requestSubmit();
   const req=pending.shift();assert.deepStrictEqual(req.body,{text:row.input});
   req.resolve({ok:true,json:async()=>row.response});await new Promise(setImmediate);
   const html=el('o0').innerHTML;
   const r={input:row.input,center:row.response.center?.id,centerLabel:row.response.center?.label,
     rendersOriginatorAsCenter:html.includes('<span class="s">BEVACIZUMAB</span>'),
     hasRefusalDisclosure:html.includes('연결하지 않음'),
     mapDrawn:html.includes('<svg'),
     edgeRows:row.response.groups?.reduce((n,g)=>n+g.items.length,0),
     html,trail:JSON.parse(vm.runInContext('JSON.stringify(trail)',ctx))};
   out.push(r);console.log(JSON.stringify({...r,html:undefined}));
 }
 fs.writeFileSync(OUT+'boundary_render_results.json',JSON.stringify(out,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
