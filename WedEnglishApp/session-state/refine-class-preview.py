from pathlib import Path
base=Path('WedEnglishApp')
def edit(f,a,b):
 p=base/f;s=p.read_text(encoding='utf8');assert a in s,f;p.write_text(s.replace(a,b),encoding='utf8')
edit('Controllers/HomeController.cs','            var model = new HomeViewModel','            var today = DateTime.Today;\n            var model = new HomeViewModel')
edit('Controllers/HomeController.cs','(c.Status == "Planning" || c.Status == "InProgress"))\n                    .OrderBy(c => c.StartDate).Take(4)', '(c.Status == "Planning" || c.Status == "InProgress") && c.EndDate >= today && c.EndDate >= c.StartDate)\n                    .OrderBy(c => c.StartDate < today).ThenBy(c => c.StartDate).Take(4)')
edit('Controllers/ProgramController.cs','            var program = await _context.Programs','            var today = DateTime.Today;\n            var program = await _context.Programs')
edit('Controllers/ProgramController.cs','(c.Status == "Planning" || c.Status == "InProgress")))','(c.Status == "Planning" || c.Status == "InProgress") && c.EndDate >= today && c.EndDate >= c.StartDate))')
edit('Views/Home/Index.cshtml','''<section class="py-5 bg-light"><div class="container"><h3>Các lớp hiện có</h3>
<p>Tham khảo lịch học của trung tâm. Khi đăng ký khóa học, bạn chỉ cần gửi lịch mong muốn; Admin sẽ xếp lớp sau.</p>
@await Html.PartialAsync("_AvailableClasses", Model.UpcomingClasses)
</div></section>''','''<section class="py-5 bg-light" id="class-schedule">
    <div class="container">
        <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
            <div>
                <h3 class="fw-bold mb-2">Lịch lớp tại trung tâm</h3>
                <p class="text-muted mb-0">Tham khảo các lớp sắp khai giảng và đang học.</p>
            </div>
            <a asp-controller="Program" asp-action="Index" class="btn btn-primary">Chọn khóa học</a>
        </div>
        @await Html.PartialAsync("_AvailableClasses", Model.UpcomingClasses)
        <p class="small text-muted mt-4 mb-0">Bạn đăng ký khóa học và gửi thời gian có thể học. Trung tâm sẽ liên hệ, xếp lớp phù hợp và xác nhận lịch học chính thức.</p>
    </div>
</section>''')
edit('Views/Program/Detail.cshtml','''<div class="mb-4"><h4>Các lớp hiện có để tham khảo</h4>
                <p class="text-muted">Không cần chọn lớp khi đăng ký. Admin sẽ xếp lớp theo nguyện vọng của bạn.</p>
                @if (Model.Classes.Any()) { @await Html.PartialAsync("_AvailableClasses", Model.Classes) }
                else { <p>Trung tâm đang tiếp nhận đăng ký khóa học và sắp xếp lớp mới.</p> }
            </div>''','''<div class="mb-4">
                <h4 class="fw-bold">Lịch lớp tham khảo</h4>
                <p class="text-muted">Các lớp của khóa học này. Lớp chính thức của bạn được trung tâm xác nhận sau khi tiếp nhận nguyện vọng.</p>
                @await Html.PartialAsync("_AvailableClasses", Model.Classes)
            </div>''')
(base/'Views/Shared/_AvailableClasses.cshtml').write_text(r'''@model IEnumerable<WedEnglishApp.Models.CourseClass>
@{
    var today = DateTime.Today;
    var current = Model.Where(c => !c.IsDeleted && c.EndDate.Date >= today && c.EndDate >= c.StartDate
        && (c.Status == "Planning" || c.Status == "InProgress")).ToList();
    var upcoming = current.Where(c => c.StartDate.Date >= today).OrderBy(c => c.StartDate).ToList();
    var ongoing = current.Where(c => c.StartDate.Date < today).OrderBy(c => c.EndDate).ToList();
}
@if (!current.Any())
{
    <p class="text-muted py-3 mb-0">Lịch lớp đang được cập nhật. Bạn vẫn có thể đăng ký khóa học và gửi thời gian mong muốn.</p>
}
@foreach (var group in new[] { upcoming, ongoing })
{
    if (!group.Any()) { continue; }
    var isUpcoming = group == upcoming;
    <div class="mb-4">
        <h5 class="fw-semibold mb-3">@(isUpcoming ? "Sắp khai giảng" : "Đang học")</h5>
        <div class="row g-3">
            @foreach (var cls in group)
            {
                <div class="col-lg-6">
                    <article class="card border-0 shadow-sm p-4 h-100">
                        <div class="mb-3">
                            <span class="badge @(isUpcoming ? "bg-primary-subtle text-primary" : "bg-success-subtle text-success") mb-2">
                                @(isUpcoming ? "Sắp khai giảng" : "Đang học")
                            </span>
                            <h6 class="fw-bold mb-1">
                                <a asp-controller="Program" asp-action="Detail" asp-route-id="@cls.ProgramId" class="text-decoration-none">@cls.Program.ProgramName</a>
                            </h6>
                            <div class="small text-muted">Mã lớp: @cls.ClassName</div>
                        </div>
                        <div class="small mb-2">
                            <i class="fa-regular fa-calendar me-2 text-primary" aria-hidden="true"></i>
                            @(isUpcoming ? "Khai giảng" : "Đã bắt đầu"): <strong>@cls.StartDate.ToString("dd/MM/yyyy")</strong>
                            <span class="text-muted">· Kết thúc @cls.EndDate.ToString("dd/MM/yyyy")</span>
                        </div>
                        <div class="small mb-2">
                            <i class="fa-regular fa-clock me-2 text-primary" aria-hidden="true"></i>
                            @if (cls.Schedules.Any())
                            {
                                @string.Join(" · ", cls.Schedules.OrderBy(s => s.DayOfWeek).Select(s => $"{(s.DayOfWeek == 8 ? "CN" : $"Thứ {s.DayOfWeek}")}: {s.StartTime:hh\:mm}–{s.EndTime:hh\:mm}"))
                            }
                            else
                            {
                                <span class="text-muted">Giờ học đang được cập nhật</span>
                            }
                        </div>
                        @if (!string.IsNullOrWhiteSpace(cls.Room))
                        {
                            <div class="small text-muted"><i class="fa-solid fa-location-dot me-2" aria-hidden="true"></i>Địa điểm: @cls.Room</div>
                        }
                    </article>
                </div>
            }
        </div>
    </div>
}
''',encoding='utf8')
