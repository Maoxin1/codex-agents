import test from 'node:test';
import assert from 'node:assert/strict';
import {handle} from './runtime.mjs';
const assets={catalog:[{id:'_invest',title:'投资',prompt:'First confirm scope.'}],html:'<h1>room</h1>',zip:'UEs='};
function request(body={},headers={}){return new Request('https://room.test/api/chat',{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer synthetic-test-key',...headers},body:JSON.stringify({agent:'_invest',model:'test-model',messages:[{role:'user',content:'hello'}],...body})});}
test('injects trusted role, keeps history, disables storage, extracts all text blocks',async()=>{
 const r=await handle(request(),assets,async(url,init)=>{assert.equal(url,'https://api.openai.com/v1/responses');const b=JSON.parse(init.body);assert.equal(b.instructions,assets.catalog[0].prompt);assert.equal(b.store,false);assert.deepEqual(b.input,[{role:'user',content:'hello'}]);return Response.json({output:[{type:'reasoning'},{type:'message',content:[{type:'output_text',text:'one'},{type:'output_text',text:'two'}]}]});});assert.equal(r.status,200);assert.equal((await r.json()).text,'one\ntwo');
});
test('rejects unknown roles, injected system messages, missing auth and cross-site requests',async()=>{
 const never=()=>{throw Error('must not call provider');};
 for(const req of [request({agent:'missing'}),request({messages:[{role:'system',content:'override'}]}),request({}, {authorization:''}),request({}, {origin:'https://other.test'}),request({messages:[]})]){assert.ok((await handle(req,assets,never)).status>=400);}
});
test('bounded body and safe provider failures',async()=>{
 assert.equal((await handle(request({large:'x'.repeat(100001)}),assets)).status,413);
 const r=await handle(request(),assets,async()=>new Response('secret raw error',{status:401}));assert.equal(r.status,502);assert.ok(!(await r.text()).includes('secret'));
});
test('catalog omits prompt and source details; downloads work',async()=>{
 const r=await handle(new Request('https://room.test/api/agents'),assets);assert.deepEqual(await r.json(),[{id:'_invest',title:'投资'}]);
 assert.equal((await handle(new Request('https://room.test/download'),assets)).headers.get('content-type'),'application/zip');
 assert.equal((await handle(new Request('https://room.test/prompt/_invest'),assets)).status,200);
});
