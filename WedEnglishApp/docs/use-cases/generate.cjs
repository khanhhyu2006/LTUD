const fs = require('node:fs');
const path = require('node:path');
const out = __dirname;
const shared = [
  ['Đăng nhập', 'Account.Login'],
  ['Đổi mật khẩu', 'Account.ChangePassword'],
  ['Đăng xuất', 'Account.Logout'],
];
const specs = [
  {file:'01-tong-quat',title:'Use case tổng quát',groups:[
    {actor:'Khách',items:[['Tra cứu thông tin và khóa học'],['Gửi yêu cầu tư vấn'],['Đăng ký tài khoản / Đăng nhập']]},
    {actor:'Học viên',items:[['Quản lý tài khoản và hồ sơ'],['Đăng ký lớp và học phí'],['Theo dõi lớp, lịch học và thi'],['Gửi đánh giá khóa học']]},
    {actor:'Giáo viên',items:[['Quản lý tài khoản và ảnh hồ sơ'],['Theo dõi lớp và lịch giảng dạy'],['Quản lý tài liệu / Chấm thi xếp lớp'],['Xem phản hồi và bảng lương']]},
    {actor:'Admin',items:[['Thống kê / Quản lý đào tạo'],['Quản lý học viên và giáo viên'],['Quản lý học phí và lương'],['Quản lý tư vấn, banner, thùng rác']]},
  ]},
  {file:'02-khach',title:'Use case khách chưa đăng nhập',groups:[{actor:'Khách',items:[
    ['Xem trang chủ, khóa học nổi bật', 'Home.Index'],
    ['Tìm kiếm, lọc và xem danh sách khóa học', 'Program.Index'],
    ['Xem chi tiết khóa học và lớp mở', 'Program.Detail'],
    ['Xem thông tin liên hệ', 'Home.Contact'],
    ['Gửi yêu cầu tư vấn', 'Consultation.Submit'],
    ['Đăng ký tài khoản học viên', 'Account.Register'],
    ['Đăng nhập', 'Account.Login'],
  ]}]},
  {file:'03-hoc-vien',title:'Use case tài khoản học viên',groups:[{actor:'Học viên',items:[
    ...shared,
    ['Xem và cập nhật hồ sơ, ảnh đại diện', 'Student.Profile'],
    ['Tra cứu khóa học và lớp mở', 'Program.Index / Detail'],
    ['Đăng ký lớp và chọn cách thanh toán', 'Enrollment.Checkout / Confirm'],
    ['Gửi nguyện vọng giáo viên, ghi chú, ảnh', 'Enrollment.Confirm'],
    ['Xem lớp đã đăng ký và trạng thái', 'Student.MyClasses'],
    ['Xem lịch học và lịch thi theo tuần', 'Student.Schedule'],
    ['Xem lịch sử học phí', 'Student.MyPayments'],
    ['Xem và in biên lai học phí', 'Student.PrintReceipt'],
    ['Đặt lịch kiểm tra xếp lớp', 'PlacementTest.BookTest (POST)'],
    ['Xem lịch, điểm và cấp độ đề xuất', 'PlacementTest.BookTest (GET)'],
    ['Gửi đánh giá, nhận xét khóa học', 'Student.SubmitFeedback'],
  ]}]},
  {file:'04-giao-vien',title:'Use case tài khoản giáo viên',groups:[{actor:'Giáo viên',items:[
    ...shared,
    ['Xem bảng điều khiển giảng dạy', 'Teacher/TeacherDashboard.Index'],
    ['Cập nhật ảnh hồ sơ', 'Teacher/TeacherDashboard.UploadPhoto'],
    ['Xem các lớp được phân công', 'Teacher/TeachingClass.Index'],
    ['Xem danh sách học viên của lớp', 'Teacher/TeachingClass.Students'],
    ['Xem lịch dạy và lịch thi được giao', 'Teacher/TeachingClass.Schedule'],
    ['Xem, tải lên và xóa tài liệu lớp', 'Teacher/Document.Index / Upload / Delete'],
    ['Tải tài liệu về', 'Teacher/Views/Document/Index.cshtml (liên kết tệp)'],
    ['Xem bài kiểm tra được phân công', 'Teacher/TeacherTest.Index'],
    ['Chấm điểm và đề xuất cấp độ', 'Teacher/TeacherTest.Grade'],
    ['Xem phản hồi của học viên', 'Teacher/Feedback.Index'],
    ['Xem bảng lương và trạng thái chi trả', 'Teacher/TeacherSalary.Index'],
  ]}]},
  {file:'05-admin',title:'Use case tài khoản quản trị viên',groups:[{actor:'Admin',items:[
    ...shared,
    ['Xem thống kê và biểu đồ doanh thu', 'Admin/Dashboard.Index'],
    ['Quản lý chương trình, bật / tắt tuyển sinh', 'Admin/ProgramManager.Index / Create / Edit / Delete / ToggleStatus'],
    ['Thêm, sửa, xóa mềm lớp và lịch học', 'Admin/ClassManager.Index / Create / Edit / Delete'],
    ['Xem chi tiết lớp, phân công giáo viên', 'Admin/ClassManager.Details / AssignTeacher'],
    ['Thêm / Gỡ học viên khỏi lớp', 'Admin/ClassManager.AddStudentToClass / RemoveStudentFromClass'],
    ['Tạo, sửa, xóa mềm hồ sơ giáo viên', 'Admin/TeacherManager.Index / Create / Edit / Delete'],
    ['Sửa hồ sơ, khóa / mở tài khoản học viên', 'Admin/StudentManager.Index / Edit / ToggleStatus'],
    ['Xếp / Chuyển lớp cho đơn đăng ký', 'Admin/RegistrationAdmin.AssignClass'],
    ['Duyệt, hủy, xóa mềm đơn đăng ký', 'Admin/RegistrationAdmin.Index / UpdateStatus / Delete'],
    ['Xem học phí và xác nhận thu tiền', 'Admin/PaymentAdmin.Index / ConfirmPayment'],
    ['Xem và in biên lai học phí', 'Admin/PaymentAdmin.PrintReceipt'],
    ['Xếp lịch, phòng, giáo viên thi đầu vào', 'Admin/PlacementTestAdmin.Index / AssignScheduleAndTeacher'],
    ['Cập nhật điểm, cấp độ / Xóa mềm lịch thi', 'Admin/PlacementTestAdmin.UpdateResult / Delete'],
    ['Lập, sửa, lọc và xóa bảng lương', 'Admin/SalaryAdmin.Index / CreateOrUpdate / Delete'],
    ['Xác nhận chi trả lương giáo viên', 'Admin/SalaryAdmin.ConfirmPayment'],
    ['Xem, đổi trạng thái, xóa mềm tư vấn', 'Admin/ConsultationManager.Index / ToggleStatus / Delete'],
    ['Quản lý banner và bật / tắt hiển thị', 'Admin/BannerManager.Index / Create / Edit / Delete / ToggleActive'],
    ['Xem và khôi phục dữ liệu thùng rác', 'Admin/Trash.Index / Restore'],
    ['Xóa vĩnh viễn / Dọn thùng rác', 'Admin/Trash.PermanentDelete / EmptyTrash'],
  ]}]},
];
const esc = s => String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function wrap(s, max=42) {
  const lines=[''];
  for (const word of s.split(' ')) {
    if ((lines.at(-1)+' '+word).trim().length>max) lines.push(word);
    else lines[lines.length-1]=(lines.at(-1)+' '+word).trim();
  }
  return lines;
}
function svg(spec) {
  const row=88, gap=38;
  const height=140+spec.groups.reduce((sum,g)=>sum+g.items.length*row+gap,0);
  let parts=[`<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="${height}" viewBox="0 0 1080 ${height}" role="img" aria-label="${esc(spec.title)}"><style>text{font-family:Arial,'Segoe UI',sans-serif;fill:#172b4d} .uc{fill:#f4f8ff;stroke:#315a85;stroke-width:1.5}.link{stroke:#6e839c;stroke-width:1.3;fill:none}</style><rect width="1080" height="${height}" fill="white"/><text x="40" y="38" font-size="25" font-weight="700">${esc(spec.title)}</text><text x="40" y="65" font-size="14">NHK English times · Đối chiếu mã nguồn ngày 03/11/2026</text><rect x="310" y="88" width="735" height="${height-112}" rx="8" fill="none" stroke="#172b4d" stroke-width="2"/><text x="332" y="114" font-size="15" font-weight="700">HỆ THỐNG QUẢN LÝ TRUNG TÂM NGOẠI NGỮ</text>`];
  let y=148;
  for (const g of spec.groups) {
    const mid=y+(g.items.length-1)*row/2;
    // Actor stays outside the system boundary; solid associations have no arrows.
    parts.push(`<g stroke="#172b4d" stroke-width="2" fill="none"><circle cx="135" cy="${mid-48}" r="15"/><path d="M135 ${mid-33}v48 M105 ${mid-15}h60 M135 ${mid+15}l-25 33 M135 ${mid+15}l25 33"/></g><text x="135" y="${mid+75}" text-anchor="middle" font-size="18" font-weight="700">${esc(g.actor)}</text>`);
    for (const [label] of g.items) {
      parts.push(`<path class="link" d="M168 ${mid} L380 ${y}"/><ellipse class="uc" cx="685" cy="${y}" rx="305" ry="34"/>`);
      const lines=wrap(label);
      lines.forEach((line,i)=>parts.push(`<text x="685" y="${y-(lines.length-1)*10+i*20+6}" text-anchor="middle" font-size="17">${esc(line)}</text>`));
      y+=row;
    }
    y+=gap;
  }
  parts.push('</svg>'); return parts.join('\n');
}
for (const spec of specs) {
  fs.writeFileSync(path.join(out,spec.file+'.svg'),svg(spec));
  let p=['@startuml','left to right direction','skinparam defaultFontName Arial','skinparam shadowing false',`title ${spec.title}`];
  spec.groups.forEach((g,i)=>p.push(`actor "${g.actor}" as A${i}`));
  p.push('rectangle "Hệ thống quản lý trung tâm ngoại ngữ NHK English times" {');
  spec.groups.forEach((g,i)=>g.items.forEach(([label],j)=>p.push(`  usecase "${label}" as U${i}_${j}`)));
  p.push('}');
  spec.groups.forEach((g,i)=>g.items.forEach((_,j)=>p.push(`A${i} -- U${i}_${j}`)));
  p.push('@enduml');
  fs.writeFileSync(path.join(out,spec.file+'.puml'),p.join('\n')+'\n');
}
let md=`# Sơ đồ use case – NHK English times\n\nPhân tích từ mã nguồn hiện có ngày 03/11/2026. Có ba vai trò tài khoản: Student, Teacher, Admin. Khách là tác nhân chưa đăng nhập, không phải một loại tài khoản. Mỗi tài khoản cùng vai trò dùng chung sơ đồ.\n\nMở **index.html** để xem toàn bộ sơ đồ, phóng to và in. Tệp SVG là ảnh vector chèn vào báo cáo; tệp PlantUML (.puml) dùng để chỉnh sửa. Chạy lại: \`node docs/use-cases/generate.cjs\`.\n\n## Quy ước\n\nNgười que là tác nhân, hình elip là use case, khung chữ nhật là ranh giới hệ thống. Đường liền là quan hệ tương tác, không thể hiện thứ tự thực hiện. Sơ đồ tổng quát gộp các mục tiêu nghiệp vụ; sơ đồ từng vai trò phân rã chức năng. Không dùng include/extend khi chưa có quan hệ bắt buộc hoặc mở rộng rõ ràng. Đăng nhập là điều kiện trước cho các chức năng bảo vệ, không phải bước được gọi lại trong mỗi use case. Chức năng công khai vẫn có thể được truy cập khi dùng tài khoản; không lặp lại toàn bộ ở mọi sơ đồ.\n\n## Giới hạn được xác nhận từ mã nguồn\n\n- **Điểm danh:** checkbox trong Teacher/Views/TeachingClass/Students.cshtml chưa có thao tác lưu; AttendanceController chỉ trả View. Không đưa điểm danh đã lưu vào sơ đồ.\n- **Thanh toán:** VietQR hiển thị ảnh QR; Admin xác nhận thu tiền. Enrollment.Confirm tự gán Paid cho lựa chọn VNPay/MoMo; các lớp VnPayService/IVnPayService còn trống, chưa có luồng gọi cổng hoặc callback thật. Sơ đồ không thêm tác nhân cổng thanh toán tự động.\n- **Tài liệu học viên:** chưa tìm thấy giao diện/action tra cứu, tải tài liệu trong Student; hiện quản lý/tải tài liệu nằm ở Teacher.\n- **Tư vấn:** Admin đổi trạng thái Pending/Replied; chưa có thao tác gửi nội dung trả lời/email trong ConsultationManagerController.\n- **Tài khoản giáo viên:** có tạo, sửa và xóa mềm; chưa có action khóa/mở riêng như học viên.\n- **Lương, banner, thùng rác:** có triển khai trong mã nguồn, đã bổ sung vào bộ sơ đồ.\n- Đây là tài liệu phân tích tĩnh chức năng, chưa phải kết quả kiểm thử vận hành hay kiểm toán phân quyền.\n\n`;
for (const spec of specs) {
  md+=`## ${spec.title}\n\n![${spec.title}](${spec.file}.svg)\n\n`;
  if(spec.file==='01-tong-quat')continue;
  md+='| Use case | Controller / Action hoặc View đối chiếu |\n|---|---|\n';
  for(const g of spec.groups)for(const [label,source] of g.items)md+=`| ${label} | ${source} |\n`;
  md+='\n';
}
fs.writeFileSync(path.join(out,'README.md'),md);
const cards=specs.map(s=>`<section id="${s.file}"><h2>${esc(s.title)}</h2><p><a href="${s.file}.svg" download>Tải SVG</a> · <a href="${s.file}.puml" download>Mã PlantUML</a> · <a href="${s.file}.svg" target="_blank">Mở ảnh để phóng to</a></p><img src="${s.file}.svg" alt="${esc(s.title)}" loading="lazy"></section>`).join('\n');
fs.writeFileSync(path.join(out,'index.html'),`<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sơ đồ use case NHK English times</title><style>body{margin:0;background:#edf2f7;color:#172b4d;font:16px/1.6 Arial,sans-serif}main{max-width:1150px;margin:auto;padding:28px}h1{margin-bottom:8px}nav{display:flex;gap:12px;flex-wrap:wrap}a{color:#17569a}section{background:white;border-radius:12px;margin:28px 0;padding:24px;box-shadow:0 2px 10px #18345212}img{display:block;width:100%;height:auto}aside{background:#fff5db;padding:16px;border-left:4px solid #ba8614}button{padding:8px 16px;cursor:pointer}@media print{body{background:white}nav,button,section>p{display:none}main{padding:0}section{box-shadow:none;padding:0;break-before:page}h2{font-size:18px}img{max-height:255mm;object-fit:contain;object-position:top}}</style><main><h1>Sơ đồ use case NHK English times</h1><p>01 sơ đồ tổng quát · 03 vai trò tài khoản · 01 sơ đồ khách. Đối chiếu mã nguồn ngày 03/11/2026.</p><nav>${specs.map(s=>`<a href="#${s.file}">${esc(s.title.replace('Use case ',''))}</a>`).join('')}</nav><p><button onclick="window.print()">In / Lưu PDF</button> · <a href="README.md">Bảng đối chiếu chức năng với mã nguồn</a></p><aside><b>Phạm vi thực tế:</b> Điểm danh chưa lưu dữ liệu; VNPay/MoMo đang mô phỏng. Chưa có luồng tải tài liệu riêng cho học viên hoặc gửi trả lời tư vấn qua email. Xem README để biết chi tiết.</aside>${cards}<p>Quy ước UML: người que = tác nhân; elip = use case; khung = hệ thống; đường liền = tương tác. Các sơ đồ thể hiện mục tiêu chức năng, không mô tả thứ tự thao tác.</p></main></html>`);
console.log(`Generated ${specs.length} SVG, ${specs.length} PlantUML, index.html and README.md`);

// Preserve the current reference-style overview after rebuilding the legacy role diagrams.
require('./overview-nhk.cjs');
