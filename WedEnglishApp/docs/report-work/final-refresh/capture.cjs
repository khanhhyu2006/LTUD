const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
const base='https://localhost:44317';
const dest=path.join(__dirname,'assets');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--disable-gpu']});
 const results=[];
 async function context(){return browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:900},deviceScaleFactor:1.5});}
 async function shot(page,name,url){
  try{
   const response=await page.goto(base+url,{waitUntil:'domcontentloaded',timeout:30000});
   await page.waitForTimeout(800); await page.screenshot({path:path.join(dest,name+'.png'),animations:'disabled'});
   const title=await page.title();
   const body=(await page.locator('body').innerText()).slice(0,1300);
   results.push({name,url,status:response.status(),title,body});
   console.log(name,response.status(),title);
  }catch(e){results.push({name,url,error:e.message});console.log(name,e.message.slice(0,200));}
 }
 async function login(page,email){
  await page.goto(base+'/Account/Login',{waitUntil:'domcontentloaded'});
  await page.locator('input[name="Email"]').fill(email);
  await page.locator('input[name="Password"]').fill('123456');
  await Promise.all([page.waitForURL(u=>!u.pathname.endsWith('/Login'),{timeout:15000}),page.locator('button[type="submit"]').click()]);
 }
 const guest=await context(),g=await guest.newPage();
 await shot(g,'ui-home','/');
 await shot(g,'ui-programs','/Program');
 const detail=await g.locator('a[href*="/Program/Detail/"]').first().getAttribute('href');
 await shot(g,'ui-detail',detail||'/Program/Detail/1');
 await shot(g,'ui-login','/Account/Login');
 await shot(g,'ui-register','/Account/Register');
 await shot(g,'ui-contact','/Home/Contact');
 const student=await context(),s=await student.newPage();
 for(const email of ['hocvien1@gmail.com']){
  try{await login(s,email);console.log('Student login succeeded');break;}catch(e){console.log('Student login failed',e.message);}
 }
 await shot(s,'ui-profile','/Student/Profile');
 await shot(s,'ui-myclasses','/Student/MyClasses');
 const receipt=await s.locator('a[href*="PrintReceipt"]').first().getAttribute('href').catch(()=>null);
 await shot(s,'ui-schedule','/Student/Schedule');
 await shot(s,'ui-payments','/Student/MyPayments');
 const receipt2=await s.locator('a[href*="PrintReceipt"]').first().getAttribute('href').catch(()=>null);
 if(receipt||receipt2)await shot(s,'ui-receipt',receipt||receipt2);
 await shot(s,'ui-test','/PlacementTest/BookTest');
 await s.goto(base+(detail||'/Program/Detail/1'),{waitUntil:'domcontentloaded'});
 const checkout=await s.locator('a[href*="Checkout"]').first().getAttribute('href').catch(()=>null);
 if(checkout)await shot(s,'ui-checkout',checkout);
 await shot(s,'ui-change-password','/Account/ChangePassword?authRole=Student');
 const teacher=await context(),t=await teacher.newPage();
 try{await login(t,'maitt@englishcenter.edu.vn');}catch(e){console.log('Teacher login failed',e.message);}
 for(const [name,url] of [
 ['ui-teacher-dashboard','/Teacher/TeacherDashboard'],['ui-teacher-classes','/Teacher/TeachingClass'],
 ['ui-teacher-schedule','/Teacher/TeachingClass/Schedule'],['ui-teacher-tests','/Teacher/TeacherTest'],
 ['ui-teacher-documents','/Teacher/Document'],['ui-teacher-feedback','/Teacher/Feedback'],['ui-teacher-salary','/Teacher/TeacherSalary']])await shot(t,name,url);
 const admin=await context(),a=await admin.newPage();
 await login(a,'admin@englishcenter.edu.vn');
 for(const [name,url] of [
 ['ui-admin-dashboard','/Admin/Dashboard'],['ui-admin-programs','/Admin/ProgramManager'],['ui-admin-classes','/Admin/ClassManager'],
 ['ui-admin-registrations','/Admin/RegistrationAdmin'],['ui-admin-payments','/Admin/PaymentAdmin'],
 ['ui-admin-students','/Admin/StudentManager'],['ui-admin-teachers','/Admin/TeacherManager'],
 ['ui-admin-tests','/Admin/PlacementTestAdmin'],['ui-admin-salaries','/Admin/SalaryAdmin'],
 ['ui-admin-consultations','/Admin/ConsultationManager'],['ui-admin-banners','/Admin/BannerManager'],['ui-admin-trash','/Admin/Trash']])await shot(a,name,url);
 fs.writeFileSync(path.join(__dirname,'captures.json'),JSON.stringify(results,null,2));
 await browser.close();
})();


