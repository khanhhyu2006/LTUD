// =================================================================================================
// TẬP TIN: Program.cs - TẬP TIN CẤU HÌNH VÀ KHỞI ĐỘNG CHÍNH CỦA ỨNG DỤNG ASP.NET CORE (.NET 8)
// Chức năng: Cấu hình Dependency Injection (DI), CSDL SQL Server, Xác thực Cookie, Pipeline và Routing
// =================================================================================================

using Microsoft.AspNetCore.Authentication.Cookies; // Thư viện xử lý xác thực đăng nhập bằng Cookie
using Microsoft.EntityFrameworkCore;               // Thư viện Entity Framework Core để thao tác CSDL
using WedEnglishApp.Data;                          // Namespace chứa ApplicationDbContext và DbInitializer

// Khởi tạo đối tượng builder để đăng ký các dịch vụ (Services) vào hệ thống
var builder = WebApplication.CreateBuilder(args);

// -------------------------------------------------------------------------------------------------
// KHỐI 1: CẤU HÌNH KẾT NỐI CƠ SỞ DỮ LIỆU SQL SERVER VỚI ENTITY FRAMEWORK CORE
// -------------------------------------------------------------------------------------------------
// Đăng ký ApplicationDbContext vào DI Container với vòng đời Scoped (mỗi request 1 instance)
// Lấy chuỗi kết nối có tên "DefaultConnection" được cấu hình trong file appsettings.json
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// -------------------------------------------------------------------------------------------------
// KHỐI 2: CẤU HÌNH XÁC THỰC NGƯỜI DÙNG BẰNG COOKIE (COOKIE AUTHENTICATION) & PHÂN QUYỀN
// -------------------------------------------------------------------------------------------------
builder.Services.AddAuthentication(options =>
    {
        options.DefaultScheme = "RoleCookieRouter";
        options.DefaultAuthenticateScheme = "RoleCookieRouter";
        options.DefaultChallengeScheme = "RoleCookieRouter";
        })
        .AddPolicyScheme("RoleCookieRouter", "Role-specific cookie router", options =>
        {
            options.ForwardDefaultSelector = context =>
            {
                var path = context.Request.Path;
                if (path.StartsWithSegments("/Admin", StringComparison.OrdinalIgnoreCase)) return "AdminCookie";
                if (path.StartsWithSegments("/Teacher", StringComparison.OrdinalIgnoreCase)) return "TeacherCookie";
                if (path.StartsWithSegments("/Consultation", StringComparison.OrdinalIgnoreCase)
                    || path.StartsWithSegments("/Home/Contact", StringComparison.OrdinalIgnoreCase)) return "StudentCookie";
                var roleScheme = context.Request.Query["authRole"].ToString() switch
                {
                    "Admin" => "AdminCookie",
                    "Teacher" => "TeacherCookie",
                    "Student" => "StudentCookie",
                    _ => null
                };
                if (roleScheme != null)
                {
                    return roleScheme;
                }

                if (path.StartsWithSegments("/Student", StringComparison.OrdinalIgnoreCase)
                    || path.StartsWithSegments("/Enrollment", StringComparison.OrdinalIgnoreCase)
                    || path.StartsWithSegments("/PlacementTest", StringComparison.OrdinalIgnoreCase)
                    || path.StartsWithSegments("/Consultation", StringComparison.OrdinalIgnoreCase))
                {
                    return "StudentCookie";
                }

                return "GuestCookie";
            };
        })
    .AddCookie("AdminCookie", options =>
    {
        options.Cookie.Name = "WedEnglishApp.AdminAuth";
        options.LoginPath = "/Account/Login";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromDays(7);
        options.SlidingExpiration = true;
    })
    .AddCookie("TeacherCookie", options =>
    {
        options.Cookie.Name = "WedEnglishApp.TeacherAuth";
        options.LoginPath = "/Account/Login";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromDays(7);
        options.SlidingExpiration = true;
    })
    .AddCookie("StudentCookie", options =>
    {
        options.Cookie.Name = "WedEnglishApp.StudentAuth";
        options.LoginPath = "/Account/Login";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromDays(7);
        options.SlidingExpiration = true;
    })
    .AddCookie("GuestCookie", options =>
    {
        options.LoginPath = "/Account/Login";              // Đường dẫn tự động chuyển hướng nếu người dùng chưa đăng nhập
        options.LogoutPath = "/Account/Logout";            // Đường dẫn xử lý khi người dùng đăng xuất
        options.AccessDeniedPath = "/Account/AccessDenied";// Đường dẫn chuyển hướng khi truy cập trang vượt quá quyền hạn (403)
        options.ExpireTimeSpan = TimeSpan.FromDays(7);      // Thời hạn tồn tại của Cookie phiên đăng nhập (7 ngày)
        options.SlidingExpiration = true;                   // Tự động gia hạn thời gian sống của Cookie khi người dùng có tương tác
    });

// -------------------------------------------------------------------------------------------------
// KHỐI 3: ĐĂNG KÝ HỖ TRỢ KIẾN TRÚC MVC (MODEL - VIEW - CONTROLLER)
// -------------------------------------------------------------------------------------------------
// Cho phép hệ thống xử lý các Controller và render giao diện Razor Views (.cshtml)
builder.Services.AddControllersWithViews();
builder.Services.AddScoped<WedEnglishApp.Services.ConsultationAccess>();

// -------------------------------------------------------------------------------------------------
// KHỐI 4: CẤU HÌNH SWAGGER ĐỂ KIỂM THỬ VÀ TÀI LIỆU HÓA API (NẾU CẦN DÙNG)
// -------------------------------------------------------------------------------------------------
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Xây dựng (Build) đối tượng ứng dụng WebApplication từ cấu hình builder ở trên
var app = builder.Build();

// -------------------------------------------------------------------------------------------------
// KHỐI 5: TỰ ĐỘNG KHỞI TẠO CSDL VÀ NẠP DỮ LIỆU MẪU (SEEDING DATA) KHI ỨNG DỤNG BẮT ĐẦU CHẠY
// -------------------------------------------------------------------------------------------------
using (var scope = app.Services.CreateScope()) // Tạo scope tạm thời để lấy DbContext từ DI Container
{
    var services = scope.ServiceProvider;
    try
    {
        // Lấy DbContext ra và gọi phương thức nạp dữ liệu mẫu
        var context = services.GetRequiredService<ApplicationDbContext>();
        DbInitializer.Initialize(context); // Nạp 14 tài khoản, 10 lớp học, 20 hóa đơn, 5 khóa học...
    }
    catch (Exception ex)
    {
        // Ghi log nếu xảy ra lỗi kết nối CSDL trong quá trình khởi tạo ban đầu
        var logger = services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "Lỗi khi khởi tạo CSDL hoặc Seeding dữ liệu mẫu.");
    }
}

// -------------------------------------------------------------------------------------------------
// KHỐI 6: CẤU HÌNH ĐƯỜNG ỐNG XỬ LÝ HTTP REQUEST (HTTP REQUEST PIPELINE / MIDDLEWARES)
// -------------------------------------------------------------------------------------------------
// Nếu đang ở môi trường phát triển (Development), bật giao diện Swagger UI để test
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection(); // Tự động chuyển hướng yêu cầu HTTP sang giao thức bảo mật HTTPS
app.UseStaticFiles();      // Cho phép phục vụ các tệp tĩnh trong thư mục wwwroot (CSS, JS, Hình ảnh, Font)

app.UseRouting();          // Bật cơ chế định tuyến URL tới Controller/Action tương ứng

// Middleware Bảo mật: Luôn đặt UseAuthentication() TRƯỚC UseAuthorization()
app.UseAuthentication();   // 1. Xác thực: Nhận diện người dùng là ai qua Cookie
app.UseAuthorization();    // 2. Phân quyền: Kiểm tra người dùng có quyền (Role: Admin, Teacher, Student) hay không

// -------------------------------------------------------------------------------------------------
// KHỐI 7: CẤU HÌNH ĐỊNH TUYẾN (MAP ROUTE)
// -------------------------------------------------------------------------------------------------
// Cấu hình Route dành cho các phân hệ phân vùng Areas (Admin và Teacher)
// Ví dụ: /Admin/Dashboard/Index hoặc /Teacher/TeachingClass/Index
app.MapControllerRoute(
    name: "areas",
    pattern: "{area:exists}/{controller=Dashboard}/{action=Index}/{id?}");

// Cấu hình Route mặc định dành cho Khách vãng lai và Học viên (Public)
// Ví dụ: truy cập trang chủ / sẽ gọi HomeController -> Index()
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

// Khởi chạy ứng dụng và lắng nghe các HTTP request gửi đến máy chủ Kestrel/IIS
app.Run();

