from pathlib import Path
root=Path('WedEnglishApp')
def r(p):return(root/p).read_text(encoding='utf-8-sig')
def w(p,s):(root/p).write_text(s,encoding='utf8')
w('Areas/Admin/Views/RegistrationAdmin/Index.cshtml','''@model List<WedEnglishApp.Models.Registration>
@using WedEnglishApp.Services
@{ ViewData["Title"] = "Đăng ký khóa học và xếp lớp";
var classes = ViewBag.AvailableClasses as List<WedEnglishApp.Models.CourseClass> ?? new();
var programs = ViewBag.Programs as List<WedEnglishApp.Models.CourseProgram> ?? new(); }
<h3>Đăng ký khóa học và xếp lớp</h3>
<p class="text-muted">Tiếp nhận nguyện vọng, kiểm tra lịch và xếp học viên vào lớp phù hợp. Thanh toán được quản lý riêng.</p>
<form method="get" class="d-flex gap-2 mb-4"><select class="form-select" name="programId"><option value="">Tất cả khóa học</option>@foreach(var p in programs) { <option value="@p.ProgramId" selected="@(ViewBag.SelectedProgramId == p.ProgramId)">@p.ProgramName</option> }</select><button class="btn btn-primary">Lọc</button></form>
<div class="admin-card"><div class="table-responsive"><table class="table align-middle"><thead><tr><th>Học viên / Khóa học</th><th>Nguyện vọng lịch học</th><th>Lớp đã xếp</th><th>Thanh toán</th><th>Trạng thái / Thao tác</th></tr></thead><tbody>
@foreach(var reg in Model) {
var candidates = classes.Where(c => CourseClassAssignment.CheckPreferences(reg, c) == null && c.Registrations.Count(x => !x.IsDeleted && x.Status == "Confirmed" && x.RegistrationId != reg.RegistrationId) < c.MaxStudents).OrderByDescending(c => reg.DesiredTeacherId.HasValue && c.TeacherId == reg.DesiredTeacherId).ThenBy(c => c.StartDate).ToList();
<tr><td><strong>@reg.Student.UserAccount.FullName</strong><div class="small">@reg.Student.UserAccount.Email</div><div class="text-primary mt-2">@reg.Program.ProgramName</div><small>#REG-@reg.RegistrationId</small></td>
<td>@await Html.PartialAsync("_EnrollmentPreferences", reg)</td>
<td>@(reg.Class?.ClassName ?? "Chờ xếp lớp")
@if(reg.Class != null) { <div class="small">@reg.Class.StartDate.ToString("dd/MM/yyyy") · @(reg.Class.Teacher?.UserAccount.FullName ?? "Chưa phân công giáo viên")</div> }
</td>
<td><span class="badge @(reg.Payment?.Status == "Paid" ? "bg-success" : "bg-warning text-dark")">@(reg.Payment?.Status == "Paid" ? "Đã thu học phí" : "Chờ thu học phí")</span><div>@reg.Payment?.Amount.ToString("N0") đ</div></td>
<td><div class="mb-2">@(reg.Status == "Confirmed" ? "Đã xếp lớp" : reg.Status == "Cancelled" ? "Đã hủy" : "Chờ xếp lớp")</div>
@if(reg.Status != "Cancelled") {
@if(candidates.Any()) { <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#assign-@reg.RegistrationId">Xếp / đổi lớp</button> }
else { <div class="small text-warning-emphasis">Chưa có lớp đáp ứng ngày bắt đầu, buổi học, thứ học hoặc sĩ số. Hãy tạo / điều chỉnh lớp phù hợp trước.</div><a asp-controller="ClassManager" asp-action="Create" class="btn btn-sm btn-outline-primary">Mở lớp mới</a> }
<form asp-action="UpdateStatus" method="post" class="mt-2">@Html.AntiForgeryToken()<input type="hidden" name="id" value="@reg.RegistrationId" /><button class="btn btn-sm btn-outline-secondary" name="status" value="Pending">Đưa về chờ xếp lớp</button><button class="btn btn-sm btn-outline-danger mt-1" name="status" value="Cancelled" onclick="return confirm('Hủy đăng ký này?');">Hủy đăng ký</button></form>
}
</td></tr>
}
</tbody></table></div></div>
@foreach(var reg in Model.Where(r => r.Status != "Cancelled")) {
var candidates = classes.Where(c => CourseClassAssignment.CheckPreferences(reg, c) == null && c.Registrations.Count(x => !x.IsDeleted && x.Status == "Confirmed" && x.RegistrationId != reg.RegistrationId) < c.MaxStudents).OrderByDescending(c => reg.DesiredTeacherId.HasValue && c.TeacherId == reg.DesiredTeacherId).ThenBy(c => c.StartDate).ToList();
<div class="modal fade" id="assign-@reg.RegistrationId" tabindex="-1" aria-labelledby="assign-title-@reg.RegistrationId" aria-hidden="true"><div class="modal-dialog modal-lg"><div class="modal-content"><form asp-action="AssignClass" method="post">@Html.AntiForgeryToken()<input type="hidden" name="registrationId" value="@reg.RegistrationId" /><div class="modal-header"><h5 id="assign-title-@reg.RegistrationId">Xếp lớp: @reg.Student.UserAccount.FullName</h5><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Đóng"></button></div><div class="modal-body"><h6>@reg.Program.ProgramName</h6>@await Html.PartialAsync("_EnrollmentPreferences", reg)
<label class="form-label mt-3" for="class-@reg.RegistrationId">Lớp đáp ứng lịch học và còn chỗ</label><select name="newClassId" id="class-@reg.RegistrationId" class="form-select" required><option value="">Chọn lớp phù hợp</option>
@foreach(var c in candidates) { <option value="@c.ClassId">@c.ClassName · @c.StartDate.ToString("dd/MM/yyyy") · @string.Join(", ",c.Schedules.Select(s => $"{(s.DayOfWeek == 8 ? "CN" : $"T{s.DayOfWeek}")} {s.StartTime:hh\\:mm}–{s.EndTime:hh\\:mm}")) · @(c.Teacher?.UserAccount.FullName ?? "Chưa có giáo viên") @(reg.DesiredTeacherId.HasValue && c.TeacherId == reg.DesiredTeacherId ? "(Đúng giáo viên mong muốn)" : "")</option> }
</select><p class="form-text">Hệ thống kiểm tra lại sĩ số và lịch trùng khi xác nhận. Giáo viên mong muốn được ưu tiên, không phải cam kết.</p></div><div class="modal-footer"><button class="btn btn-primary" type="submit">Xác nhận xếp lớp</button></div></form></div></div></div>
}
''')
s=r('Views/Student/MyClasses.cshtml');s=s.replace('Lớp Học Của Tôi','Khóa học và lớp của tôi').replace('Đăng ký thêm lớp','Đăng ký thêm khóa học').replace('Bạn chưa đăng ký lớp học nào!','Bạn chưa đăng ký khóa học nào!').replace('để chọn lớp học phù hợp','để chọn khóa học phù hợp').replace('Chờ xác nhận','Chờ xếp lớp').replace('Đã xác nhận','Đã xếp lớp')
s=s.replace('            {\n                <div class="col-lg-6">','''            {
                @if (reg.ClassId == null || reg.Class == null) {
                    <div class="col-lg-6"><div class="card p-4 h-100"><span class="badge @(reg.Status == "Cancelled" ? "bg-secondary" : "bg-warning text-dark") align-self-start">@(reg.Status == "Cancelled" ? "Đã hủy" : "Chờ Admin xếp lớp")</span><h4 class="mt-3">@reg.Program.ProgramName</h4><p>Đơn #REG-@reg.RegistrationId · @reg.RegistrationDate.ToString("dd/MM/yyyy")</p>
                    @await Html.PartialAsync("_EnrollmentPreferences", reg)
                    <p class="mt-3">Trung tâm sẽ xếp lớp theo lịch bạn đã gửi. Lịch chính thức sẽ xuất hiện tại đây sau khi Admin xác nhận.</p>
                    @await Html.PartialAsync("_RegistrationPayment", reg)
                    </div></div>
                    continue;
                }
                <div class="col-lg-6">''')
s=s.replace('reg.Class.Program.', 'reg.Program.')
s=s.replace('                        <!-- Modal Đánh giá lớp học -->','''                        @await Html.PartialAsync("_RegistrationPayment", reg)
                        <!-- Modal Đánh giá lớp học -->''')
w('Views/Student/MyClasses.cshtml',s)
w('Views/Shared/_RegistrationPayment.cshtml','''@model WedEnglishApp.Models.Registration
@if (Model.Payment != null) {
<p class="small">Học phí: <strong>@Model.Payment.Amount.ToString("N0") VNĐ</strong> · @(Model.Payment.Status == "Paid" ? "Đã thanh toán" : "Chờ trung tâm xác nhận thanh toán")</p>
@if (Model.Status != "Cancelled" && Model.Payment.Status != "Paid" && Model.Payment.PaymentMethod == "VietQR") {
<div class="text-center border rounded p-3 mt-2"><p>Chuyển khoản với nội dung <strong>@Model.Payment.TransactionCode</strong></p><img src="https://img.vietqr.io/image/vietinbank-113366668888-compact2.png?amount=@((long)Model.Payment.Amount)&amp;addInfo=@Uri.EscapeDataString(Model.Payment.TransactionCode ?? $"HPREG{Model.RegistrationId}")&amp;accountName=TRUNG%20TAM%20NGOAI%20NGU%20HITC" alt="Mã VietQR cho đơn đăng ký" class="img-fluid" style="max-width:240px" /><p class="small mb-0">VietinBank · 113366668888 · TRUNG TAM NGOAI NGU HITC</p></div>
}
}
''')
# Class-details waiting list includes preferences and correctly handles no previous class.
s=r('Areas/Admin/Views/ClassManager/Details.cshtml');s=s.replace('<span class="badge bg-light text-dark border">@(reg.Class?.ClassName ?? "Chờ xếp lớp")</span>','<span class="badge bg-light text-dark border">@(reg.Class?.ClassName ?? "Chờ xếp lớp")</span>\n                                @await Html.PartialAsync("_EnrollmentPreferences", reg)');w('Areas/Admin/Views/ClassManager/Details.cshtml',s)
# Every read model showing recent records needs a course even if no class exists.
s=r('Areas/Admin/Controllers/DashboardController.cs').replace('.Include(r => r.Class)', '.Include(r => r.Program)\n                .Include(r => r.Class)');w('Areas/Admin/Controllers/DashboardController.cs',s)
s=r('Areas/Admin/Views/Dashboard/Index.cshtml').replace('@(r.Class?.ClassName ?? "Chờ xếp lớp")','@(r.Class?.ClassName ?? $"{r.Program.ProgramName} · Chờ xếp lớp")');w('Areas/Admin/Views/Dashboard/Index.cshtml',s)
print('Admin assignment UI and student pending-course cards updated')
