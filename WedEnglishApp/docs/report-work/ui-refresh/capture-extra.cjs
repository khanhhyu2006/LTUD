const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});let c=await b.newContext({viewport:{width:1280,height:820},deviceScaleFactor:1.5}),p=await c.newPage();const base='http://127.0.0.1:5270';
async function login(email){await p.goto(base+'/Account/Login');await p.locator('[name=Email]').fill(email);await p.locator('[name=Password]').fill('123456');await Promise.all([p.waitForURL(u=>!u.pathname.endsWith('/Login')),p.locator('button[type=submit]').click()]);}
const checks=[];
await p.goto(base+'/Admin/Dashboard');checks.push({name:'Guest Admin access',url:p.url(),result:p.url().includes('/Account/Login')?'Redirect login':'Unexpected'});
await login('hocvien1@gmail.com');await p.goto(base+'/Admin/Dashboard');checks.push({name:'Student Admin access',url:p.url(),result:p.url().includes('/Account/Login')?'Redirect Admin login':'Unexpected'});
const captures=JSON.parse(fs.readFileSync(path.join(__dirname,'captures.json'),'utf8'));const checkout=captures.find(x=>x.name==='ui-checkout');if(checkout){await p.goto(base+checkout.url);await p.locator('#payVietQR').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(__dirname,'assets/ui-qr.png')});}
await login('maitt@englishcenter.edu.vn');await p.goto(base+'/Teacher/TeachingClass');let students=p.locator('a[href*="/TeachingClass/Students/"]');if(await students.count()){await p.goto(base+await students.first().getAttribute('href'));await p.screenshot({path:path.join(__dirname,'assets/ui-teacher-students.png')});}
fs.writeFileSync(path.join(__dirname,'read-checks.json'),JSON.stringify(checks,null,2));console.log(checks);await b.close();})();
