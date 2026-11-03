// Execute the page's real form handler with a minimal DOM and real API JSON responses.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const out = __dirname;
const root = path.resolve(out, '../../..');
const html = fs.readFileSync(path.join(root, 'web/try.html'), 'utf8');
const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const data = JSON.parse(fs.readFileSync(path.join(out,'modelui_attack_api_fixtures.json'),'utf8'));
async function run(row) {
  const els = new Map();
  const document = { getElementById(id) {
    if (!els.has(id)) els.set(id,{value:'',innerHTML:'',listeners:{},addEventListener(name,fn){this.listeners[name]=fn;}});
    return els.get(id);
  }};
  const sandbox = {document,fetch:async () => ({ok:row.http_status===200,status:row.http_status,json:async()=>JSON.parse(row.response_raw)})};
  vm.createContext(sandbox);vm.runInContext(source,sandbox);
  const request=JSON.parse(row.request);
  document.getElementById('q4').value=request.text;
  document.getElementById('a4').value=request.answer;
  await document.getElementById('f4').listeners.submit({preventDefault(){}});
  const output=document.getElementById('o4').innerHTML;
  return {case:row.case,html:output,has_raw_injected_element:/<(?:script|img)\b/i.test(output),has_escaped_injected_element:/&lt;(?:script|img)\b/i.test(output),marker_executed:sandbox.MODEL_INJECTED||false};
}
(async()=>{
const rows=[];
for (const row of data) rows.push(await run(row));
fs.writeFileSync(path.join(out,'modelui_attack_page_results.json'),JSON.stringify(rows,null,2));
for (const row of rows) console.log(JSON.stringify({...row,html:row.html.slice(0,170)}));
})();
