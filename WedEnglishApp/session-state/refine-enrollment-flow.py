from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
s=r('ViewModels/Enrollment/CourseEnrollmentViewModel.cs');s=s.replace('    public int[] PreferredDays { get; set; } = [];\n    public int? DesiredTeacherId { get; set; }','''    [Required(ErrorMessage = "Chọn lịch học Thứ 2–4–6 hoặc Thứ 3–5–7.")]
    public string SchedulePattern { get; set; } = string.Empty;''').replace('    public List<Teacher> Teachers { get; set; } = [];\n','');w('ViewModels/Enrollment/CourseEnrollmentViewModel.cs',s)
w('Services/EnrollmentSchedule.cs','''namespace WedEnglishApp.Services;

public static class EnrollmentSchedule
{
    public static string? GetDays(string? pattern) => pattern switch
    {
        "246" => "2,4,6",
        "357" => "3,5,7",
        _ => null
    };
}
''')
s=r('Controllers/EnrollmentController.cs');a=s.index('        model.Teachers =');b=s.index('        return model.Student',a);s=s[:a]+s[b:];a=s.index('        if (model.PreferredDays.Length');b=s.index('        if (!new[] { "Cash"',a);s=s[:a]+'''        var preferredDays = EnrollmentSchedule.GetDays(model.SchedulePattern);
        if (preferredDays == null)
            ModelState.AddModelError(nameof(model.SchedulePattern), "Chọn một trong hai lịch học: Thứ 2–4–6 hoặc Thứ 3–5–7.");
'''+s[b:];a=s.index('        if (model.DesiredTeacherId.HasValue');b=s.index('        if (model.StudentPhoto',a);s=s[:a]+s[b:];s=s.replace('PreferredDays = string.Join(",", model.PreferredDays.Distinct().Order()),\n            DesiredTeacherId = model.DesiredTeacherId, Notes = model.Notes?.Trim(), Status = "Pending"','PreferredDays = preferredDays,\n            Notes = model.Notes?.Trim(), Status = "Pending"');s=s.replace('return RedirectToAction("MyClasses", "Student");\n    }\n}', '''return RedirectToAction(nameof(Payment), new { registrationId = registration.RegistrationId });
    }

    public async Task<IActionResult> Payment(int registrationId)
    {
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var accountId);
        var registration = await context.Registrations
            .Include(r => r.Program).Include(r => r.Payment)
            .Include(r => r.Student).ThenInclude(s => s.UserAccount)
            .FirstOrDefaultAsync(r => r.RegistrationId == registrationId && r.Student.AccountId == accountId && !r.IsDeleted);
        if (registration == null || registration.Status == "Cancelled") return NotFound();
        return View(registration);
    }
}''');w('Controllers/EnrollmentController.cs',s)
w('Views/Enrollment/Checkout.cshtml','''@model WedEnglishApp.ViewModels.Enrollment.CourseEnrollmentViewModel
@{ ViewData["Title"] = "Đăng ký khóa học"; }
<div class="container py-5">
    <div class="mb-4">
        <h2 class="fw-bold mb-2">Đăng ký khóa học</h2>
        <p class="text-primary fs-5 mb-2">@Model.Course!.ProgramName</p>
        <p class="text-muted mb-0">Chọn lịch mong muốn, xác nhận đăng ký và hoàn tất hướng dẫn đóng học phí. Trung tâm sẽ xếp lớp và thông báo lịch chính thức.</p>
    </div>
    <ol class="d-flex flex-wrap gap-4 list-unstyled small mb-4" aria-label="Các bước đăng ký">
        <li class="text-primary fw-bold">1. Chọn lịch học</li>
        <li class="text-primary fw-bold">2. Xác nhận đăng ký</li>
        <li class="text-muted">3. Đóng học phí</li>
    </ol>
    <form asp-action="Confirm" asp-route-authRole="Student" method="post" enctype="multipart/form-data">
        <div asp-validation-summary="All" class="text-danger mb-3" role="alert"></div>
        <input asp-for="ProgramId" type="hidden" />
        <div class="row g-4">
            <div class="col-lg-8">
                <div class="card border-0 shadow-sm p-4">
                    <h5 class="fw-bold mb-3">Lịch học mong muốn</h5>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label asp-for="EarliestStartDate" class="form-label">Có thể bắt đầu từ ngày <span class="text-danger">*</span></label>
                            <input asp-for="EarliestStartDate" type="date" min="@DateTime.Today.ToString("yyyy-MM-dd")" class="form-control" required />
                            <span asp-validation-for="EarliestStartDate" class="text-danger small"></span>
                            <div class="form-text">Trung tâm sẽ chọn lớp khai giảng từ ngày này trở đi.</div>
                        </div>
                        <div class="col-md-6">
                            <label asp-for="PreferredSession" class="form-label">Buổi học <span class="text-danger">*</span></label>
                            <select asp-for="PreferredSession" class="form-select">
                                <option value="Morning">Buổi sáng (06:00–12:00)</option>
                                <option value="Afternoon">Buổi chiều (12:00–18:00)</option>
                                <option value="Evening">Buổi tối (18:00–22:00)</option>
                                <option value="Any">Linh hoạt các buổi</option>
                            </select>
                        </div>
                        <fieldset class="col-12">
                            <legend class="fs-6 mb-2">Lịch trong tuần <span class="text-danger">*</span></legend>
                            <div class="row g-2">
                                <div class="col-sm-6">
                                    <input asp-for="SchedulePattern" type="radio" value="246" id="schedule-246" class="btn-check" required />
                                    <label for="schedule-246" class="btn btn-outline-primary w-100 py-3">Thứ 2 – Thứ 4 – Thứ 6</label>
                                </div>
                                <div class="col-sm-6">
                                    <input asp-for="SchedulePattern" type="radio" value="357" id="schedule-357" class="btn-check" required />
                                    <label for="schedule-357" class="btn btn-outline-primary w-100 py-3">Thứ 3 – Thứ 5 – Thứ 7</label>
                                </div>
                            </div>
                            <span asp-validation-for="SchedulePattern" class="text-danger small"></span>
                            <div class="form-text">Đây là lịch mong muốn để trung tâm tham khảo khi xếp lớp.</div>
                        </fieldset>
                        <div class="col-12">
                            <label asp-for="Notes" class="form-label">Ghi chú thêm (không bắt buộc)</label>
                            <textarea asp-for="Notes" maxlength="500" rows="3" class="form-control" placeholder="Ví dụ: chỉ có thể học sau 19 giờ, muốn học cùng bạn..."></textarea>
                        </div>
                    </div>
                    <details class="mt-4">
                        <summary class="text-secondary">Thông tin học viên và ảnh hồ sơ</summary>
                        <p class="small mt-3 mb-2"><strong>@Model.Student!.UserAccount.FullName</strong> · @Model.Student.UserAccount.Email</p>
                        <label asp-for="StudentPhoto" class="form-label small">Cập nhật ảnh hồ sơ (không bắt buộc)</label>
                        <input asp-for="StudentPhoto" type="file" accept=".jpg,.jpeg,.png,.webp" class="form-control" />
                        <div class="form-text">JPG, PNG hoặc WEBP, tối đa 5 MB.</div>
                    </details>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card border-0 shadow-sm p-4">
                    <h5 class="fw-bold mb-3">Học phí khóa học</h5>
                    <p class="mb-2">@Model.Course.ProgramName</p>
                    <p class="small text-muted">Thời lượng: @Model.Course.DurationWeeks tuần</p>
                    <div class="d-flex justify-content-between align-items-center border-top border-bottom py-3 mb-4 gap-2">
                        <span>Tổng học phí</span><strong class="text-danger fs-5">@Model.Course.TuitionFee.ToString("N0") đ</strong>
                    </div>
                    <fieldset>
                        <legend class="fs-6 fw-semibold">Cách đóng học phí</legend>
                        <div class="form-check mb-3">
                            <input asp-for="PaymentMethod" type="radio" value="VietQR" id="payment-qr" class="form-check-input" />
                            <label for="payment-qr" class="form-check-label">Chuyển khoản VietQR</label>
                            <div class="small text-muted">Nhận mã QR, số tiền và nội dung chuyển khoản riêng sau khi xác nhận đăng ký.</div>
                        </div>
                        <div class="form-check mb-3">
                            <input asp-for="PaymentMethod" type="radio" value="Cash" id="payment-cash" class="form-check-input" />
                            <label for="payment-cash" class="form-check-label">Đóng tại trung tâm</label>
                            <div class="small text-muted">Nộp học phí tại quầy và cung cấp mã đăng ký.</div>
                        </div>
                    </fieldset>
                    <p class="small text-muted">Sau khi gửi, bạn sẽ đến trang hướng dẫn đóng học phí. Trung tâm xác nhận khoản thu và xếp lớp riêng.</p>
                    <button type="submit" class="btn btn-primary w-100 py-2 fw-semibold">Xác nhận đăng ký và tiếp tục</button>
                    <a asp-controller="Program" asp-action="Detail" asp-route-id="@Model.ProgramId" class="btn btn-link mt-2">Quay lại khóa học</a>
                </div>
            </div>
        </div>
    </form>
</div>
''')
w('Views/Enrollment/Payment.cshtml','''@model WedEnglishApp.Models.Registration
@{ ViewData["Title"] = "Đóng học phí"; }
<div class="container py-5"><div class="row justify-content-center"><div class="col-lg-8">
    <h2 class="fw-bold">@(Model.Payment?.Status == "Paid" ? "Đã xác nhận học phí" : "Hoàn tất đăng ký và đóng học phí")</h2>
    <p class="text-success">Đã tiếp nhận đăng ký #REG-@Model.RegistrationId của @Model.Student.UserAccount.FullName.</p>
    <div class="card border-0 shadow-sm p-4 mb-4">
        <h5>@Model.Program.ProgramName</h5>
        @await Html.PartialAsync("_EnrollmentPreferences", Model)
        <hr />
        @if (Model.Payment?.PaymentMethod == "Cash" && Model.Payment.Status != "Paid")
        {
            <h5>Đóng học phí tại trung tâm</h5>
            <p>Vui lòng cung cấp mã <strong>#REG-@Model.RegistrationId</strong> và họ tên tại quầy để đóng học phí. Nhân viên sẽ xác nhận khoản thu vào tài khoản của bạn.</p>
        }
        @await Html.PartialAsync("_RegistrationPayment", Model)
        @if (Model.Payment?.Status == "Paid")
        {
            <a asp-controller="Student" asp-action="PrintReceipt" asp-route-id="@Model.Payment.PaymentId" class="btn btn-outline-primary align-self-start">Xem biên lai học phí</a>
        }
        else
        {
            <p class="small text-muted mt-3 mb-0">Nếu đã chuyển khoản, vui lòng chờ trung tâm đối soát. Trạng thái chỉ đổi thành đã thanh toán sau khi khoản thu được xác nhận.</p>
        }
    </div>
    <div class="d-flex flex-wrap gap-2">
        <a asp-controller="Student" asp-action="MyClasses" class="btn btn-primary">Theo dõi đăng ký và xếp lớp</a>
        <a asp-controller="Student" asp-action="MyPayments" class="btn btn-outline-primary">Lịch sử học phí</a>
    </div>
</div></div></div>
''')
# Pending requests retain a direct route back to their own payment instructions.
s=r('Views/Shared/_RegistrationPayment.cshtml');s=s.replace('<p class="small">Học phí:', '''@if (Model.Status != "Cancelled" && Model.Payment.Status != "Paid" && ViewContext.RouteData.Values["action"]?.ToString() != "Payment") {
<a asp-controller="Enrollment" asp-action="Payment" asp-route-registrationId="@Model.RegistrationId" asp-route-authRole="Student" class="btn btn-sm btn-outline-primary mb-2">Xem hướng dẫn đóng học phí</a>
}
<p class="small">Học phí:''');w('Views/Shared/_RegistrationPayment.cshtml',s)
