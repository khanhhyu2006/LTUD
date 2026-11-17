// =================================================================================================
// CONTROLLER: BannerManagerController (Area: Admin) - QUẢN LÝ BANNER QUẢNG BÁ TRÊN TRANG CHỦ
// Quyền truy cập: [Area("Admin")], [Authorize(Roles = "Admin")] - Dành riêng cho Quản trị viên
// Nghiệp vụ: Danh sách banner, Thêm mới, Chỉnh sửa, Xóa, Bật/Tắt hiển thị và liên kết LinkUrl
// =================================================================================================

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]                  // Thuộc phân vùng Quản trị viên (Areas/Admin)
    [Authorize(Roles = "Admin")]     // Kiểm tra quyền hạn phải là Admin
    public class BannerManagerController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _env;

        public BannerManagerController(ApplicationDbContext context, IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        // =============================================================================================
        // HÀM 1: GET /Admin/BannerManager - XEM DANH SÁCH TẤT CẢ BANNER CHƯA BỊ XÓA
        // =============================================================================================
        public async Task<IActionResult> Index()
        {
            var banners = await _context.Banners
                .Where(b => !b.IsDeleted) // Chỉ lấy các banner chưa chuyển vào thùng rác
                .OrderBy(b => b.DisplayOrder)
                .ThenByDescending(b => b.CreatedAt)
                .ToListAsync();

            return View(banners);
        }

        // =============================================================================================
        // HÀM 2: GET /Admin/BannerManager/Create - HIỂN THỊ FORM TẠO BANNER MỚI
        // =============================================================================================
        [HttpGet]
        public IActionResult Create()
        {
            var banner = new Banner
            {
                DisplayOrder = (_context.Banners.Where(b => !b.IsDeleted).Max(b => (int?)b.DisplayOrder) ?? 0) + 1,
                ButtonText = "Khám phá ngay",
                LinkUrl = "/Program",
                IsActive = true
            };
            return View(banner);
        }

        // =============================================================================================
        // HÀM 3: POST /Admin/BannerManager/Create - XỬ LÝ LƯU BANNER VÀ UPLOAD HÌNH ẢNH
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(Banner banner, IFormFile? imageFile)
        {
            // Xử lý upload ảnh nếu người dùng chọn file từ máy tính
            if (imageFile != null && imageFile.Length > 0)
            {
                string uploadsFolder = Path.Combine(_env.WebRootPath, "uploads", "banners");
                if (!Directory.Exists(uploadsFolder))
                {
                    Directory.CreateDirectory(uploadsFolder);
                }

                string uniqueFileName = $"{Guid.NewGuid()}_{Path.GetFileName(imageFile.FileName)}";
                string filePath = Path.Combine(uploadsFolder, uniqueFileName);

                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await imageFile.CopyToAsync(stream);
                }

                banner.ImageUrl = $"/uploads/banners/{uniqueFileName}";
                ModelState.Remove("ImageUrl"); // Xóa lỗi validation mặc định của ImageUrl nếu có
            }

            // Kiểm tra tính hợp lệ nếu chưa có ảnh
            if (string.IsNullOrWhiteSpace(banner.ImageUrl))
            {
                ModelState.AddModelError("ImageUrl", "Vui lòng tải lên tệp ảnh từ máy tính hoặc dán link ảnh trực tuyến.");
            }

            if (ModelState.IsValid)
            {
                banner.IsDeleted = false;
                banner.CreatedAt = DateTime.Now;
                _context.Banners.Add(banner);
                await _context.SaveChangesAsync();

                TempData["SuccessMessage"] = "Thêm mới Banner thành công!";
                return RedirectToAction(nameof(Index));
            }

            return View(banner);
        }

        // =============================================================================================
        // HÀM 4: GET /Admin/BannerManager/Edit/{id} - HIỂN THỊ FORM CHỈNH SỬA BANNER
        // =============================================================================================
        [HttpGet]
        public async Task<IActionResult> Edit(int id)
        {
            var banner = await _context.Banners.FindAsync(id);
            if (banner == null)
            {
                return NotFound();
            }
            return View(banner);
        }

        // =============================================================================================
        // HÀM 5: POST /Admin/BannerManager/Edit/{id} - XỬ LÝ CẬP NHẬT BANNER
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, Banner model, IFormFile? imageFile)
        {
            if (id != model.BannerId)
            {
                return NotFound();
            }

            var banner = await _context.Banners.FindAsync(id);
            if (banner == null)
            {
                return NotFound();
            }

            // Xử lý upload ảnh mới nếu có
            if (imageFile != null && imageFile.Length > 0)
            {
                string uploadsFolder = Path.Combine(_env.WebRootPath, "uploads", "banners");
                if (!Directory.Exists(uploadsFolder))
                {
                    Directory.CreateDirectory(uploadsFolder);
                }

                string uniqueFileName = $"{Guid.NewGuid()}_{Path.GetFileName(imageFile.FileName)}";
                string filePath = Path.Combine(uploadsFolder, uniqueFileName);

                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await imageFile.CopyToAsync(stream);
                }

                banner.ImageUrl = $"/uploads/banners/{uniqueFileName}";
            }
            else if (!string.IsNullOrWhiteSpace(model.ImageUrl))
            {
                banner.ImageUrl = model.ImageUrl;
            }

            if (ModelState.IsValid)
            {
                banner.Title = model.Title.Trim();
                banner.Subtitle = model.Subtitle?.Trim();
                banner.LinkUrl = model.LinkUrl.Trim();
                banner.ButtonText = model.ButtonText?.Trim() ?? "Khám phá ngay";
                banner.DisplayOrder = model.DisplayOrder;
                banner.IsActive = model.IsActive;

                _context.Banners.Update(banner);
                await _context.SaveChangesAsync();

                TempData["SuccessMessage"] = "Cập nhật Banner thành công!";
                return RedirectToAction(nameof(Index));
            }

            return View(model);
        }

        // =============================================================================================
        // HÀM 6: POST /Admin/BannerManager/ToggleActive/{id} - BẬT / TẮT TRẠNG THÁI HIỂN THỊ
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ToggleActive(int id)
        {
            var banner = await _context.Banners.FindAsync(id);
            if (banner == null)
            {
                return NotFound();
            }

            banner.IsActive = !banner.IsActive;
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã {(banner.IsActive ? "kích hoạt" : "tạm ẩn")} banner: {banner.Title}";
            return RedirectToAction(nameof(Index));
        }

        // =============================================================================================
        // HÀM 7: POST /Admin/BannerManager/Delete/{id} - CHUYỂN BANNER VÀO THÙNG RÁC (XÓA MỀM)
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var banner = await _context.Banners.FindAsync(id);
            if (banner != null)
            {
                banner.IsDeleted = true;
                banner.DeletedAt = DateTime.Now;
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = $"Đã chuyển banner '{banner.Title}' vào thùng rác! Bạn có thể xem hoặc khôi phục trong mục Thùng rác.";
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
