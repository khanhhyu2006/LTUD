from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
s=r('ViewModels/Admin/ClassScheduleInput.cs').replace('    [Required] public string SchedulePattern','    public bool AllowKeepExisting { get; set; }\n    [Required] public string SchedulePattern');w('ViewModels/Admin/ClassScheduleInput.cs',s)
w('Areas/Admin/Views/Shared/_ClassScheduleForm.cshtml',r'''@model WedEnglishApp.ViewModels.Admin.ClassScheduleInput
<fieldset class="mb-4"><legend class="fs-6 fw-bold">Lịch học trong tuần</legend><div class="row g-3">
<div class="col-md-6"><label for="class-pattern" class="form-label">Các thứ học <span class="text-danger">*</span></label><select name="SchedulePattern" id="class-pattern" class="form-select" required><option value="">Chọn lịch học</option>@if(Model.AllowKeepExisting) { <option value="Keep" selected="@(Model.SchedulePattern=="Keep")">Giữ lịch cũ hiện có</option> }<option value="246" selected="@(Model.SchedulePattern=="246")">Thứ 2 – Thứ 4 – Thứ 6</option><option value="357" selected="@(Model.SchedulePattern=="357")">Thứ 3 – Thứ 5 – Thứ 7</option></select></div>
<div class="col-md-3"><label for="class-start" class="form-label">Giờ bắt đầu <span class="text-danger">*</span></label><input name="StartTime" id="class-start" type="time" value="@Model.StartTime?.ToString(@"hh\:mm")" class="form-control" required /></div>
<div class="col-md-3"><label for="class-end" class="form-label">Giờ kết thúc <span class="text-danger">*</span></label><input name="EndTime" id="class-end" type="time" value="@Model.EndTime?.ToString(@"hh\:mm")" class="form-control" required /></div>
</div><p class="form-text">Lưu lớp sẽ áp dụng lịch này vào thời khóa biểu học viên và giáo viên trong khoảng ngày khai giảng đến bế giảng.</p></fieldset>
''')
s=r('Areas/Admin/Controllers/ClassManagerController.cs');s=s.replace('            await PopulateClassFormOptionsAsync();\n            return View(new CourseClass','            await PopulateClassFormOptionsAsync();\n            ViewBag.ScheduleForm = new ClassScheduleInput();\n            return View(new CourseClass')
a=s.index('            if (string.IsNullOrEmpty(input.SchedulePattern))');b=s.index('            if (ModelState.IsValid)\n            {\n                _context.Classes.Add(cls);',a);s=s[:a]+'''            ViewBag.ScheduleForm = input;
            var scheduleError = await ClassSchedulePlanner.ValidateAsync(_context, cls, input);
            if (scheduleError != null) ModelState.AddModelError("", scheduleError);
            else cls.Schedules = ClassSchedulePlanner.Create(input);
'''+s[b:]
s=s.replace('var cls = await _context.Classes.FindAsync(id);\n            if (cls == null) return NotFound();\n\n            ViewBag.Programs', '''var cls = await _context.Classes.Include(c => c.Schedules).FirstOrDefaultAsync(c => c.ClassId == id);
            if (cls == null) return NotFound();
            var days = string.Join(",", cls.Schedules.OrderBy(s => s.DayOfWeek).Select(s => s.DayOfWeek));
            ViewBag.ScheduleForm = new ClassScheduleInput
            {
                SchedulePattern = days == "2,4,6" ? "246" : days == "3,5,7" ? "357" : cls.Schedules.Any() ? "Keep" : "",
                AllowKeepExisting = cls.Schedules.Any() && days != "2,4,6" && days != "3,5,7",
                StartTime = cls.Schedules.FirstOrDefault()?.StartTime,
                EndTime = cls.Schedules.FirstOrDefault()?.EndTime
            };
            ViewBag.Programs''')
s=s.replace('public async Task<IActionResult> Edit(int id, CourseClass cls)', 'public async Task<IActionResult> Edit(int id, CourseClass cls, ClassScheduleInput input)')
s=s.replace('            var existing = await _context.Classes.Include(c => c.Registrations).FirstOrDefaultAsync(c => c.ClassId == id && !c.IsDeleted);','            await using var transaction = await _context.Database.BeginTransactionAsync(IsolationLevel.Serializable);\n            var existing = await _context.Classes.Include(c => c.Registrations).Include(c => c.Schedules).FirstOrDefaultAsync(c => c.ClassId == id && !c.IsDeleted);')
a=s.index('            if (ModelState.IsValid)\n            {\n                existing.ClassName');s=s[:a]+'''            input.AllowKeepExisting = existing.Schedules.Any();
            ViewBag.ScheduleForm = input;
            if (input.SchedulePattern != "Keep" || !existing.Schedules.Any())
            {
                var scheduleError = await ClassSchedulePlanner.ValidateAsync(_context, cls, input);
                if (scheduleError != null) ModelState.AddModelError("", scheduleError);
            }
'''+s[a:]
s=s.replace('existing.MaxStudents = cls.MaxStudents; existing.Status = cls.Status;\n                await _context.SaveChangesAsync();','''existing.MaxStudents = cls.MaxStudents; existing.Status = cls.Status;
                if (input.SchedulePattern != "Keep")
                {
                    _context.ClassSchedules.RemoveRange(existing.Schedules);
                    await _context.SaveChangesAsync();
                    existing.Schedules = ClassSchedulePlanner.Create(input);
                }
                await _context.SaveChangesAsync();
                await transaction.CommitAsync();''');w('Areas/Admin/Controllers/ClassManagerController.cs',s)
s=r('Areas/Admin/Views/ClassManager/Create.cshtml');a=s.index('                <fieldset class="mb-4"><legend');b=s.index('                <div class="mb-4">\n                    <label asp-for="Status"',a);s=s[:a]+'''                @await Html.PartialAsync("_ClassScheduleForm", (WedEnglishApp.ViewModels.Admin.ClassScheduleInput)ViewBag.ScheduleForm)

'''+s[b:];w('Areas/Admin/Views/ClassManager/Create.cshtml',s)
s=r('Areas/Admin/Views/ClassManager/Edit.cshtml');s=s.replace('asp-validation-summary="ModelOnly"','asp-validation-summary="All"');a=s.index('                <div class="mb-4">\n                    <label asp-for="Status"');s=s[:a]+'''                @await Html.PartialAsync("_ClassScheduleForm", (WedEnglishApp.ViewModels.Admin.ClassScheduleInput)ViewBag.ScheduleForm)

'''+s[a:];w('Areas/Admin/Views/ClassManager/Edit.cshtml',s)
