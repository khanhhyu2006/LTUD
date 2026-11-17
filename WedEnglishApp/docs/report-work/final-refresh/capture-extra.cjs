const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const c=await b.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:900},deviceScaleFactor:1.5,locale:'vi-VN'}),p=await c.newPage();
 const base='https://localhost:44317',out=path.join(__dirname,'assets');
 async function go(url,name){const r=await p.goto(base+url,{waitUntil:'domcontentloaded'});await p.waitForTimeout(650);await p.screenshot({path:path.join(out,'ui-'+name+'.png'),animations:'disabled',timeout:15000});console.log(name,r.status());}
 async function login(email){await p.goto(base+'/Account/Login');await p.locator('[name=Email]').fill(email);await p.locator('[name=Password]').fill('123456');await Promise.all([p.waitForURL(u=>!u.pathname.endsWith('/Login')),p.locator('button[type=submit]').click()]);}
 await login('hocvien1@gmail.com');
 await go('/?authRole=Student','home-student');await p.locator('button[data-bs-toggle=dropdown]').first().click();await p.screenshot({path:path.join(out,'ui-home-student.png')});
 await p.goto(base+'/Program');
 if(true){
  await p.goto(base+'/Program');const links=await p.locator('a[href*="/Program/Detail/"]').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
  for(const u of links){await p.goto(base+u);const l=p.locator('a[href*="Checkout"]');if(await l.count()){await go(await l.first().getAttribute('href'),'checkout');if(await p.locator('[name=EarliestStartDate]').count())break;}}
 }else await p.screenshot({path:path.join(out,'ui-checkout.png')});
 const pay=await p.goto(base+'/Student/MyPayments'); const paymentLinks=await p.locator('a[href*="/Enrollment/Payment"]').evaluateAll(a=>a.map(x=>x.getAttribute('href')));console.log('payment links',paymentLinks);if(paymentLinks.length)await go(paymentLinks[0],'qr');
 await login('maitt@englishcenter.edu.vn');await p.goto(base+'/Teacher/TeachingClass');let l=p.locator('a[href*="/TeachingClass/Students/"]');if(await l.count())await go(await l.first().getAttribute('href'),'teacher-students');
 await login('admin@englishcenter.edu.vn');
 await go('/Admin/ClassManager/Create','class-create');
 await go('/Admin/ClassManager/Edit/1004','class-edit');
 await go('/Admin/PlacementTestAdmin/Create','exam-create');
 await p.goto(base+'/Admin/PlacementTestAdmin');l=p.locator('a[href*="/PlacementTestAdmin/Details/"]');if(await l.count())await go(await l.first().getAttribute('href'),'exam-details');
 await p.goto(base+'/Admin/ConsultationManager');l=p.getByRole('link',{name:'Mở và trả lời'});if(await l.count())await go(await l.first().getAttribute('href'),'consultation-thread');
 await b.close();
})();

