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

            payment.Status = "Paid";
            // Payment confirmation never assigns a class.
            if (string.IsNullOrEmpty(payment.TransactionCode))
            {
                payment.TransactionCode = $"MANUAL{DateTime.Now:yyyyMMddHHmmss}";
            }

            await _context.SaveChangesAsync();
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

            if (payment == null || payment.Registration.IsDeleted || payment.Registration.Status == "Cancelled") return NotFound();

            return View("~/Views/Student/PrintReceipt.cshtml", payment);
        }
    }
}
