using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class PaymentAdminController : Controller
    {
        private readonly ApplicationDbContext _context;

        public PaymentAdminController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: Admin/PaymentAdmin
        public async Task<IActionResult> Index()
        {
            var payments = await _context.Payments
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Student)
                        .ThenInclude(s => s.UserAccount)
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Class)
                        .ThenInclude(c => c.Program)
                .Where(p => !p.Registration.IsDeleted) // Chỉ hiển thị hóa đơn của đăng ký chưa xóa vào thùng rác
                .OrderByDescending(p => p.PaymentDate)
                .ToListAsync();

            return View(payments);
        }

        // POST: Admin/PaymentAdmin/ConfirmPayment
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ConfirmPayment(int id)
        {
            var payment = await _context.Payments
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                .FirstOrDefaultAsync(p => p.PaymentId == id);

            if (payment == null || payment.Registration.IsDeleted || payment.Registration.Status == "Cancelled") return NotFound();

            var now = DateTime.Now;
            var code = $"MANUAL{now:yyyyMMddHHmmss}";
            // Conditional update preserves the first confirmation even for concurrent requests.
            await _context.Payments.Where(p => p.PaymentId == id && p.Status != "Paid" && !p.Registration.IsDeleted && p.Registration.Status != "Cancelled")
                .ExecuteUpdateAsync(update => update.SetProperty(p => p.Status, "Paid")
                    .SetProperty(p => p.ConfirmedAt, (DateTime?)now)
                    .SetProperty(p => p.TransactionCode, p => p.TransactionCode == null || p.TransactionCode == "" ? code : p.TransactionCode));
            TempData["SuccessMessage"] = $"Đã xác nhận thanh toán thành công cho hóa đơn #PAY-{id}!";
            return RedirectToAction(nameof(Index));
        }

        // GET: Admin/PaymentAdmin/PrintReceipt/5
        public async Task<IActionResult> PrintReceipt(int id)
        {
            var payment = await _context.Payments
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Student)
                        .ThenInclude(s => s.UserAccount)
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Class)
                        .ThenInclude(c => c.Program)
                .FirstOrDefaultAsync(p => p.PaymentId == id);

            if (payment == null || payment.Status != "Paid" || payment.Registration.IsDeleted || payment.Registration.Status == "Cancelled") return NotFound();

            return View("~/Views/Student/PrintReceipt.cshtml", payment);
        }
    }
}
