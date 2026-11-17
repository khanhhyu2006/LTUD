// =================================================================================================
// CONTROLLER: ProgramController - QUẢN LÝ TÌM KIẾM, LỌC VÀ XEM CHI TIẾT CHƯƠNG TRÌNH HỌC
// Quyền truy cập: Public (Dành cho mọi khách truy cập website)
// Nghiệp vụ: Tìm kiếm khóa học theo từ khóa, lọc theo Level (Beginner/Inter/Adv), lọc theo học phí, phân trang
// =================================================================================================

using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.ViewModels.Program;

namespace WedEnglishApp.Controllers
{
    public class ProgramController : Controller
    {
        private readonly ApplicationDbContext _context; // Đối tượng truy vấn cơ sở dữ liệu

        public ProgramController(ApplicationDbContext context)
        {
            _context = context;
        }

        // =============================================================================================
        // HÀM 1: GET /Program - HIỂN THỊ DANH SÁCH KHÓA HỌC KÈM BỘ LỌC ĐA TIÊU CHÍ VÀ PHÂN TRANG
        // Tham số: search (từ khóa), level (cấp độ), minFee/maxFee (khoảng giá), page (trang hiện tại)
        // =============================================================================================
        public async Task<IActionResult> Index(string? search, string? level, decimal? minFee, decimal? maxFee, int page = 1)
        {
            int pageSize = 6; // Số lượng khóa học hiển thị trên 1 trang (Pagination)
            var query = _context.Programs.Where(p => p.IsActive && !p.IsDeleted).AsQueryable(); // Khởi tạo truy vấn các khóa đang mở

            // BỘ LỌC 1: Tìm kiếm theo Tên chương trình học hoặc Mô tả
            if (!string.IsNullOrWhiteSpace(search))
            {
                string searchLower = search.Trim().ToLower();
                query = query.Where(p => p.ProgramName.ToLower().Contains(searchLower) || p.Description.ToLower().Contains(searchLower));
            }

            // BỘ LỌC 2: Lọc theo Cấp độ (Level: Beginner, Intermediate, Advanced)
            if (!string.IsNullOrWhiteSpace(level))
            {
                query = query.Where(p => p.Level == level);
            }

            // BỘ LỌC 3: Lọc theo Khoảng học phí (Tối thiểu - Tối đa)
            if (minFee.HasValue)
            {
                query = query.Where(p => p.TuitionFee >= minFee.Value);
            }
            if (maxFee.HasValue)
            {
                query = query.Where(p => p.TuitionFee <= maxFee.Value);
            }

            // XỬ LÝ PHÂN TRANG: Tính tổng số kết quả và tổng số trang
            int totalItems = await query.CountAsync();
            int totalPages = (int)Math.Ceiling(totalItems / (double)pageSize);
            page = Math.Max(1, Math.Min(page, Math.Max(1, totalPages)));

            // Lấy dữ liệu cho trang hiện tại (Skip & Take)
            var programs = await query
                .OrderByDescending(p => p.ProgramId)
                .Skip((page - 1) * pageSize) // Bỏ qua các bản ghi của các trang trước
                .Take(pageSize)              // Lấy đúng số bản ghi của trang này
                .ToListAsync();

            // Đóng gói vào ViewModel gửi ra View
            var viewModel = new ProgramListViewModel
            {
                Programs = programs,
                SearchTerm = search,
                SelectedLevel = level,
                MinFee = minFee,
                MaxFee = maxFee,
                CurrentPage = page,
                TotalPages = totalPages,
                TotalItems = totalItems,
                PageSize = pageSize
            };

            return View(viewModel); // Trả về giao diện danh sách khóa học Index.cshtml
        }

        // =============================================================================================
        // HÀM 2: GET /Program/Detail/{id} - XEM CHI TIẾT KHÓA HỌC & CÁC LỚP HỌC ĐANG MỞ
        // =============================================================================================
        public async Task<IActionResult> Detail(int id)
        {
            // Truy vấn thông tin chi tiết của khóa học kèm:
            // 1. Danh sách các lớp học (Classes)
            // 2. Thông tin Giảng viên phụ trách từng lớp (Teacher -> UserAccount)
            // 3. Thời khóa biểu ca học trong tuần (Schedules)
            var today = DateTime.Today;
            var program = await _context.Programs
                .Include(p => p.Classes.Where(c => !c.IsDeleted && (c.Status == "Planning" || c.Status == "InProgress") && c.EndDate >= today && c.EndDate >= c.StartDate))
                    .ThenInclude(c => c.Schedules)
                .FirstOrDefaultAsync(p => p.ProgramId == id && p.IsActive && !p.IsDeleted);

            if (program == null)
            {
                return NotFound(); // Không tìm thấy hoặc khóa học đã bị vô hiệu hóa
            }

            return View(program); // Trả về giao diện chi tiết Detail.cshtml
        }
    }
}
