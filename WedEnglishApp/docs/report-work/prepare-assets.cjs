const fs=require('node:fs'),path=require('node:path'),sharp=require('sharp');
const root=__dirname,dir=path.join(root,'assets');
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
const wrap=(s,max=36)=>{let a=[''];for(const w of s.split(' ')){if((a.at(-1)+' '+w).trim().length>max)a.push(w);else a[a.length-1]=(a.at(-1)+' '+w).trim();}return a;};
function diagram(title,groups){
 const row=70,gap=20,h=115+groups.reduce((s,g)=>s+g.items.length*row+gap,0);
 let a=[`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="${h}"><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial;fill:#111}path{fill:none;stroke:#333;stroke-width:1.5}</style><rect x="260" y="15" width="800" height="${h-30}" fill="none" stroke="#222" stroke-width="2"/><text x="285" y="47" font-size="23" font-weight="bold">Hệ thống HITC English</text>`];
 let y=95;
 for(const g of groups){const m=y+(g.items.length-1)*row/2;
 a.push(`<g stroke="#111" stroke-width="2" fill="none"><circle cx="112" cy="${m-44}" r="14"/><path d="M112 ${m-30}v48 M84 ${m-12}h56 M112 ${m+18}l-23 30 M112 ${m+18}l23 30"/></g><text x="112" y="${m+75}" text-anchor="middle" font-size="23">${escape(g.actor)}</text>`);
 for(const s of g.items){a.push(`<path d="M145 ${m}L330 ${y}"/><ellipse cx="685" cy="${y}" rx="355" ry="29" fill="#fff" stroke="#222" stroke-width="1.6"/>`);let lines=wrap(s,46);lines.forEach((l,i)=>a.push(`<text x="685" y="${y-(lines.length-1)*11+i*22+7}" font-size="22" text-anchor="middle">${escape(l)}</text>`));y+=row;}y+=gap;}
 a.push('</svg>');return a.join('');
}
const defs=[
 ['uc-overview',[{actor:'Khách',items:['Tra cứu khóa học và liên hệ','Đăng ký tài khoản và yêu cầu tư vấn']},{actor:'Học viên',items:['Quản lý hồ sơ và đăng ký lớp','Theo dõi học phí, lịch học và thi','Gửi đánh giá khóa học']},{actor:'Giáo viên',items:['Theo dõi lớp và lịch giảng dạy','Quản lý tài liệu và chấm thi','Xem phản hồi và bảng lương']},{actor:'Admin',items:['Quản lý đào tạo và tài khoản','Quản lý học phí, lương và thống kê','Quản lý tư vấn, banner và thùng rác']}]],
 ['uc-guest',[{actor:'Khách',items:['Xem trang chủ và khóa học nổi bật','Tìm kiếm và lọc khóa học','Xem chi tiết chương trình và lớp mở','Xem thông tin liên hệ','Gửi yêu cầu tư vấn','Đăng ký tài khoản học viên','Đăng nhập hệ thống']}]],
 ['uc-student',[{actor:'Học viên',items:['Đăng nhập, đổi mật khẩu và đăng xuất','Xem và cập nhật hồ sơ, ảnh đại diện','Tra cứu khóa học và lớp mở','Đăng ký lớp, chọn phương thức thanh toán','Gửi nguyện vọng giáo viên và ghi chú','Xem lớp đã đăng ký và trạng thái','Xem thời khóa biểu và lịch thi','Xem lịch sử học phí và in biên lai','Đặt lịch kiểm tra xếp lớp','Xem điểm thi và cấp độ đề xuất','Gửi đánh giá, nhận xét khóa học']}]],
 ['uc-teacher',[{actor:'Giáo viên',items:['Đăng nhập, đổi mật khẩu và đăng xuất','Xem bảng điều khiển giảng dạy','Cập nhật ảnh hồ sơ','Xem lớp được phân công','Xem danh sách học viên của lớp','Xem lịch dạy và lịch thi được giao','Xem, tải lên, tải về và xóa tài liệu','Xem bài kiểm tra được phân công','Chấm điểm và đề xuất cấp độ','Xem phản hồi của học viên','Xem bảng lương và tình trạng chi trả']}]],
 ['uc-admin',[{actor:'Admin',items:['Đăng nhập, đổi mật khẩu và đăng xuất','Xem thống kê và biểu đồ doanh thu','Quản lý chương trình học và tuyển sinh','Quản lý lớp, phân công giáo viên','Quản lý hồ sơ học viên và giáo viên','Xếp lớp và duyệt đơn đăng ký','Xác nhận học phí và in biên lai','Xếp lịch thi và cập nhật kết quả','Quản lý bảng lương và xác nhận chi trả','Quản lý tư vấn và banner','Khôi phục hoặc xóa dữ liệu thùng rác']}]],
];
async function main(){
 for(const [name,groups] of defs){const s=diagram(name,groups);fs.writeFileSync(path.join(dir,name+'.svg'),s);await sharp(Buffer.from(s),{density:180}).png().toFile(path.join(dir,name+'.png'));}
 await sharp('C:/Users/ASUS/AppData/Local/Temp/codex-clipboard-8006146d-cc76-4509-84fa-27479a66296a.png').extract({left:197,top:196,width:112,height:113}).png().toFile(path.join(dir,'hitc-logo.png'));
 // An entity relationship overview: show actual DbSet names, keys and cardinalities.
 const boxes=[
 ['UserAccount',40,35,['PK AccountId','Email (unique), Role']],['Student',440,35,['PK StudentId','FK AccountId']],['Teacher',840,35,['PK TeacherId','FK AccountId']],
 ['Program',40,235,['PK ProgramId','ProgramName, TuitionFee']],['Class',440,235,['PK ClassId','FK ProgramId, TeacherId']],['Registration',840,235,['PK RegistrationId','FK StudentId, ClassId','FK DesiredTeacherId']],
 ['ClassSchedule',40,435,['PK ScheduleId','FK ClassId']],['ClassDocument',440,435,['PK DocumentId','FK ClassId']],['Payment',840,435,['PK PaymentId','FK RegistrationId (unique)']],
 ['PlacementTest',40,635,['PK TestId','FK StudentId','FK EvaluatedByTeacherId']],['CourseFeedback',440,635,['PK FeedbackId','FK StudentId, ClassId']],['TeacherSalary',840,635,['PK SalaryId','FK TeacherId']],
 ['Consultation',240,835,['PK ConsultationId','ContactName, Status']],['Banner',640,835,['PK BannerId','ImageUrl, DisplayOrder']],
 ];
 let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1040"><rect width="1200" height="1040" fill="white"/><style>text{font-family:Arial;font-size:23px}path{stroke:#555;stroke-width:2;fill:none}</style>`;
 // FK details in each box identify cross-links without unreadable crossing edges.
 for(const [name,x,y,fields]of boxes){svg+=`<rect x="${x}" y="${y}" width="315" height="155" rx="4" fill="white" stroke="#222" stroke-width="2"/><rect x="${x}" y="${y}" width="315" height="40" fill="#e8eef5"/><text x="${x+14}" y="${y+28}" font-weight="bold">${name}</text>`;fields.forEach((f,i)=>svg+=`<text x="${x+14}" y="${y+69+i*29}" font-size="20">${escape(f)}</text>`);}
 svg+='<text x="40" y="1020" font-size="20">PK: khóa chính · FK: khóa ngoại · Quan hệ chi tiết trình bày trong bảng thiết kế dữ liệu.</text></svg>';
 fs.writeFileSync(path.join(dir,'data-model.svg'),svg);await sharp(Buffer.from(svg),{density:180}).png().toFile(path.join(dir,'data-model.png'));
 // Convert screenshots to high-quality JPEG for a manageable Word file size.
 for(const f of fs.readdirSync(dir).filter(f=>f.startsWith('ui-')&&f.endsWith('.png'))){await sharp(path.join(dir,f)).jpeg({quality:88,mozjpeg:true}).toFile(path.join(dir,f.replace('.png','.jpg')));}
 let inputs=fs.readdirSync(dir).filter(f=>f.startsWith('ui-')&&f.endsWith('.jpg'));let comp=[];
 for(let i=0;i<inputs.length;i++){let b=await sharp(path.join(dir,inputs[i])).resize(360,230,{fit:'contain',background:'white'}).png().toBuffer();let label=Buffer.from(`<svg width="360" height="24"><rect width="360" height="24" fill="white"/><text x="5" y="18" font-family="Arial" font-size="14">${inputs[i]}</text></svg>`);comp.push({input:b,left:i%3*380,top:Math.floor(i/3)*270+24},{input:label,left:i%3*380,top:Math.floor(i/3)*270});}
 await sharp({create:{width:1140,height:Math.ceil(inputs.length/3)*270,channels:3,background:'white'}}).composite(comp).png().toFile(path.join(root,'qa/captures-sheet.png'));
 console.log('Prepared diagrams, logo, screenshots and QA contact sheet');
}
main();
