exec(open('session-state/implement-criteria.py',encoding='utf-8-sig').read().split("write('Models/TeacherActivity.cs'")[0])
write('Areas/Teacher/Views/Document/Index.cshtml','''
@model List<WedEnglishApp.Models.ClassDocument>
@{ ViewData["Title"] = "Tài liệu lớp học"; }
<div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
 <div><h3 class="fw-bold">Tài liệu lớp học</h3><p class="text-muted mb-0">Quản lý bản nháp và tài liệu đã công bố cho các lớp bạn phụ trách.</p></div>
 <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#uploadDocModal">Tải tài liệu mới</button>
</div>
<div class="modal fade" id="uploadDocModal" tabindex="-1" aria-labelledby="uploadTitle" aria-hidden="true"><div class="modal-dialog"><div class="modal-content">
<form asp-action="Upload" method="post" enctype="multipart/form-data">
 @Html.AntiForgeryToken()
 <div class="modal-header"><h5 id="uploadTitle" class="modal-title">Thêm tài liệu</h5><button class="btn-close" type="button" data-bs-dismiss="modal" aria-label="Đóng"></button></div>
 <div class="modal-body">
  <label class="form-label" for="docClass">Lớp học</label><select id="docClass" name="classId" asp-items="ViewBag.Classes" class="form-select mb-3" required><option value="">Chọn lớp bạn phụ trách</option></select>
  <label class="form-label" for="docTitle">Tiêu đề</label><input id="docTitle" name="title" class="form-control mb-3" required maxlength="200" />
  <label class="form-label" for="docFile">Tệp tài liệu</label><input id="docFile" type="file" name="documentFile" class="form-control" accept=".pdf,.docx,.pptx,.xlsx,.txt" required />
  <p class="form-text">PDF, DOCX, PPTX, XLSX hoặc TXT; tối đa 10 MB.</p>
  <div class="form-check"><input id="publishNew" class="form-check-input" type="checkbox" name="isPublished" value="true"/><label class="form-check-label" for="publishNew">Công bố cho học viên ngay</label></div>
 </div>
 <div class="modal-footer"><button class="btn btn-secondary" type="button" data-bs-dismiss="modal">Hủy</button><button class="btn btn-success" type="submit">Lưu tài liệu</button></div>
</form></div></div></div>
<div class="teacher-card table-responsive"><table class="table align-middle mb-0">
<thead class="table-light"><tr><th>Tiêu đề</th><th>Lớp</th><th>Ngày cập nhật</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>
@if (!Model.Any()) { <tr><td colspan="5" class="text-center p-4 text-muted">Chưa có tài liệu. Chọn “Tải tài liệu mới” để bắt đầu.</td></tr> }
@foreach (var item in Model) {
<tr data-document-id="@item.DocumentId"><td class="fw-semibold">@item.Title</td><td>@item.Class.ClassName</td><td>@((item.UpdatedAt ?? item.UploadedAt).ToString("dd/MM/yyyy HH:mm"))</td>
<td><span class="badge @(item.IsPublished ? "bg-success" : "bg-secondary")">@(item.IsPublished ? "Đã công bố" : "Bản nháp")</span></td>
<td><div class="d-flex flex-wrap gap-2">
 <a asp-action="Download" asp-route-id="@item.DocumentId" class="btn btn-sm btn-outline-primary">Tải về</a>
 <a asp-action="Edit" asp-route-id="@item.DocumentId" class="btn btn-sm btn-outline-success">Sửa</a>
 <form asp-action="SetPublished" method="post">@Html.AntiForgeryToken()<input type="hidden" name="id" value="@item.DocumentId"/><input type="hidden" name="published" value="@((!item.IsPublished).ToString().ToLowerInvariant())"/><button class="btn btn-sm btn-outline-secondary">@(item.IsPublished ? "Ẩn" : "Công bố")</button></form>
 <form asp-action="Delete" asp-route-id="@item.DocumentId" method="post" onsubmit="return confirm('Xóa tài liệu này?');">@Html.AntiForgeryToken()<button class="btn btn-sm btn-outline-danger">Xóa</button></form>
</div></td></tr>
}
</tbody></table></div>
''')
write('Areas/Teacher/Views/Document/Edit.cshtml','''
@model WedEnglishApp.Models.ClassDocument
@{ ViewData["Title"] = "Sửa tài liệu"; }
<div class="teacher-card p-4 mx-auto" style="max-width:760px">
<h3>Sửa tài liệu</h3><p class="text-muted">Lớp @Model.Class.ClassName. Giữ nguyên tệp hiện tại nếu không chọn tệp thay thế.</p>
<form asp-action="Edit" asp-route-id="@Model.DocumentId" method="post" enctype="multipart/form-data">
 @Html.AntiForgeryToken()
 <label for="editTitle" class="form-label">Tiêu đề</label><input id="editTitle" name="title" value="@Model.Title" maxlength="200" required class="form-control mb-3"/>
 <label for="replaceFile" class="form-label">Thay thế tệp (tùy chọn)</label><input id="replaceFile" name="documentFile" type="file" accept=".pdf,.docx,.pptx,.xlsx,.txt" class="form-control"/>
 <p class="form-text">PDF, DOCX, PPTX, XLSX hoặc TXT, tối đa 10 MB.</p>
 <div class="form-check mb-4"><input asp-for="IsPublished" class="form-check-input"/><label asp-for="IsPublished" class="form-check-label">Công bố cho học viên trong lớp</label></div>
 <button type="submit" class="btn btn-success">Lưu thay đổi</button><a asp-action="Index" class="btn btn-outline-secondary ms-2">Quay lại</a>
</form></div>
''')
write('Views/StudentMaterials/Index.cshtml','''
@model List<WedEnglishApp.Models.ClassDocument>
@{ ViewData["Title"] = "Tài liệu học tập"; }
<div class="container py-4"><div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4"><div><h2>Tài liệu học tập</h2><p class="text-muted">Tài liệu giáo viên đã công bố cho các lớp bạn được xếp.</p></div><a asp-controller="Student" asp-action="MyClasses" class="btn btn-outline-primary">Lớp học của tôi</a></div>
<div class="card table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Tài liệu</th><th>Lớp</th><th>Cập nhật</th><th>Tải về</th></tr></thead><tbody>
@if (!Model.Any()) { <tr><td colspan="4" class="text-center p-4 text-muted">Chưa có tài liệu được công bố cho lớp của bạn.</td></tr> }
@foreach(var d in Model){<tr><td>@d.Title</td><td>@d.Class.ClassName</td><td>@((d.UpdatedAt ?? d.UploadedAt).ToString("dd/MM/yyyy HH:mm"))</td><td><a asp-action="Download" asp-route-id="@d.DocumentId" class="btn btn-sm btn-primary">Tải tài liệu</a></td></tr>}
</tbody></table></div></div>
''')
p=ROOT/'Views/Student/MyClasses.cshtml';s=p.read_text(encoding='utf-8-sig');a=s.index('\n<div');s=s[:a]+'\n<div class="container pt-3"><a href="/Student/Materials" class="btn btn-outline-primary">Tài liệu học tập của tôi</a></div>\n'+s[a:];write('Views/Student/MyClasses.cshtml',s)
edit('Areas/Teacher/Views/Shared/_TeacherLayout.cshtml','<div class="px-3 pt-3 pb-2 text-uppercase','''<a class="sidebar-link" asp-area="Teacher" asp-controller="Report" asp-action="Index"><i class="fa-solid fa-chart-column"></i> Thống kê & Báo cáo</a>
                <div class="px-3 pt-3 pb-2 text-uppercase''')
edit('Areas/Teacher/Views/TeacherDashboard/Index.cshtml','ViewData["Title"] = "Bảng Điều Khiển Giáo Viên";','''ViewData["Title"] = "Bảng Điều Khiển Giáo Viên";
    var activities = ViewBag.RecentActivities as List<WedEnglishApp.Models.TeacherActivity> ?? new();''')
p=ROOT/'Areas/Teacher/Views/TeacherDashboard/Index.cshtml';s=p.read_text(encoding='utf8');s+='''
<div class="teacher-card p-4 mt-4"><div class="d-flex flex-wrap justify-content-between gap-2 mb-3"><h5>Hoạt động gần đây</h5><a asp-controller="Report" asp-action="Index" class="btn btn-sm btn-outline-success">Xem báo cáo</a></div>
@if (!activities.Any()) { <p class="text-muted mb-0">Chưa có hoạt động được ghi nhận. Các thao tác mới về tài liệu, chấm thi và ảnh hồ sơ sẽ xuất hiện tại đây.</p> }
else { <ul class="list-group list-group-flush">@foreach(var a in activities){<li class="list-group-item d-flex flex-wrap justify-content-between gap-2"><span>@a.Description</span><time class="small text-muted">@a.OccurredAt.ToString("dd/MM/yyyy HH:mm:ss")</time></li>}</ul> }
</div>
''';write('Areas/Teacher/Views/TeacherDashboard/Index.cshtml',s)
edit('Areas/Admin/Views/TeacherManager/Index.cshtml','<th>Số Lớp Dạy</th>','<th>Số Lớp Dạy</th><th>Tài khoản</th>')
edit('Areas/Admin/Views/TeacherManager/Index.cshtml','<td class="text-end pe-4">','''<td><span class="badge @(t.UserAccount.IsActive ? "bg-success" : "bg-secondary")">@(t.UserAccount.IsActive ? "Hoạt động" : "Đã khóa")</span></td>
                        <td class="text-end pe-4">
                            <form asp-action="ToggleStatus" asp-route-id="@t.TeacherId" method="post" class="d-inline">@Html.AntiForgeryToken()<button class="btn btn-sm btn-outline-warning mb-1">@(t.UserAccount.IsActive ? "Khóa tài khoản" : "Kích hoạt")</button></form>''')
write('Areas/Teacher/Views/Report/Index.cshtml','''
@model WedEnglishApp.ViewModels.Reports.TeacherReportViewModel
@{ ViewData["Title"] = "Báo cáo giảng dạy"; }
<div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-3"><div><h3>Báo cáo giảng dạy</h3><p>@Model.TeacherName · @Model.From.ToString("dd/MM/yyyy") – @Model.To.ToString("dd/MM/yyyy")</p></div>
<div class="d-flex gap-2 no-print"><a asp-action="Index" asp-route-from="@Model.From.ToString("yyyy-MM-dd")" asp-route-to="@Model.To.ToString("yyyy-MM-dd")" asp-route-format="csv" class="btn btn-outline-success">Xuất CSV</a><button class="btn btn-success" onclick="window.print()">In / Lưu PDF</button></div></div>
<form method="get" class="teacher-card p-3 d-flex flex-wrap align-items-end gap-3 mb-4 no-print"><div><label for="from" class="form-label">Từ ngày</label><input id="from" name="from" type="date" value="@Model.From.ToString("yyyy-MM-dd")" required class="form-control"/></div><div><label for="to" class="form-label">Đến ngày</label><input id="to" name="to" type="date" value="@Model.To.ToString("yyyy-MM-dd")" required class="form-control"/></div><button class="btn btn-success">Xem báo cáo</button></form>
<div class="row g-3 mb-4"><div class="col-sm-3"><div class="teacher-card p-3">Lớp trong kỳ<strong class="d-block fs-3">@Model.Classes.Count</strong></div></div><div class="col-sm-3"><div class="teacher-card p-3">Bài đã chấm<strong class="d-block fs-3">@Model.Graded / @Model.Tests.Count</strong></div></div><div class="col-sm-3"><div class="teacher-card p-3">Điểm trung bình<strong class="d-block fs-3">@(Model.AverageScore?.ToString("0.##") ?? "—")</strong></div></div><div class="col-sm-3"><div class="teacher-card p-3">Hoạt động trong kỳ<strong class="d-block fs-3">@Model.ActivityCount</strong></div></div></div>
<div class="teacher-card p-3 mb-4"><h5>Tổng hợp lớp phụ trách</h5><p class="small text-muted">Các lớp có thời gian giao với kỳ đã chọn; sĩ số và tài liệu là số hiện tại của lớp.</p><div class="table-responsive"><table class="table"><thead><tr><th>Lớp</th><th>Khóa học</th><th>Phòng</th><th>Trạng thái</th><th>Sĩ số</th><th>Tài liệu / Công bố</th></tr></thead><tbody>
@if (!Model.Classes.Any()){<tr><td colspan="6">Không có lớp phù hợp với kỳ đã chọn.</td></tr>}
@foreach(var c in Model.Classes){<tr><td>@c.Name</td><td>@c.Program</td><td>@c.Room</td><td>@c.Status</td><td>@c.Students</td><td>@c.Documents / @c.Published</td></tr>}
</tbody></table></div></div>
<div class="teacher-card p-3"><h5>Kết quả kiểm tra theo ngày thi</h5><div class="table-responsive"><table class="table"><thead><tr><th>Mã bài</th><th>Học viên</th><th>Ngày thi</th><th>Điểm</th><th>Cấp độ đề xuất</th><th>Trạng thái</th></tr></thead><tbody>
@if(!Model.Tests.Any()){<tr><td colspan="6">Không có bài kiểm tra trong kỳ.</td></tr>}
@foreach(var t in Model.Tests){<tr><td>@t.Id</td><td>@t.Student</td><td>@t.Date.ToString("dd/MM/yyyy")</td><td>@(t.Score?.ToString("0.##") ?? "Chưa chấm")</td><td>@t.Level</td><td>@t.Status</td></tr>}
</tbody></table></div></div>
@section Styles {<style>@@media print{#sidebar,.teacher-header,footer,.no-print{display:none!important}.portal-shell{display:block!important}.main-content,.portal-body{margin:0!important;padding:0!important;width:100%!important}.teacher-card{box-shadow:none}.table-responsive{overflow:visible}tr{break-inside:avoid}thead{display:table-header-group}}</style>}
''')
write('Areas/Admin/Views/Report/Index.cshtml','''
@model WedEnglishApp.ViewModels.Reports.AdminReportViewModel
@{ ViewData["Title"] = "Báo cáo thu học phí"; var counts = ViewBag.DataCounts as Dictionary<string,int> ?? new(); var registrationStates=ViewBag.RegistrationStates as Dictionary<string,int> ?? new();var paymentStates=ViewBag.PaymentStates as Dictionary<string,int> ?? new(); }
<div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-3"><div><h3>Báo cáo thu học phí năm @Model.Year</h3><p class="text-muted">Khoản thu đã xác nhận, gồm cả chứng từ còn lưu của đơn trong thùng rác.</p></div><div class="d-flex gap-2 no-print"><a asp-action="Index" asp-route-year="@Model.Year" asp-route-format="csv" class="btn btn-outline-primary">Xuất CSV</a><button class="btn btn-primary" onclick="window.print()">In / Lưu PDF</button></div></div>
<form method="get" class="d-flex flex-wrap gap-2 align-items-center mb-3 no-print"><label for="year">Năm</label><input id="year" name="year" type="number" min="2000" max="2100" value="@Model.Year" required class="form-control" style="max-width:140px"/><button class="btn btn-primary">Xem báo cáo</button><a asp-controller="Dashboard" asp-action="Index" asp-route-year="@Model.Year" class="btn btn-outline-secondary">Biểu đồ</a></form>
<div class="alert alert-info">Khoản thu mới dùng thời điểm xác nhận ConfirmedAt. Chứng từ cũ chưa có thời điểm này dùng PaymentDate đang lưu; dữ liệu lịch sử không bị sửa lại.</div>
<div class="admin-card p-3 mb-4"><h4>Tổng đã thu: <span data-total-revenue="@Model.Revenue.ToString(System.Globalization.CultureInfo.InvariantCulture)">@Model.Revenue.ToString("N0") VNĐ</span></h4><div class="table-responsive"><table class="table"><thead><tr><th>Tháng</th><th>Số biên lai</th><th>Số tiền (VNĐ)</th></tr></thead><tbody>@foreach(var m in Model.Months){<tr><td>@m.Month</td><td>@m.Receipts</td><td>@m.Amount.ToString("N0")</td></tr>}</tbody></table></div></div>
<div class="admin-card p-3 mb-4"><h5>Chi tiết chứng từ đã thu</h5><div class="table-responsive"><table class="table"><thead><tr><th>Biên lai</th><th>Ngày ghi nhận</th><th>Chương trình</th><th>Số tiền</th><th>Cơ sở thời gian</th></tr></thead><tbody>
@if(!Model.Receipts.Any()){<tr><td colspan="5">Chưa có khoản thu trong năm đã chọn.</td></tr>}
@foreach(var r in Model.Receipts){<tr><td>#PAY-@r.Id</td><td>@r.Date.ToString("dd/MM/yyyy HH:mm")</td><td>@r.Program</td><td>@r.Amount.ToString("N0")</td><td>@(r.LegacyDate ? "PaymentDate lịch sử" : "Ngày xác nhận thu")</td></tr>}
</tbody></table></div></div>
<div class="admin-card p-3"><h5>Độ bao phủ dữ liệu hiện tại</h5><p class="small text-muted">Số bản ghi thực trong CSDL, gồm dữ liệu lịch sử và đã xóa mềm; không phải số tình huống đã kiểm thử.</p><div class="row g-3"><div class="col-md-6"><table class="table table-sm"><thead><tr><th>Bảng</th><th>Số bản ghi</th></tr></thead><tbody>@foreach(var c in counts){<tr><td>@c.Key</td><td>@c.Value</td></tr>}</tbody></table></div><div class="col-md-6"><h6>Trạng thái ghi danh</h6><ul>@foreach(var c in registrationStates){<li>@c.Key: @c.Value</li>}</ul><h6>Trạng thái học phí</h6><ul>@foreach(var c in paymentStates){<li>@c.Key: @c.Value</li>}</ul></div></div></div>
@section Styles{<style>@@media print{#sidebar,header,footer,.no-print{display:none!important}.portal-shell{display:block!important}.main-content,.portal-body{margin:0!important;padding:0!important;width:100%!important}.admin-card{box-shadow:none}.table-responsive{overflow:visible}tr{break-inside:avoid}thead{display:table-header-group}}</style>}
''')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','decimal totalRevenue =','var report = (WedEnglishApp.ViewModels.Reports.AdminReportViewModel)ViewBag.Report;\n    decimal totalRevenue =')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','Theo dõi thời gian thực về quy mô đào tạo, tỷ lệ lấp đầy lớp và hoạt động tài chính','Quy mô đào tạo, sĩ số lớp và học phí đã xác nhận theo dữ liệu hiện tại')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','<div class="d-flex gap-2">','''<div class="d-flex flex-wrap gap-2">
        <a asp-controller="Report" asp-action="Index" asp-route-year="@report.Year" class="btn btn-outline-primary btn-sm">Báo cáo / Xuất dữ liệu</a>''')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','>2026</span>','>@report.Year</span>')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','100% Đạt chuẩn CELTA/TESOL','Theo hồ sơ giáo viên trong hệ thống')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','Thống kê học phí các tháng gần nhất năm 2026','Học phí đã xác nhận trong 12 tháng năm @report.Year')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','Thị Phần Khóa Học','Phân Bổ Ghi Danh')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','Tỷ lệ quan tâm theo từng chương trình','Số đơn chưa hủy, chưa xóa theo chương trình trong năm @report.Year')
edit('Areas/Admin/Views/Dashboard/Index.cshtml',"labels: ['Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10 (Hiện tại)'],",'labels: @Html.Raw(System.Text.Json.JsonSerializer.Serialize(report.Months.Select(m => "Tháng " + m.Month))),')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','data: [15000000, 22000000, 28500000, 31000000, 35000000, @totalRevenue],','data: @Html.Raw(System.Text.Json.JsonSerializer.Serialize(report.Months.Select(m => m.Amount))),')
edit('Areas/Admin/Views/Dashboard/Index.cshtml',"labels: ['IELTS Master', 'TOEIC Cấp Tốc', 'Giao Tiếp Phản Xạ', 'Business English', 'Cambridge'],",'labels: @Html.Raw(System.Text.Json.JsonSerializer.Serialize(report.Programs.Select(p => p.Name))),')
edit('Areas/Admin/Views/Dashboard/Index.cshtml','data: [35, 25, 20, 10, 10],','data: @Html.Raw(System.Text.Json.JsonSerializer.Serialize(report.Programs.Select(p => p.Count))),')
p=ROOT/'Areas/Admin/Views/Dashboard/Index.cshtml';s=p.read_text(encoding='utf8');at=s.index('<!-- TOP PERFORMANCE');s=s[:at]+'''<form method="get" class="d-flex flex-wrap align-items-center gap-2 mb-3"><label for="dashboardYear">Năm báo cáo</label><input id="dashboardYear" type="number" min="2000" max="2100" name="year" value="@report.Year" class="form-control" style="max-width:140px"/><button class="btn btn-outline-primary">Áp dụng</button><span class="small text-muted">Khoản thu cũ dùng PaymentDate; khoản mới dùng ngày xác nhận.</span></form>
'''+s[at:];write('Areas/Admin/Views/Dashboard/Index.cshtml',s)
print('Added document, report, download and account-state interfaces.')
