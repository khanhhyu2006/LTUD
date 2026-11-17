// =================================================================================================
// CONTROLLER: PlacementTestController - XỬ LÝ NGHIỆP VỤ THI XẾP LỚP ĐẦU VÀO CỦA HỌC VIÊN
// Quyền truy cập: [Authorize(Roles = "Student")] - Dành riêng cho học viên đã đăng nhập
// Nghiệp vụ: Đăng ký lịch thi xếp lớp (ngày thi, ca thi), xem lịch sử và kết quả điểm số/lớp đề xuất
// =================================================================================================

using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;

namespace WedEnglishApp.Controllers
{
    [Authorize(Roles = "Student")] // Bắt buộc đăng nhập với quyền Student
    public class PlacementTestController : Controller
    {
        private readonly ApplicationDbContext _context; // Đối tượng truy xuất cơ sở dữ liệu

        public PlacementTestController(ApplicationDbContext context)
        {
            _context = context;
        }

        // =============================================================================================
        // HÀM 1: GET /PlacementTest/BookTest - HIỂN THỊ TRANG ĐĂNG KÝ VÀ LỊCH SỬ THI XẾP LỚP
        // =============================================================================================
        public async Task<IActionResult> BookTest()
        {
            // Lấy AccountId của học viên từ Cookie Claims
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return RedirectToAction("Login", "Account");

            // Truy vấn thông tin học viên kèm danh sách các bài thi xếp lớp đã đăng ký
            // Kèm thông tin Giảng viên phụ trách chấm thi
            var student = await _context.Students
                .Include(s => s.UserAccount)
                .Include(s => s.PlacementTests.Where(t => !t.IsDeleted)).ThenInclude(t => t.ExamSession)
                .Include(s => s.PlacementTests.Where(t => !t.IsDeleted))
                    .ThenInclude(pt => pt.EvaluatedByTeacher)
                        .ThenInclude(t => t!.UserAccount)
                .FirstOrDefaultAsync(s => s.AccountId == accountId);

            if (student == null) return RedirectToAction("Login", "Account");

            return View(student); // Trả về giao diện BookTest.cshtml
        }

        // =============================================================================================
        // HÀM 2: POST /PlacementTest/BookTest - XỬ LÝ LƯU ĐƠN ĐĂNG KÝ LỊCH THI XẾP LỚP
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken] // Chống tấn công giả mạo CSRF
        public async Task<IActionResult> BookTest(DateTime testDate, string testTime)
        {
            // Lấy AccountId từ Cookie Claims
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return RedirectToAction("Login", "Account");

            var student = await _context.Students.FirstOrDefaultAsync(s => s.AccountId == accountId);
            if (student == null) return RedirectToAction("Login", "Account");

            // Kiểm tra tính hợp lệ: Ngày thi xếp lớp không được chọn ngày trong quá khứ
            if (!ModelState.IsValid || testDate.Date < DateTime.Today.AddDays(1))
            {
                TempData["ErrorMessage"] = "Ngày kiểm tra xếp lớp phải từ ngày mai trở đi.";
                return RedirectToAction(nameof(BookTest));
            }

            if (!new[] { "08:30 AM", "10:00 AM", "02:00 PM", "04:00 PM", "06:30 PM" }.Contains(testTime))
            {
                TempData["ErrorMessage"] = "Khung giờ mong muốn không hợp lệ.";
                return RedirectToAction(nameof(BookTest));
            }
            if (await _context.PlacementTests.AnyAsync(t => t.StudentId == student.StudentId && !t.IsDeleted && t.Status == "Pending"))
            {
                TempData["ErrorMessage"] = "Bạn đã có đăng ký thi chưa hoàn tất. Hãy theo dõi lịch thi trong tài khoản.";
                return RedirectToAction(nameof(BookTest));
            }
            // Tạo bản ghi PlacementTest mới với trạng thái "Pending" (Chờ thi / Chờ chấm)
            var test = new PlacementTest
            {
                StudentId = student.StudentId,
                RequestedDate = testDate.Date, RequestedTime = testTime, Room = null,
                TestDate = testDate,
                TestTime = string.IsNullOrWhiteSpace(testTime) ? "09:00 AM" : testTime,
                Status = "Pending"
            };

            _context.PlacementTests.Add(test);
            await _context.SaveChangesAsync(); // Lưu vào SQL Server

            TempData["SuccessMessage"] = "Đã tiếp nhận đăng ký. Admin sẽ xếp bạn vào phòng thi và phân công giáo viên chấm ca thi.";
            return RedirectToAction(nameof(BookTest));
        }
    }
}
