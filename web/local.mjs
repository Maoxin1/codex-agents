import {createServer} from 'node:http';
import {readFileSync} from 'node:fs';
const {default:worker}=await import('./dist/server/index.js');
createServer(async(req,res)=>{
  try {
    const body=[]; let size=0;for await(const chunk of req){size+=chunk.length;if(size>100000){res.writeHead(413);res.end();return;}body.push(chunk);}
    const request=new Request(`http://localhost:8787${req.url}`,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:Buffer.concat(body)}:{})});
    const response=await worker.fetch(request);res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));
  }catch{res.writeHead(500);res.end('Request failed');}
}).listen(8787,'127.0.0.1',()=>console.log('Local: http://localhost:8787'));
