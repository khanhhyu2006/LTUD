const fs=require('fs'),path=require('path'),sharp=require('sharp');
const out=path.join(__dirname,'chapter3-assets');fs.mkdirSync(out,{recursive:true});
const schema=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../session-state/report-live-schema.json'),'utf8'));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
const txt=(x,y,s,size=23,anchor='start')=>`<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${esc(s)}</text>`;
const start=(w,h)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#3f5669"/></marker></defs><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial,'Segoe UI',sans-serif;fill:#172b3a}.line{fill:none;stroke:#3f5669;stroke-width:2;marker-end:url(#arr)}.dash{stroke-dasharray:8 6}rect.box{fill:white;stroke:#3f5669;stroke-width:2}</style>`;
async function save(name,s){fs.writeFileSync(path.join(out,name+'.svg'),s);await sharp(Buffer.from(s),{density:145}).png().toFile(path.join(out,name+'.png'));}
const box=(x,y,w,h,lines)=>`<rect class="box" x="${x}" y="${y}" width="${w}" height="${h}" rx="8"/>`+lines.map((v,i)=>txt(x+w/2,y+h/2+(i-(lines.length-1)/2)*30+8,v,25,'middle')).join('');
async function erd(){
 const grid=[['UserAccounts','Students','Teachers','Banners'],['Consultations','Programs','Classes','TeacherSalaries'],['ConsultationMessages','Registrations','ClassSchedules','ClassDocuments'],['PlacementTests','Payments','ExamSessions','CourseFeedbacks']];
 const pos={};let y=100;for(const row of grid){let max=0;row.forEach((t,i)=>{let fields=schema.columns.filter(c=>c.table===t);const h=65+fields.length*31;pos[t]={x:45+i*610,y,w:530,h,fields};max=Math.max(max,h);});y+=max+125;}
 let s=start(2450,y+10)+txt(1225,46,'NHK English times — Sơ đồ quan hệ 16 bảng nghiệp vụ',35,'middle');
 const edges=Object.values(Object.groupBy(schema.foreign_keys,k=>k.name));
 edges.forEach((parts,i)=>{const f=parts[0],a=pos[f.target_table],b=pos[f.source_table];if(!a||!b)return;
  const ai=a.fields.findIndex(c=>c.name===f.target_column),bi=b.fields.findIndex(c=>c.name===f.source_column),right=b.x>=a.x;
  const ax=a.x+(right?a.w:0),ay=a.y+61+ai*31,bx=b.x+(right?0:b.w),by=b.y+61+bi*31;
  const lane=right?Math.min(ax+35+(i%4)*10,bx-15):Math.max(ax-35-(i%4)*10,bx+15);
  let d;if(a.x===b.x){const xx=a.x+a.w+25+(i%4)*12;d=`M${a.x+a.w} ${ay}H${xx}V${by}H${b.x+b.w}`;}else d=`M${ax} ${ay}H${lane}V${by}H${bx}`;
  s+=`<path d="${d}" fill="none" stroke="#54a2ce" stroke-width="2" marker-end="url(#arr)"/>`;
 });
 for(const [name,b]of Object.entries(pos)){
  s+=`<rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" fill="white" stroke="#289bd0" stroke-width="2"/><rect x="${b.x}" y="${b.y}" width="${b.w}" height="43" fill="#fff7ce" stroke="#289bd0" stroke-width="1"/>`+txt(b.x+12,b.y+30,name,27);
  for(const [i,c]of b.fields.entries()){const fk=schema.foreign_keys.some(f=>f.source_table===name&&f.source_column===c.name);s+=txt(b.x+10,b.y+68+i*31,`${c.is_pk?'PK':fk?'FK':'  '}  ${c.name}${c.is_nullable?' ?':''}`,23);}
 }
 s+=txt(50,y-15,'PK: khóa chính   FK: khóa ngoại vật lý   ?: cho phép NULL   Đường nối: từ khóa được tham chiếu đến khóa ngoại',24);
 await save('erd-full',s+'</svg>');
}
async function activity(){
 const W=1600,H=1900;let s=start(W,H)+txt(800,42,'Biểu đồ hoạt động quy trình đăng ký khóa học',34,'middle');
 const lanes=[['Học viên',0],['Hệ thống',530],['Admin',1060]];
 for(const [name,x]of lanes)s+=`<rect x="${x+15}" y="65" width="520" height="1785" fill="none" stroke="#b1bcc6"/>`+txt(x+275,105,name,29,'middle');
 const node=(x,y,w,h,t)=>s+=box(x,y,w,h,t);const arrow=(d,label,x,y)=>{s+=`<path class="line" d="${d}"/>`;if(label)s+=txt(x,y,label,23);};
 s+='<circle cx="275" cy="150" r="13" fill="#172b3a"/>';
 node(75,205,400,88,['Tra cứu, chọn khóa học','và đăng nhập tài khoản']);arrow('M275 163V205');
 node(75,350,400,110,['Nhập ngày có thể bắt đầu','buổi, 246 / 357, ghi chú','và cách đóng học phí']);arrow('M275 293V350');
 node(605,350,390,110,['Kiểm tra dữ liệu đầu vào','và đơn đăng ký trùng']);arrow('M475 405H605');
 s+='<path d="M800 520L905 580L800 640L695 580Z" fill="white" stroke="#3f5669" stroke-width="2"/>'+txt(800,588,'Hợp lệ?',25,'middle');arrow('M800 460V520');
 node(85,535,380,88,['Nhận lỗi và sửa biểu mẫu']);arrow('M695 580H465','Không',510,565);arrow('M275 535V460');
 node(595,705,410,135,['Mở transaction','Lưu Registration Pending','ClassId = NULL','và Payment Pending']);arrow('M800 640V705','Có',817,680);
 node(595,900,410,95,['Commit và trả trang','hướng dẫn đóng học phí']);arrow('M800 840V900');
 node(1110,1070,405,105,['Nhận đơn và nguyện vọng','Tìm lớp cùng khóa học']);arrow('M1005 950H1040V1120H1110');
 node(1110,1230,405,115,['Kiểm tra ngày khai giảng','sĩ số và lịch trùng thực tế']);arrow('M1310 1175V1230');
 s+='<path d="M1310 1395L1435 1455L1310 1515L1185 1455Z" fill="white" stroke="#3f5669" stroke-width="2"/>'+txt(1310,1463,'Phù hợp?',25,'middle');arrow('M1310 1345V1395');
 arrow('M1435 1455H1550V1120H1515','Không: giữ chờ',1370,1380);
 node(1100,1580,420,95,['Gán ClassId và Confirmed','Công bố lớp, lịch học']);arrow('M1310 1515V1580','Có',1327,1550);
 node(85,1580,380,95,['Xem lớp và thời khóa biểu','trong tài khoản']);arrow('M1100 1625H465');
 s+='<circle cx="275" cy="1760" r="19" fill="none" stroke="#172b3a" stroke-width="3"/><circle cx="275" cy="1760" r="12" fill="#172b3a"/>';arrow('M275 1675V1740');
 s+=txt(800,1880,'Xác nhận thu học phí được xử lý riêng; buổi và nhóm thứ là nguyện vọng để Admin cân nhắc.',24,'middle');
 await save('activity-enrollment',s+'</svg>');
}
async function sequence(){
 let s=start(1800,1670)+txt(900,40,'Biểu đồ tuần tự đối soát và xác nhận học phí',34,'middle');
 const xs=[130,440,850,1220,1640],names=[['Học viên'],['Razor View'],['Controllers'],['EF Core','SQL Server'],['Admin']];
 xs.forEach((x,i)=>{s+=box(x-115,80,230,76,names[i]);s+=`<path d="M${x} 156V1570" fill="none" stroke="#82909a" stroke-dasharray="9 7"/>`;});
 function msg(a,b,y,label,dash=false){s+=`<path class="line ${dash?'dash':''}" d="M${xs[a]} ${y}H${xs[b]}"/>`+txt((xs[a]+xs[b])/2,y-14,label,22,'middle');}
 msg(0,1,220,'1. Gửi đăng ký + cách đóng học phí');msg(1,2,305,'2. POST Enrollment/Confirm');
 msg(2,3,390,'3. Transaction: Registration + Payment Pending');msg(3,2,475,'4. Commit; RegistrationId và mã HPREG',true);
 msg(2,1,560,'5. Redirect Enrollment/Payment',true);msg(1,0,645,'6. Hiển thị QR / hướng dẫn nộp tiền',true);
 s+=`<rect x="40" y="705" width="1710" height="130" fill="#f4f6f8" stroke="#82909a"/>`+txt(895,755,'Học viên thanh toán ngoài hệ thống bằng ứng dụng ngân hàng hoặc tại quầy.',25,'middle')+txt(895,795,'Không có callback ngân hàng tự động; hiển thị QR không làm Payment chuyển Paid.',25,'middle');
 msg(4,2,900,'7. Mở danh sách và kiểm tra chứng từ');msg(2,3,985,'8. Đọc Payment và Registration');msg(3,2,1070,'9. Trả thông tin học phí',true);
 msg(4,2,1155,'10. POST PaymentAdmin/ConfirmPayment');msg(2,3,1240,'11. Cập nhật Status = Paid; SaveChanges');msg(3,2,1325,'12. Lưu thành công',true);
 msg(2,4,1410,'13. Thông báo đã xác nhận thu',true);msg(0,2,1495,'14. Xem lịch sử và in biên lai theo quyền sở hữu');
 s+=txt(900,1630,'Registration Pending / Confirmed và ClassId không tự thay đổi khi xác nhận học phí.',25,'middle');await save('sequence-payment',s+'</svg>');
}
async function architecture(){
 let s=start(1300,1170)+txt(650,45,'Kiến trúc phân tầng ứng dụng ASP.NET Core MVC',34,'middle');
 const boxes=[['Trình bày', ['Razor Views · Bootstrap · JavaScript','Views, Areas/*/Views, wwwroot']],['Điều phối yêu cầu',['Controllers · ViewModels','Routing, kiểm tra dữ liệu, cookie và phân quyền']],['Nghiệp vụ',['Services','Xếp lớp, lập lịch, phòng thi, tư vấn, tệp tải lên']],['Truy cập và lưu trữ dữ liệu',['ApplicationDbContext · Models · EF Core','SQL Server LocalDB · Data/Sql · Migrations']]];
 boxes.forEach(([title,lines],i)=>{const y=100+i*240;s+=`<rect x="160" y="${y}" width="980" height="155" fill="white" stroke="#3f5669" stroke-width="2"/><rect x="160" y="${y}" width="980" height="42" fill="#edf2f5"/>`+txt(650,y+31,title,28,'middle');lines.forEach((v,j)=>s+=txt(650,y+82+j*37,v,26,'middle'));if(i<3)s+=`<path class="line" d="M650 ${y+155}V${y+240}"/>`;});
 s+=txt(650,1120,'Một ứng dụng triển khai chung; Controllers có thể truy vấn DbContext trực tiếp.',26,'middle');await save('architecture',s+'</svg>');
}
(async()=>{await erd();await activity();await sequence();await architecture();console.log('Created ERD, activity, sequence and architecture from the project schema and code.');})();
