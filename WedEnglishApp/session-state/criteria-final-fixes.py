exec(open('session-state/implement-criteria.py',encoding='utf-8-sig').read().split("write('Models/TeacherActivity.cs'")[0])
p=ROOT/'Areas/Admin/Controllers/PaymentAdminController.cs';s=p.read_text(encoding='utf8');a=s.index('            if (payment.Status != "Paid")');b=s.index('            TempData["SuccessMessage"]',a)
s=s[:a]+'''            var now = DateTime.Now;
            var code = $"MANUAL{now:yyyyMMddHHmmss}";
            // Conditional update preserves the first confirmation even for concurrent requests.
            await _context.Payments.Where(p => p.PaymentId == id && p.Status != "Paid" && !p.Registration.IsDeleted && p.Registration.Status != "Cancelled")
                .ExecuteUpdateAsync(update => update.SetProperty(p => p.Status, "Paid")
                    .SetProperty(p => p.ConfirmedAt, (DateTime?)now)
                    .SetProperty(p => p.TransactionCode, p => p.TransactionCode == null || p.TransactionCode == "" ? code : p.TransactionCode));
''' + s[b:];
a=s.index('public async Task<IActionResult> PrintReceipt');before=s[:a];after=s[a:].replace('if (payment == null ||','if (payment == null || payment.Status != "Paid" ||');write('Areas/Admin/Controllers/PaymentAdminController.cs',before+after)
edit('Controllers/StudentController.cs','.FirstOrDefaultAsync(p => p.PaymentId == id && p.Registration.StudentId == studentId);','.FirstOrDefaultAsync(p => p.PaymentId == id && p.Status == "Paid" && p.Registration.StudentId == studentId);')
edit('Areas/Teacher/Controllers/DocumentController.cs','public async Task<IActionResult> SetPublished(int id, bool published)\n    {','public async Task<IActionResult> SetPublished(int id, bool published)\n    {\n        if (!ModelState.IsValid) return BadRequest("Trạng thái công bố không hợp lệ.");')
edit('Services/ReportingService.cs','c.Registrations.Count(r => !r.IsDeleted && r.Status == "Confirmed")','c.Registrations.Where(r => !r.IsDeleted && r.Status == "Confirmed").Select(r => r.StudentId).Distinct().Count()')
edit('Areas/Admin/Views/TeacherManager/Index.cshtml','table-people"','table-people table-people-accounts"')
p=ROOT/'wwwroot/css/portal-layout.css';s=p.read_text(encoding='utf-8-sig');s+='''
/* A resizing chart must not widen the portal while Chart.js updates its canvas. */
.portal-body .chart-container { min-width: 0; max-width: 100%; overflow: hidden; }
.portal-body .chart-container canvas { max-width: 100%; }
.portal-body .table-people-accounts th:nth-child(1) { width: 20%; }
.portal-body .table-people-accounts th:nth-child(2) { width: 22%; }
.portal-body .table-people-accounts th:nth-child(3) { width: 14%; }
.portal-body .table-people-accounts th:nth-child(4) { width: 15%; }
.portal-body .table-people-accounts th:nth-child(5) { width: 7%; }
.portal-body .table-people-accounts th:nth-child(6) { width: 8%; }
.portal-body .table-people-accounts th:nth-child(7) { width: 14%; }
''';write('wwwroot/css/portal-layout.css',s)
edit('Areas/Admin/Views/Shared/_AdminLayout.cshtml','<div class="px-3 pt-3 pb-2 text-uppercase text-secondary fw-bold" style="font-size: 0.7rem;">Đào tạo','''<a class="sidebar-link" asp-area="Admin" asp-controller="Report" asp-action="Index"><i class="fa-solid fa-chart-column"></i> Báo cáo & Dữ liệu</a>
                <div class="px-3 pt-3 pb-2 text-uppercase text-secondary fw-bold" style="font-size: 0.7rem;">Đào tạo''')
print('Hardened publication validation, confirmation idempotency and chart resizing.')
