const fs=require('fs'),path=require('path'),sharp=require('sharp');
const dir=path.join(__dirname,'assets');
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
const text=(x,y,s,size=24,anchor='start')=>`<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${esc(s)}</text>`;
const start=(w,h)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial;fill:#111}path,line{fill:none;stroke:#444;stroke-width:2}</style>`;
async function save(name,s){fs.writeFileSync(path.join(dir,name+'.svg'),s);await sharp(Buffer.from(s),{density:180}).png().toFile(path.join(dir,name+'.png'));}
function actor(x,y,label){return `<g stroke="#222" stroke-width="2.3" fill="none"><circle cx="${x}" cy="${y-45}" r="16"/><path d="M${x} ${y-29}v55m-32-35h64m-32 35l-26 38m26-38l26 38"/></g>`+text(x,y+97,label,24,'middle');}
function uc(label,items){const h=items.length*82+90;let s=start(1060,h)+`<rect x="255" y="12" width="790" height="${h-24}" fill="none" stroke="#333" stroke-width="2"/>`+text(280,47,'Hệ thống NHK English times',25)+actor(115,h/2-10,label);items.forEach((v,i)=>{const y=97+i*82;s+=`<path d="M151 ${h/2-10}L285 ${y}"/><ellipse cx="655" cy="${y}" rx="365" ry="31" fill="white" stroke="#222" stroke-width="2"/>`+text(655,y+8,v,24,'middle');});return s+'</svg>';}
(async()=>{
 const defs={
 'uc-guest':['Khách',['Tra cứu chương trình và lớp tham khảo','Tìm kiếm và lọc khóa học','Xem chi tiết và học phí','Gửi yêu cầu tư vấn','Trao đổi trực tiếp với Admin','Theo dõi tư vấn bằng liên kết riêng','Đăng ký tài khoản học viên','Đăng nhập hệ thống']],
 'uc-student':['Học viên',['Quản lý hồ sơ và mật khẩu','Đăng ký khóa học theo nguyện vọng','Chọn ngày bắt đầu buổi và nhóm thứ','Xem hướng dẫn đóng học phí','Theo dõi đơn và lớp được Admin xếp','Xem thời khóa biểu và lịch thi','Đặt lịch kiểm tra xếp lớp','Xem điểm và cấp độ đề xuất','Xem học phí và in biên lai','Gửi đánh giá lớp đã được xếp','Trao đổi tư vấn và xem lịch sử']],
 'uc-teacher':['Giáo viên',['Xem bảng điều khiển và hồ sơ','Xem lớp và học viên được phân công','Theo dõi lịch giảng dạy','Quản lý tài liệu lớp học','Xem lớp thi được phân công chấm','Nhập điểm và đề xuất cấp độ','Xem phản hồi của học viên','Xem bảng lương của mình','Đổi mật khẩu và đăng xuất']],
 'uc-admin':['Admin',['Quản lý chương trình đào tạo','Tạo lớp và lịch 246 hoặc 357','Phân công giáo viên giảng dạy','Xếp lớp từ đơn và nguyện vọng','Đối soát và xác nhận học phí','Tạo phòng thi và xếp thí sinh','Phân công người chấm cả lớp thi','Quản lý hồ sơ và bảng lương','Trả lời và quản lý cuộc tư vấn','Quản lý thống kê và banner','Khôi phục dữ liệu trong thùng rác']]};
 for(const [name,[a,b]]of Object.entries(defs))await save(name,uc(a,b));
 require('../../use-cases/overview-nhk.cjs');
 let s;
 // Core entity diagram. Explicit cardinalities and nullable assignment are essential.
 function erd(name,boxes,edges,w=1200,h=960){let s=start(w,h);for(const [a,b,label]of edges){const A=boxes[a],B=boxes[b],ax=A[1]+155,ay=A[2]+120,bx=B[1]+155,by=B[2];s+=`<path d="M${ax} ${ay}L${bx} ${by}"/>`+text((ax+bx)/2+8,(ay+by)/2,label,22);}
 for(const [title,x,y,lines]of boxes){s+=`<rect x="${x}" y="${y}" width="320" height="120" rx="3" fill="white" stroke="#222" stroke-width="2"/><rect x="${x}" y="${y}" width="320" height="37" fill="#edf1f5"/>`+text(x+12,y+27,title,25);lines.forEach((l,i)=>s+=text(x+12,y+64+i*24,l,21));}return s+'</svg>';}
 await save('data-model',erd('core',[
 ['UserAccounts',35,25,['PK AccountId','Email unique Role']],['Students',440,25,['PK StudentId FK AccountId','Hồ sơ học viên']],['Teachers',845,25,['PK TeacherId FK AccountId','Hồ sơ giáo viên']],
 ['Programs',35,305,['PK ProgramId TuitionFee','Level Duration']],['Registrations',440,305,['PK RegistrationId','FK StudentId ProgramId ClassId?']],['Classes',845,305,['PK ClassId FK ProgramId','FK TeacherId? MaxStudents']],
 ['Payments',440,605,['PK PaymentId','FK RegistrationId unique']],['ClassSchedules',845,605,['PK ScheduleId FK ClassId','DayOfWeek StartTime EndTime']]
 ],[[0,1,'1 : 0..1'],[0,2,'1 : 0..1'],[1,4,'1 : N'],[2,5,'1 : N'],[3,4,'1 : N'],[4,6,'1 : 0..1'],[5,7,'1 : N']],1200,800));
 await save('data-support',erd('support',[
 ['ExamSessions',35,30,['PK ExamSessionId','FK TeacherId? Room ExamDate']],['PlacementTests',440,30,['PK TestId FK StudentId','FK ExamSessionId?']],['TeacherSalaries',845,30,['PK SalaryId FK TeacherId','Month Year Status']],
 ['Consultations',35,320,['PK ConsultationId','FK OwnerAccountId? Status']],['ConsultationMessages',440,320,['PK MessageId','FK ConsultationId SenderAccountId?']],['ClassDocuments',845,320,['PK DocumentId FK ClassId','Title FilePath']],
 ['Banners',35,630,['PK BannerId','ImageUrl DisplayOrder']],['CourseFeedbacks',845,630,['PK FeedbackId','FK StudentId ClassId Rating']]
 ],[[0,1,'1 : N'],[3,4,'1 : N']],1200,805));
 // Two independent branches ensure payment is not mistaken for class confirmation.
 s=start(1100,820)+text(550,40,'Luồng đăng ký và xếp lớp',29,'middle');
 const node=(x,y,w,h,lines)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="white" stroke="#222" stroke-width="2"/>`+lines.map((v,i)=>text(x+w/2,y+30+i*29,v,24,'middle')).join('');
 s+=node(225,70,650,90,['Học viên chọn chương trình','Ngày có thể bắt đầu buổi và nhóm 246 hoặc 357']);
 s+='<path d="M550 160v55"/>'+node(225,215,650,90,['Kiểm tra dữ liệu và đăng ký trùng','Tạo Registration Pending và Payment Pending']);
 s+='<path d="M550 305v45H270v55m280-55h280v55"/>';
 s+=node(40,405,460,115,['Admin xếp lớp đúng chương trình','Khai giảng từ ngày mong muốn trở đi','Kiểm tra sĩ số và lịch trùng']);
 s+=node(600,405,460,115,['Học viên đóng tiền mặt hoặc VietQR','Admin kiểm tra chứng từ','Xác nhận Payment Paid']);
 s+='<path d="M270 520v60m560-60v60"/>'+node(40,580,460,90,['Registration Confirmed ClassId được gán','Hiển thị lớp và thời khóa biểu'])+node(600,580,460,90,['Lưu trạng thái học phí','Hiển thị biên lai khi đủ điều kiện']);
 s+=text(550,737,'Xếp lớp và xác nhận học phí là hai nghiệp vụ độc lập',25,'middle');
 await save('enrollment-flow',s+'</svg>');
 // Replace the dense core overview with routed connectors and short field lines.
 s=start(1100,1100);
 const box=(x,y,title,lines)=>`<rect x="${x}" y="${y}" width="300" height="145" fill="white" stroke="#222" stroke-width="2"/><rect x="${x}" y="${y}" width="300" height="38" fill="#edf1f5"/>`+text(x+12,y+27,title,24)+lines.map((l,i)=>text(x+12,y+67+i*27,l,21)).join('');
 s+='<path d="M550 170v42H180v48m370-48h370v48M180 405v160M920 405v160M400 333H352v159H180v73m520-232h48v159h172v73M330 637h440M180 710v160M920 710v160"/>';
 for(const [x,y,t] of [[190,240,'1 : 0..1'],[780,240,'1 : 0..1'],[190,488,'1 : N'],[930,488,'1 : N'],[228,472,'1 : N'],[760,472,'1 : N'],[450,625,'N : 0..1'],[190,800,'1 : 0..1'],[930,800,'1 : N']])s+=text(x,y,t,21);
 s+=box(400,25,'UserAccounts',['PK AccountId','Email unique','Role PasswordHash'])+box(30,260,'Students',['PK StudentId','FK AccountId unique','Hồ sơ học viên'])+box(400,260,'Programs',['PK ProgramId','TuitionFee Level','Duration IsActive'])+box(770,260,'Teachers',['PK TeacherId','FK AccountId unique','Hồ sơ giáo viên'])+box(30,565,'Registrations',['PK RegistrationId','FK StudentId ProgramId','FK ClassId tùy chọn'])+box(770,565,'Classes',['PK ClassId','FK ProgramId TeacherId?','StartDate MaxStudents'])+box(30,870,'Payments',['PK PaymentId','FK RegistrationId unique','Amount Status'])+box(770,870,'ClassSchedules',['PK ScheduleId FK ClassId','DayOfWeek','StartTime EndTime']);
 s+=text(550,1070,'PK khóa chính   FK khóa ngoại   ? liên kết có thể để trống',22,'middle');
 await save('data-model',s+'</svg>');
 // Supporting tables are shown as a legible key map with only local links.
 s=start(1100,930);
 const sb=(x,y,title,lines)=>`<rect x="${x}" y="${y}" width="450" height="165" fill="white" stroke="#222" stroke-width="2"/><rect x="${x}" y="${y}" width="450" height="38" fill="#edf1f5"/>`+text(x+12,y+28,title,25)+lines.map((l,i)=>text(x+12,y+69+i*29,l,23)).join('');
 s+='<path d="M480 108h140M480 333h140"/>'+text(510,95,'1 : N',22)+text(510,320,'1 : N',22);
 const blocks=[['ExamSessions',30,25,['PK ExamSessionId FK TeacherId?','Room ExamDate Capacity','StartTime EndTime Status']],['PlacementTests',620,25,['PK TestId FK StudentId','FK ExamSessionId?','Score RecommendedLevel']],['Consultations',30,250,['PK ConsultationId','FK OwnerAccountId?','GuestAccessHash Status']],['ConsultationMessages',620,250,['PK MessageId FK ConsultationId','FK SenderAccountId?','Body SenderRole SentAt']],['TeacherSalaries',30,475,['PK SalaryId FK TeacherId','Month Year TotalSalary','Status']],['ClassDocuments',620,475,['PK DocumentId FK ClassId','Title FilePath','UploadedAt']],['Banners',30,700,['PK BannerId','ImageUrl LinkUrl','DisplayOrder IsActive']],['CourseFeedbacks',620,700,['PK FeedbackId','FK StudentId ClassId','Rating Comment']]];
 for(const [name,x,y,fields] of blocks)s+=sb(x,y,name,fields);
 await save('data-support',s+'</svg>');
 console.log('Updated use cases ER diagrams and enrollment flow');
})();
