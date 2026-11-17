using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.ViewModels.Auth;

namespace WedEnglishApp.Controllers
{
    // =================================================================================================
    // CONTROLLER: AccountController - XỬ LÝ TOÀN BỘ NGHIỆP VỤ XÁC THỰC VÀ TÀI KHOẢN NGƯỜI DÙNG
    // Bao gồm: Đăng nhập (Login), Đăng ký (Register), Đăng xuất (Logout), Phân quyền Claims, Đổi mật khẩu
    // =================================================================================================
    public class AccountController : Controller
    {
        // Khai báo đối tượng tương tác CSDL thông qua Dependency Injection
        private readonly ApplicationDbContext _context;

        // Constructor nhận ApplicationDbContext được hệ thống DI tự động truyền vào
        public AccountController(ApplicationDbContext context)
        {
            _context = context;
        }

        // =============================================================================================
        // HÀM 1: GET /Account/Login - HIỂN THỊ TRANG ĐĂNG NHẬP
        // =============================================================================================
        [HttpGet]
        public IActionResult Login(string? returnUrl = null)
        {
            // Cho phép mở trang đăng nhập kể cả khi vai trò khác đang hoạt động ở tab khác.
            // Lưu lại đường dẫn mà người dùng muốn truy cập trước khi bị bắt đăng nhập
            ViewData["ReturnUrl"] = returnUrl;
            return View(new LoginViewModel { ReturnUrl = returnUrl });
        }

        // =============================================================================================
        // HÀM 2: POST /Account/Login - TIẾP NHẬN FORM ĐĂNG NHẬP, XÁC THỰC MẬT KHẨU & TẠO COOKIE
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken] // Chống tấn công giả mạo yêu cầu chéo trang (CSRF Attack)
        public async Task<IActionResult> Login(LoginViewModel model)
        {
            // Bước 1: Kiểm tra tính hợp lệ của dữ liệu nhập (đúng định dạng email, không để trống mật khẩu)
            if (!ModelState.IsValid)
            {
                return View(model);
            }

            // Bước 2: Tìm kiếm tài khoản trong CSDL theo địa chỉ Email (không phân biệt chữ hoa/thường)
            var user = await _context.UserAccounts
                .FirstOrDefaultAsync(u => u.Email.ToLower() == model.Email.ToLower().Trim());

            // Bước 3: Kiểm tra nếu không tìm thấy User hoặc Mật khẩu không khớp
            // Dùng BCrypt.Net.BCrypt.Verify để so khớp mật khẩu người dùng nhập với chuỗi băm trong CSDL
            if (user == null || !BCrypt.Net.BCrypt.Verify(model.Password, user.PasswordHash))
            {
                ModelState.AddModelError(string.Empty, "Email hoặc mật khẩu không chính xác.");
                return View(model);
            }

            // Không cho phép tài khoản bị khóa hoặc đã chuyển vào thùng rác đăng nhập.
            if (user.IsDeleted)
            {
                ModelState.AddModelError(string.Empty, "Tài khoản này đã bị xóa. Vui lòng liên hệ quản trị viên nếu cần khôi phục.");
                return View(model);
            }

            if (!user.IsActive)
            {
                ModelState.AddModelError(string.Empty, "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ trung tâm.");
                return View(model);
            }

            // Bước 5: Tạo danh sách Claims (các thông tin định danh đính kèm phiên làm việc của người dùng)
            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, user.AccountId.ToString()), // Lưu mã tài khoản AccountId (dạng chuỗi)
                new Claim(ClaimTypes.Name, user.FullName),                       // Lưu họ và tên người dùng
                new Claim(ClaimTypes.Email, user.Email),                         // Lưu email người dùng
                new Claim(ClaimTypes.Role, user.Role),                           // Lưu vai trò quan trọng: Admin, Teacher, hoặc Student
                new Claim("AvatarUrl", user.AvatarUrl ?? "/images/default-avatar.png") // Lưu đường dẫn ảnh đại diện
            };

            var roleCookieScheme = user.Role switch
            {
                "Admin" => "AdminCookie",
                "Teacher" => "TeacherCookie",
                "Student" => "StudentCookie",
                _ => null
            };

            if (roleCookieScheme == null)
            {
                ModelState.AddModelError(string.Empty, "Vai trò tài khoản không hợp lệ.");
                return View(model);
            }

            // Mỗi vai trò có cookie riêng để đăng nhập trong các tab độc lập.
            var claimsIdentity = new ClaimsIdentity(claims, roleCookieScheme);

            // Thiết lập thuộc tính phiên đăng nhập: Ghi nhớ đăng nhập (RememberMe)
            var authProperties = new AuthenticationProperties
            {
                IsPersistent = model.RememberMe, // Nếu chọn ghi nhớ: lưu cookie lâu dài
                ExpiresUtc = model.RememberMe ? DateTimeOffset.UtcNow.AddDays(7) : DateTimeOffset.UtcNow.AddHours(4)
            };

            var principal = new ClaimsPrincipal(claimsIdentity);
            await HttpContext.SignInAsync(roleCookieScheme, principal, authProperties);

            // Bước 8: Điều hướng thông minh theo vai trò (Role) sau khi đăng nhập thành công
            if (user.Role == "Admin")
            {
                // Quản trị viên -> chuyển thẳng vào trang Admin Dashboard
                return RedirectToAction("Index", "Dashboard", new { area = "Admin" });
            }
            if (user.Role == "Teacher")
            {
                // Giáo viên -> chuyển thẳng vào trang Teacher Dashboard
                return RedirectToAction("Index", "TeacherDashboard", new { area = "Teacher" });
            }

            // Học viên -> chuyển về trang ban đầu hoặc trang chủ với ngữ cảnh cookie học viên.
            return string.IsNullOrWhiteSpace(model.ReturnUrl)
                ? RedirectToAction("Index", "Home", new { area = "", authRole = user.Role })
                : RedirectToLocal(model.ReturnUrl);
        }

        // =============================================================================================
        // HÀM 3: GET /Account/Register
        // =============================================================================================
        [HttpGet]
        public IActionResult Register()
        {
            // Nếu đã đăng nhập thì chuyển về trang chủ
            if (User.Identity != null && User.Identity.IsAuthenticated)
            {
                return RedirectToAction("Index", "Home");
            }
            return View();
        }

        // =============================================================================================
        // HÀM 4: POST /Account/Register - XỬ LÝ ĐĂNG KÝ, BĂM MẬT KHẨU BCRYPT & TỰ ĐỘNG TẠO STUDENT
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken] // Chống CSRF
        public async Task<IActionResult> Register(RegisterViewModel model)
        {
            // Kiểm tra tính hợp lệ của dữ liệu (mật khẩu xác nhận phải trùng khớp, SĐT đúng định dạng)
            if (!ModelState.IsValid)
            {
                return View(model);
            }

            // Kiểm tra xem Email đã có người khác sử dụng trong hệ thống hay chưa
            var existingUser = await _context.UserAccounts
                .AnyAsync(u => u.Email.ToLower() == model.Email.ToLower().Trim());

            if (existingUser)
            {
                ModelState.AddModelError("Email", "Email này đã được sử dụng. Vui lòng chọn email khác.");
                return View(model);
            }

            // Bước 1: Khởi tạo đối tượng UserAccount mới, băm mật khẩu với BCrypt
            var newUser = new UserAccount
            {
                FullName = model.FullName.Trim(),
                Email = model.Email.ToLower().Trim(),
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(model.Password), // Băm mật khẩu 1 chiều an toàn
                Role = "Student",                                              // Mặc định tài khoản đăng ký trên web là Học viên
                AvatarUrl = "/images/avatars/default.png",
                IsActive = true,                                               // Kích hoạt tài khoản ngay lập tức
                CreatedAt = DateTime.Now
            };

            // Thêm vào bảng UserAccounts và lưu để lấy được AccountId tự sinh (Identity)
            _context.UserAccounts.Add(newUser);
            await _context.SaveChangesAsync();

            // Bước 2: Tạo bản ghi Student tương ứng trong bảng Students (Quan hệ 1 - 1)
            var student = new Student
            {
                AccountId = newUser.AccountId,        // Khóa ngoại liên kết với UserAccount vừa tạo
                PhoneNumber = model.PhoneNumber.Trim()
            };

            _context.Students.Add(student);
            await _context.SaveChangesAsync();

            // Hiển thị thông báo thành công và chuyển sang màn hình Đăng nhập
            TempData["SuccessMessage"] = "Đăng ký tài khoản thành công! Vui lòng đăng nhập.";
            return RedirectToAction("Login");
        }

        // =============================================================================================
        // HÀM 5: POST/GET /Account/Logout - ĐĂNG XUẤT VÀ XÓA BỎ COOKIE PHIÊN LÀM VIỆC
        // =============================================================================================
        [AllowAnonymous] // Cho phép gọi hàm này ngay cả khi trạng thái chưa rõ
        public async Task<IActionResult> Logout(string? authRole)
        {
            var role = User.FindFirstValue(ClaimTypes.Role);
            if (!string.IsNullOrWhiteSpace(authRole) && !string.Equals(authRole, role, StringComparison.Ordinal))
            {
                return RedirectToAction("Index", "Home", new { area = "" });
            }

            var scheme = role switch
            {
                "Admin" => "AdminCookie",
                "Teacher" => "TeacherCookie",
                "Student" => "StudentCookie",
                _ => null
            };

            if (scheme != null)
            {
                await HttpContext.SignOutAsync(scheme);
            }

            // Clear the cookie used by earlier versions; current sessions use role-specific cookies only.
            await HttpContext.SignOutAsync("GuestCookie");
            return RedirectToAction("Index", "Home", new { area = "" });
        }

        // =============================================================================================
        // HÀM 6: GET /Account/AccessDenied - TRANG THÔNG BÁO TỪ CHỐI TRUY CẬP (LỖI 403 FORBIDDEN)
        // =============================================================================================
        [HttpGet]
        public IActionResult AccessDenied()
        {
            // Hiển thị giao diện thông báo bạn không có quyền hạn truy cập vào khu vực này
            return View();
        }

        // =============================================================================================
        // HÀM 7: GET /Account/ChangePassword - HIỂN THỊ GIAO DIỆN ĐỔI MẬT KHẨU
        // =============================================================================================
        [Authorize] // Bắt buộc phải đăng nhập mới được vào trang này
        [HttpGet]
        public IActionResult ChangePassword()
        {
            return View();
        }

        // =============================================================================================
        // HÀM 8: POST /Account/ChangePassword - XỬ LÝ ĐỔI MẬT KHẨU AN TOÀN
        // =============================================================================================
        [Authorize]
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ChangePassword(ChangePasswordViewModel model)
        {
            if (!ModelState.IsValid)
            {
                return View(model);
            }

            // Lấy AccountId của người dùng hiện tại đang đăng nhập từ Cookie Claims
            var userIdString = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdString, out int accountId))
            {
                return RedirectToAction("Login");
            }

            var user = await _context.UserAccounts.FindAsync(accountId);
            if (user == null)
            {
                return RedirectToAction("Login");
            }

            // Kiểm tra mật khẩu hiện tại có nhập đúng không bằng BCrypt.Verify
            if (!BCrypt.Net.BCrypt.Verify(model.CurrentPassword, user.PasswordHash))
            {
                ModelState.AddModelError("CurrentPassword", "Mật khẩu hiện tại không chính xác.");
                return View(model);
            }

            // Băm mật khẩu mới và lưu lại vào CSDL
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(model.NewPassword);
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = "Đổi mật khẩu thành công!";
            return RedirectToAction("ChangePassword", new { authRole = User.FindFirstValue(ClaimTypes.Role) });
        }

        // =============================================================================================
        // HÀM HỖ TRỢ: RedirectToLocal - CHUYỂN HƯỚNG AN TOÀN TRÁNH LỖ HỔNG OPEN REDIRECT ATTACK
        // =============================================================================================
        private IActionResult RedirectToLocal(string? returnUrl)
        {
            // Chỉ chuyển hướng nếu returnUrl là đường dẫn nội bộ trong website (bắt đầu bằng /)
            if (!string.IsNullOrEmpty(returnUrl) && Url.IsLocalUrl(returnUrl))
            {
                return Redirect(returnUrl);
            }
            return RedirectToAction("Index", "Home");
        }
    }
}
