const headers = {'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff'};
function reply(body, status=200) {return new Response(JSON.stringify(body), {status, headers});}
export async function handle(request, assets, upstream=fetch) {
  const url = new URL(request.url);
  if (request.method === 'GET' && url.pathname === '/') return new Response(assets.html, {headers:{'Content-Type':'text/html; charset=utf-8','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'"}});
  if (request.method === 'GET' && url.pathname === '/api/agents') return reply(assets.catalog.map(({prompt,sources,...rest})=>rest));
  if (request.method === 'GET' && url.pathname === '/download') return new Response(Uint8Array.from(atob(assets.zip), c=>c.charCodeAt(0)), {headers:{'Content-Type':'application/zip','Content-Disposition':'attachment; filename="portable-agents.zip"'}});
  if (request.method === 'GET' && url.pathname.startsWith('/prompt/')) {
    const agent = assets.catalog.find(a=>a.id === url.pathname.slice(8));
    return agent ? new Response(agent.prompt, {headers:{'Content-Type':'text/plain; charset=utf-8','Content-Disposition':`attachment; filename="${agent.id}.md"`}}) : reply({error:'顾问不存在'},404);
  }
  if (url.pathname !== '/api/chat' || request.method !== 'POST') return reply({error:'未找到入口'},404);
  if (request.headers.get('origin') && request.headers.get('origin') !== url.origin) return reply({error:'请求来源不匹配'},403);
  if (!request.headers.get('content-type')?.startsWith('application/json')) return reply({error:'需要 JSON 请求'},415);
  if (Number(request.headers.get('content-length')) > 100000) return reply({error:'对话过长，请开启新对话'},413);
  let input;
  try {
    const reader = request.body?.getReader();
    if (!reader) return reply({error:'请求为空'},400);
    let size=0; const chunks=[];
    while(true) {const {done,value}=await reader.read(); if(done) break; size+=value.length; if(size>100000) {await reader.cancel();return reply({error:'对话过长，请开启新对话'},413);} chunks.push(value);}
    const bytes=new Uint8Array(size); let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
    input=JSON.parse(new TextDecoder().decode(bytes));
  } catch {return reply({error:'请求格式错误'},400);}
  const agent=assets.catalog.find(a=>a.id===input.agent);
  const key=request.headers.get('authorization');
  if (!key || !/^Bearer [^\s]{10,512}$/.test(key)) return reply({error:'请填写有效的 API Key'},401);
  if (!agent || typeof input.model!=='string' || !/^[a-zA-Z0-9._:-]{1,100}$/.test(input.model) || !Array.isArray(input.messages) || input.messages.length<1 || input.messages.length>30 || input.messages.some(m=>!m || !['user','assistant'].includes(m.role) || typeof m.content!=='string' || m.content.length>16000) || input.messages.at(-1).role!=='user') return reply({error:'请检查顾问、模型及对话长度'},400);
  try {
    const response = await upstream('https://api.openai.com/v1/responses', {method:'POST', headers:{'Authorization':key,'Content-Type':'application/json'}, body:JSON.stringify({model:input.model,instructions:agent.prompt,input:input.messages,store:false,max_output_tokens:4000}), signal:AbortSignal.timeout(90000)});
    if(!response.ok) {if(response.body) await response.body.cancel(); return reply({error:response.status===401?'API Key 无效或已失效':response.status===429?'额度不足或请求过快，请检查 API 账户':response.status===404?'该账户无法使用此模型，请修改模型名':'模型服务暂时无法完成请求，请检查模型权限后重试'},502);}
    const data=await response.json();
    const text=(data.output??[]).filter(i=>i.type==='message').flatMap(i=>i.content??[]).filter(c=>c.type==='output_text').map(c=>c.text).join('\n');
    if(!text) return reply({error:'模型未返回文本，请重试或更换模型'},502);
    return reply({text, incomplete:data.status==='incomplete'});
  } catch {return reply({error:'连接模型服务失败或超时，请稍后重试'},502);}
}
