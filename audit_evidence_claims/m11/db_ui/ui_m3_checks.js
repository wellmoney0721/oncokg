const fs=require('fs'),vm=require('vm'),assert=require('assert');
const OUT='audit_evidence_claims/m11/db_ui/';
const page=fs.readFileSync('web/try.html','utf8');
const code=page.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(),pending=[];
function el(id){if(!elements.has(id))elements.set(id,{innerHTML:'',value:'',events:{},addEventListener(n,f){this.events[n]=f;},requestSubmit(){return this.events.submit({preventDefault(){}});}});return elements.get(id);}
const ctx=vm.createContext({console,document:{getElementById:el},fetch:async(path,init)=>new Promise((resolve,reject)=>pending.push({path,body:JSON.parse(init.body),resolve,reject}))});
vm.runInContext(code,ctx);
const run=c=>vm.runInContext(c,ctx),tick=()=>new Promise(setImmediate);
const maps=JSON.parse(fs.readFileSync(OUT+'ui_real_maps.json','utf8'));
const demos=JSON.parse(fs.readFileSync(OUT+'ui_demos_responses.json','utf8'));
const out={demoClicks:[],mapClicks:[],renderErrors:[],sponsorControls:[],booleanControls:[],browser:{performed:false,scope:'Node VM only; no current browser claim'}};
function click(id,dataset){el(id).events.click({target:{closest:()=>({dataset})}});}
async function respond(body,ok=true){const p=pending.shift();assert(p,'request was dispatched');p.resolve({ok,json:async()=>body});await tick();return p;}
function snap(){return {html:el('o0').innerHTML,trail:JSON.parse(run('JSON.stringify(trail)')),trailHTML:el('trail0').innerHTML};}
async function root(name){click('ex0',{t:name});await respond(maps[name]||{refused:name,why:'distinct_product'});}
(async()=>{
  for(const test of demos){
    const index=Number(test.kind.slice(-1));
    click('ex'+index,index<3?{t:test.request.text}:{i:String(test.index)});
    const request=await respond(test.response);
    if(index===4){assert.strictEqual(request.body.text,test.request.text);assert.deepStrictEqual(JSON.parse(request.body.answer),JSON.parse(test.request.answer));}
    else assert.deepStrictEqual(request.body,test.request);
    const html=el('o'+index).innerHTML;
    assert(!html.includes('class="err"'));
    out.demoClicks.push({kind:test.kind,index:test.index,request:request.body,path:request.path,hasError:false});
  }
  for(const name of ['osimertinib','EGFR','KRAS','AstraZeneca','NCT00200395','Mvasi']){
    await root(name);const state=snap();
    assert(!state.html.includes('그리는 중'));
    assert(!state.html.includes('class="err"'));
    if(name==='Mvasi')assert.strictEqual(state.trail.length,0);
    else assert.strictEqual(state.trail.length,1);
    out.mapClicks.push({name,trail:state.trail,hasRefusal:state.html.includes('연결하지 않음')});
  }
  // Every map entry point uses the guarded wrapper. Malformed phases was a
  // realistic render exception before the wrapper, not a fake throwing getter.
  const broken=structuredClone(maps.NCT00200395);
  broken.center.props.phases='PHASE2';
  for(const route of ['form','node','trail','example']){
    await root('osimertinib');
    click('o0',{id:'ENSG00000146648'});await respond(maps.EGFR);
    if(route==='form'){el('t0').value='NCT00200395';el('f0').requestSubmit();}
    if(route==='node')click('o0',{id:'NCT00200395'});
    if(route==='trail')click('trail0',{back:'0'});
    if(route==='example')click('ex0',{t:'NCT00200395'});
    await respond(broken);const state=snap();
    assert(state.html.includes('그리지 못했습니다'));
    assert(!state.html.includes('그리는 중'));
    assert.deepStrictEqual(state.trail,[]);
    assert.strictEqual(state.trailHTML,'');
    out.renderErrors.push({route,...state});
    await root('KRAS');assert(snap().html.includes('KRAS'));
  }
  // A stale malformed response is discarded before rendering.
  click('ex0',{t:'NCT00200395'});click('ex0',{t:'KRAS'});
  const old=pending.shift(),latest=pending.shift();
  latest.resolve({ok:true,json:async()=>maps.KRAS});await tick();
  old.resolve({ok:true,json:async()=>broken});await tick();
  out.staleMalformed=snap();assert(out.staleMalformed.html.includes('KRAS'));assert(!out.staleMalformed.html.includes('그리지 못했습니다'));
  // Empty submissions do not issue a request or throw; the displayed map stays.
  const before=snap();el('t0').value=' \n\t ';el('f0').requestSubmit();await tick();
  assert.strictEqual(pending.length,0);assert.deepStrictEqual(snap(),before);
  out.blankSubmit={requestCount:0,preservedPreviousView:true};
  for(const n of [null,0,1,14]){ctx.it={type:'Company',weight:123,evidence_trials:n,sponsor_class:'NIH'};const detail=run('itemDetail(it,"SPONSORS_TRIAL_OF")');out.sponsorControls.push({evidence_trials:n,weight:123,detail});assert(!detail.includes('123'));if(n===null)assert(detail.includes('기록 없음'));else assert(detail.includes(`${n}건`));}
  for(const n of [true,false]){const r=structuredClone(maps.EGFR);r.groups.find(g=>g.rel==='ASSOCIATED_WITH').items[0].score=n;click('ex0',{t:'EGFR'});await respond(r);const state=snap();assert(!state.html.includes('class="err"'));out.booleanControls.push({score:n,rendered:true});}
  fs.writeFileSync(OUT+'ui_m3_checks.json',JSON.stringify(out,null,2));
  console.log(JSON.stringify({demoClicks:out.demoClicks.length,mapClicks:out.mapClicks.length,renderErrorsHandled:out.renderErrors.length,staleMalformedIgnored:true,blankSubmit:out.blankSubmit,controls:out.sponsorControls,booleanControls:out.booleanControls}));
})().catch(e=>{console.error(e);process.exitCode=1;});
