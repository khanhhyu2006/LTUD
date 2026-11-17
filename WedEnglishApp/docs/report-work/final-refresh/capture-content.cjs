const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const c=await b.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:1100},deviceScaleFactor:1.5}),p=await c.newPage(),base='https://localhost:44317';
async function login(email){await p.goto(base+'/Account/Login');await p.locator('[name=Email]').fill(email);await p.locator('[name=Password]').fill('123456');await Promise.all([p.waitForURL(u=>!u.pathname.endsWith('/Login')),p.locator('button[type=submit]').click()]);}
const items=JSON.parse(fs.readFileSync(path.join(__dirname,'captures.json'),'utf8')).filter(x=>/^ui-(teacher|admin)-/.test(x.name)&&!x.name.endsWith('dashboard'));
items.push({name:'ui-class-create',url:'/Admin/ClassManager/Create'},{name:'ui-class-edit',url:'/Admin/ClassManager/Edit/1004'},{name:'ui-exam-create',url:'/Admin/PlacementTestAdmin/Create'});
let role='';for(const item of items){const r=item.url.startsWith('/Teacher')?'Teacher':'Admin';if(role!==r){await login(r==='Teacher'?'maitt@englishcenter.edu.vn':'admin@englishcenter.edu.vn');role=r;}
await p.goto(base+item.url,{waitUntil:'domcontentloaded'});await p.waitForTimeout(400);
const body=p.locator('.portal-body');const box=await body.evaluate(el=>{const rect=el.getBoundingClientRect();const kids=[...el.children].filter(x=>x.tagName!=='SCRIPT'&&x.getBoundingClientRect().height>0);const bottom=Math.max(rect.y+220,...kids.map(x=>x.getBoundingClientRect().bottom));return{x:rect.x+10,y:rect.y+8,width:rect.width-20,height:Math.min(650,bottom-rect.y+16)};});
await p.screenshot({path:path.join(__dirname,'assets',item.name+'.png'),clip:box,animations:'disabled'});console.log(item.name,Math.round(box.height));
}
await p.goto(base+'/Admin/ConsultationManager');let l=p.getByRole('link',{name:'Mở và trả lời'});await p.goto(base+await l.first().getAttribute('href'));const box=await p.locator('.consultation-conversation').boundingBox().catch(()=>null);
// Keep the existing full conversation screenshot if no dedicated container exists.
await b.close();})();
