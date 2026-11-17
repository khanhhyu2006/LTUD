// Overview follows the supplied UML reference: four external actors, two columns,
// shared authentication in the center and only mandatory subflows as includes.
const fs=require('fs'),path=require('path'),sharp=require('sharp');
const out=__dirname,W=1900,H=2610;
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const nodes=[];const links=[];const includes=[];
function add(id,x,y,lines,role,rx=300){nodes.push({id,x,y,lines,role,rx,ry:lines.length===3?54:47});}
const lx=580,rx=1320;
[
 ['g1',200,['Tra cứu, tìm kiếm','và lọc khóa học']],
 ['g2',400,['Xem chi tiết, học phí','và lớp học tham khảo']],
 ['g3',600,['Đăng ký tài khoản học viên']],
 ['g4',800,['Gửi và theo dõi tư vấn','Trao đổi riêng với Admin']]
].forEach(([id,y,t])=>add(id,lx,y,t,'Guest'));
[
 ['t0',150,['Cập nhật hồ sơ và ảnh']],
 ['t1',250,['Xem lớp, danh sách học viên']],
 ['t2',350,['Xem lịch dạy và lịch thi']],
 ['t3',450,['Quản lý tài liệu lớp học']],
 ['t4',550,['Chấm bài kiểm tra xếp lớp']],
 ['t5',650,['Nhập điểm và đề xuất cấp độ']],
 ['t6',750,['Xem phản hồi học viên']],
 ['t7',850,['Xem bảng lương cá nhân']]
].forEach(([id,y,t])=>add(id,rx,y,t,'Teacher'));
[
 ['s1',1220,['Cập nhật hồ sơ và ảnh']],
 ['s2',1360,['Đăng ký khóa học']],
 ['s3',1500,['Gửi nguyện vọng lịch học','Ngày bắt đầu, buổi, 246 / 357']],
 ['s4',1640,['Theo dõi đơn đăng ký','và lớp được Admin xếp']],
 ['s5',1780,['Xem hướng dẫn học phí','Lịch sử và in biên lai']],
 ['s6',1920,['Đăng ký kiểm tra xếp lớp']],
 ['s7',2060,['Xem thời khóa biểu','Lịch thi, điểm và cấp độ']],
 ['s8',2200,['Đánh giá lớp học']],
 ['s9',2340,['Trao đổi tư vấn với Admin','và xem lịch sử hội thoại']]
].forEach(([id,y,t])=>add(id,lx,y,t,'Student'));
[
 ['a1',1140,['Quản lý chương trình đào tạo']],
 ['a2',1260,['Tạo và chỉnh sửa lớp học']],
 ['a3',1380,['Thiết lập lịch tuần','246 / 357 và giờ học']],
 ['a0',1440,['Phân công giáo viên giảng dạy']],
 ['a4',1500,['Xếp và chuyển lớp học viên']],
 ['a5',1620,['Kiểm tra điều kiện xếp lớp','Khóa, ngày, chỗ và lịch trùng']],
 ['a6',1740,['Tạo phòng thi, xếp thí sinh','và phân công người chấm']],
 ['a7',1860,['Đối soát học phí','Xác nhận thu và in biên lai']],
 ['a8',1980,['Quản lý tài khoản, hồ sơ','học viên và giáo viên']],
 ['a9',2100,['Lập bảng lương','và xác nhận chi trả']],
 ['a10',2220,['Trả lời, kết thúc / mở lại','cuộc tư vấn']],
 ['a11',2340,['Xem thống kê','và quản lý banner']],
 ['a12',2460,['Khôi phục dữ liệu','và dọn thùng rác']]
].forEach(([id,y,t],i)=>add(id,rx,1140+i*110,t,'Admin'));
add('login',950,1000,['Đăng nhập hệ thống'],null,222);
add('password',510,1010,['Đổi mật khẩu'],null,170);
add('logout',1390,1010,['Đăng xuất'],null,160);
const actors={Guest:{x:105,y:495,label:'Khách'},Student:{x:105,y:1790,label:'Học viên'},Teacher:{x:1795,y:490,label:'Giáo viên'},Admin:{x:1795,y:1790,label:'Quản trị viên'}};
for(const n of nodes)if(n.role)links.push([n.role,n.id]);
for(const role of Object.keys(actors))links.push([role,'login']);
for(const role of ['Student','Teacher','Admin'])links.push([role,'password'],[role,'logout']);
includes.push(['s2','s3'],['t4','t5'],['a2','a3'],['a4','a5']);
let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1L11 6L1 11" fill="none" stroke="#222" stroke-width="2"/></marker></defs><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial,'Segoe UI',sans-serif;fill:#111}.assoc{fill:none;stroke:#777;stroke-width:1.6}.inc{fill:none;stroke:#222;stroke-width:2;stroke-dasharray:9 6;marker-end:url(#arrow)}.oval{fill:white;stroke:#222;stroke-width:2}</style><rect x="230" y="65" width="1440" height="2470" fill="none" stroke="#222" stroke-width="2.5"/><text x="950" y="39" text-anchor="middle" font-size="34" font-weight="bold">HỆ THỐNG TRUNG TÂM NGOẠI NGỮ NHK English times</text>`;
const byid=Object.fromEntries(nodes.map(n=>[n.id,n]));
for(const [role,id]of links){const a=actors[role],n=byid[id],left=a.x<950;
 let x=n.x+(left?-n.rx:n.rx),y=n.y;
 // Shared account goals use the gap between the upper and lower areas.
 if(!n.role){const bend=left?245:1655;const lane=id==='login'?950:id==='password'?927:1081;
  s+=`<path class="assoc" d="M${a.x+(left?24:-24)} ${a.y} L${bend} ${lane} L${x} ${y}"/>`;
 }else s+=`<path class="assoc" d="M${a.x+(left?24:-24)} ${a.y}L${x} ${y}"/>`;
}
for(const n of nodes){s+=`<ellipse class="oval" cx="${n.x}" cy="${n.y}" rx="${n.rx}" ry="${n.ry}"/>`;
 n.lines.forEach((line,i)=>s+=`<text x="${n.x}" y="${n.y}" text-anchor="middle" font-size="29" dominant-baseline="middle" transform="translate(0 ${(i-(n.lines.length-1)/2)*34})">${esc(line)}</text>`);
}
for(const [from,to]of includes){const a=byid[from],b=byid[to],right=a.x>950,corridor=right?970:925;
 const ax=a.x+(right?-1:1)*a.rx*.72,ay=a.y+a.ry*.68,bx=b.x+(right?-1:1)*b.rx*.72,by=b.y-b.ry*.68;
 s+=`<path class="inc" d="M${ax} ${ay}L${corridor} ${ay}L${corridor} ${by}L${bx} ${by}"/><rect x="${corridor-68}" y="${(ay+by)/2-17}" width="136" height="32" fill="white"/><text x="${corridor}" y="${(ay+by)/2+7}" text-anchor="middle" font-size="23">«include»</text>`;
}
for(const a of Object.values(actors)){s+=`<g fill="white" stroke="#222" stroke-width="3"><circle cx="${a.x}" cy="${a.y-52}" r="21"/><path d="M${a.x} ${a.y-31}v65m-38-41h76m-38 41l-32 43m32-43l32 43" fill="none"/></g><text x="${a.x}" y="${a.y+119}" text-anchor="middle" font-size="30" font-weight="bold">${a.label}</text>`;}
s+='<text x="950" y="2580" text-anchor="middle" font-size="23">Đường liền: tương tác với tác nhân · «include»: chức năng con bắt buộc</text></svg>';
async function main(){
 fs.writeFileSync(path.join(out,'01-tong-quat.svg'),s);
 await sharp(Buffer.from(s),{density:150}).png().toFile(path.join(out,'01-tong-quat.png'));
 const asset=path.resolve(out,'../report-work/final-refresh/assets');fs.copyFileSync(path.join(out,'01-tong-quat.svg'),path.join(asset,'uc-overview.svg'));fs.copyFileSync(path.join(out,'01-tong-quat.png'),path.join(asset,'uc-overview.png'));
 let p='@startuml\nleft to right direction\nskinparam monochrome true\n';
 for(const [id,a]of Object.entries(actors))p+=`actor "${a.label}" as ${id}\n`;
 p+='rectangle "NHK English times" {\n';for(const n of nodes)p+=`usecase "${n.lines.join('\\n')}" as ${n.id}\n`;p+='}\n';
 for(const [a,n]of links)p+=`${a} -- ${n}\n`;for(const [a,b]of includes)p+=`${a} ..> ${b} : <<include>>\n`;p+='@enduml\n';fs.writeFileSync(path.join(out,'01-tong-quat.puml'),p);
 fs.writeFileSync(path.join(out,'overview-nhk.json'),JSON.stringify({actors,nodes,links,includes},null,2));
 console.log(`${nodes.length} use cases, ${Object.keys(actors).length} actors, ${includes.length} mandatory includes`);
}
main();
