const {chromium}=require('playwright'),fs=require('fs');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const base='https://localhost:44317',rows=[],layout=[];
 const captures=JSON.parse(fs.readFileSync('docs/report-work/final-refresh/captures.json','utf8'));
 for(const [role,email] of [['Guest',null],['Student','hocvien1@gmail.com'],['Teacher','maitt@englishcenter.edu.vn'],['Admin','admin@englishcenter.edu.vn']]){
  const c=await b.newContext({ignoreHTTPSErrors:true}),p=await c.newPage();
  if(email){await p.goto(base+'/Account/Login',{waitUntil:'domcontentloaded'});await p.locator('[name=Email]').fill(email);await p.locator('[name=Password]').fill('123456');await Promise.all([p.waitForURL(u=>!u.pathname.endsWith('/Login')),p.locator('button[type=submit]').click()]);}
  let items=captures.filter(x=>role==='Admin'?x.url.startsWith('/Admin'):role==='Teacher'?x.url.startsWith('/Teacher'):role==='Guest'?['ui-home','ui-programs','ui-detail','ui-login','ui-register','ui-contact'].includes(x.name):['ui-profile','ui-myclasses','ui-schedule','ui-payments','ui-receipt','ui-test','ui-checkout','ui-change-password'].includes(x.name));
  if(role==='Admin')items.push({url:'/Admin/ClassManager/Create'},{url:'/Admin/PlacementTestAdmin/Create'},{url:'/Admin/PaymentAdmin/PrintReceipt/2'});
  for(const item of items){const r=await c.request.get(base+item.url);const html=await r.text();rows.push({role,url:item.url,status:r.status(),hasBrand:html.includes('NHK English times'),hasOldBrand:/HITC/i.test(html)});}
  const url=role==='Admin'?'/Admin/Dashboard':role==='Teacher'?'/Teacher/TeacherDashboard':'/';
  await p.goto(base+url,{waitUntil:'domcontentloaded'});
  await p.waitForLoadState('load');
  for(const width of [320,390,768,1440]){await p.setViewportSize({width,height:900});await p.waitForTimeout(400);const size=await p.evaluate(()=>({viewport:innerWidth,width:document.documentElement.scrollWidth}));layout.push({role,...size});if(width===390)await p.screenshot({path:`session-state/nhk-${role.toLowerCase()}-mobile.png`});}
  await c.close();
 }
 const failures=rows.filter(r=>r.status!==200||!r.hasBrand||r.hasOldBrand),overflow=layout.filter(x=>x.width>x.viewport+1);
 fs.writeFileSync('session-state/nhk-brand-checks.json',JSON.stringify({rows,layout,failures,overflow},null,2));console.log(JSON.stringify({pages:rows.length,failures,overflow},null,2));await b.close();
 if(failures.length||overflow.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
