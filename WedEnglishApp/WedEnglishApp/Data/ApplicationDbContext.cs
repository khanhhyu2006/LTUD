using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Models;

namespace WedEnglishApp.Data
{
    // =================================================================================================
    // LỚP: ApplicationDbContext - ĐẠI DIỆN CƠ SỞ DỮ LIỆU ENTITY FRAMEWORK CORE
    // Chức năng: Ánh xạ các bảng trong SQL Server thành các tập hợp DbSet<T>, cấu hình Fluent API,
    // thiết lập các ràng buộc quan hệ 1-1, 1-N và quy tắc xóa Cascade/Restrict.
    // =================================================================================================
    public class ApplicationDbContext : DbContext
    {
        // Constructor nhận cấu hình DbContextOptions (chuỗi kết nối, nhà cung cấp SQL Server)
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        // ---------------------------------------------------------------------------------------------
        // KHỐI KHAI BÁO CÁC TẬP HỢP THỰC THỂ (DBSETS - TƯƠNG ỨNG CÁC BẢNG TRONG SQL SERVER)
        // ---------------------------------------------------------------------------------------------
        public DbSet<UserAccount> UserAccounts => Set<UserAccount>();       // Bảng 1: Tài khoản đăng nhập (Admin, Teacher, Student)
        public DbSet<Student> Students => Set<Student>();                   // Bảng 2: Hồ sơ chi tiết của Học viên
        public DbSet<Teacher> Teachers => Set<Teacher>();                   // Bảng 3: Hồ sơ chi tiết của Giảng viên
        public DbSet<CourseProgram> Programs => Set<CourseProgram>();       // Bảng 4: Chương trình đào tạo (IELTS, TOEIC...)
        public DbSet<CourseClass> Classes => Set<CourseClass>();            // Bảng 5: Lớp học cụ thể theo khóa
        public DbSet<Registration> Registrations => Set<Registration>();    // Bảng 6: Đơn ghi danh / đăng ký học
        public DbSet<Payment> Payments => Set<Payment>();                   // Bảng 7: Hóa đơn & biên lai thanh toán học phí
        public DbSet<ExamSession> ExamSessions => Set<ExamSession>();
        public DbSet<PlacementTest> PlacementTests => Set<PlacementTest>(); // Bảng 8: Bài thi kiểm tra xếp lớp đầu vào
        public DbSet<ConsultationMessage> ConsultationMessages => Set<ConsultationMessage>();
        public DbSet<Consultation> Consultations => Set<Consultation>();   // Bảng 9 (Bổ sung): Yêu cầu tư vấn trực tuyến
        public DbSet<ClassSchedule> ClassSchedules => Set<ClassSchedule>(); // Bảng 10 (Bổ sung): Lịch học các ca trong tuần
        public DbSet<TeacherActivity> TeacherActivities => Set<TeacherActivity>();
        public DbSet<ClassDocument> ClassDocuments => Set<ClassDocument>(); // Bảng tài liệu bài giảng giáo trình
        public DbSet<CourseFeedback> CourseFeedbacks => Set<CourseFeedback>(); // Bảng đánh giá phản hồi khóa học
        public DbSet<Banner> Banners => Set<Banner>();                     // Bảng quản lý Banner quảng bá trên trang chủ
        public DbSet<TeacherSalary> TeacherSalaries => Set<TeacherSalary>(); // Bảng quản lý bảng lương của giáo viên

        // ---------------------------------------------------------------------------------------------
        // PHƯƠNG THỨC OnModelCreating: CẤU HÌNH FLUENT API CHO CÁC RÀNG BUỘC VÀ QUAN HỆ CSDL
        // ---------------------------------------------------------------------------------------------
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            modelBuilder.Entity<TeacherActivity>().HasOne(a => a.Teacher).WithMany()
                .HasForeignKey(a => a.TeacherId).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<TeacherActivity>().HasIndex(a => new { a.TeacherId, a.OccurredAt });
            modelBuilder.Entity<ClassDocument>().Property(d => d.IsPublished).HasDefaultValue(true);

            // Cấu hình 1: Ràng buộc duy nhất (Unique Index) cho trường Email trong bảng UserAccount
            // Mục đích: Đảm bảo không thể có 2 tài khoản trùng địa chỉ Email
            modelBuilder.Entity<UserAccount>()
                .HasIndex(u => u.Email)
                .IsUnique();

            // Cấu hình 2: Quan hệ 1 - 1 giữa UserAccount và Student
            // 1 tài khoản chỉ gắn với 1 hồ sơ học viên; khi xóa UserAccount thì Student bị xóa theo (Cascade)
            modelBuilder.Entity<Student>()
                .HasOne(s => s.UserAccount)
                .WithOne(u => u.Student)
                .HasForeignKey<Student>(s => s.AccountId)
                .OnDelete(DeleteBehavior.Cascade);

            // Cấu hình 3: Quan hệ 1 - 1 giữa UserAccount và Teacher
            // 1 tài khoản chỉ gắn với 1 hồ sơ giáo viên; khi xóa UserAccount thì Teacher bị xóa theo (Cascade)
            modelBuilder.Entity<Teacher>()
                .HasOne(t => t.UserAccount)
                .WithOne(u => u.Teacher)
                .HasForeignKey<Teacher>(t => t.AccountId)
                .OnDelete(DeleteBehavior.Cascade);

            // Cấu hình 4: Quan hệ 1 - N giữa Program và Class
            // 1 chương trình học có nhiều lớp học; ngăn chặn xóa Program nếu đang có lớp mở (Restrict)
            modelBuilder.Entity<CourseClass>()
                .HasOne(c => c.Program)
                .WithMany(p => p.Classes)
                .HasForeignKey(c => c.ProgramId)
                .OnDelete(DeleteBehavior.Restrict);

            // Cấu hình 5: Quan hệ 1 - N giữa Teacher và Class
            // 1 giáo viên phụ trách nhiều lớp; nếu xóa giáo viên thì trường TeacherId trong Class chuyển thành NULL (SetNull)
            modelBuilder.Entity<CourseClass>()
                .HasOne(c => c.Teacher)
                .WithMany(t => t.Classes)
                .HasForeignKey(c => c.TeacherId)
                .OnDelete(DeleteBehavior.SetNull);

            // Cấu hình 6: Quan hệ giữa Registration với Student và Class (Tránh lỗi chu trình Cascade Delete)
            modelBuilder.Entity<Registration>()
                .HasOne(r => r.Student)
                .WithMany(s => s.Registrations)
                .HasForeignKey(r => r.StudentId)
                .OnDelete(DeleteBehavior.Restrict); // Không cho xóa học viên nếu đang có đơn ghi danh

            modelBuilder.Entity<Registration>()
                .HasOne(r => r.Class)
                .WithMany(c => c.Registrations)
                .HasForeignKey(r => new { r.ClassId, r.ProgramId })
                .HasPrincipalKey(c => new { c.ClassId, c.ProgramId })
                .OnDelete(DeleteBehavior.Restrict); // Không cho xóa lớp học nếu đang có học viên đăng ký

            modelBuilder.Entity<Registration>()
                .HasOne(r => r.Program).WithMany()
                .HasForeignKey(r => r.ProgramId).OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<CourseClass>().HasAlternateKey(c => new { c.ClassId, c.ProgramId });
            modelBuilder.Entity<Registration>().HasIndex(r => new { r.StudentId, r.ProgramId });
            modelBuilder.Entity<Registration>().ToTable("Registrations", t =>
            {
                t.HasTrigger("TR_Registrations_CourseFlow");
                t.UseSqlOutputClause(false);
            });
            modelBuilder.Entity<Payment>().ToTable("Payments", t =>
            {
                t.HasTrigger("TR_Payments_CourseFlow");
                t.UseSqlOutputClause(false);
            });
            modelBuilder.Entity<ClassSchedule>()
                .HasIndex(s => new { s.ClassId, s.DayOfWeek, s.StartTime, s.EndTime })
                .IsUnique().HasDatabaseName("UX_ClassSchedules_Class_Day_Time");

            // Cấu hình 7: Quan hệ 1 - 1 giữa Registration và Payment
            // Mỗi đơn ghi danh chỉ sinh ra 1 hóa đơn thanh toán; nếu xóa đơn thì hóa đơn bị xóa theo
            modelBuilder.Entity<Payment>()
                .HasOne(p => p.Registration)
                .WithOne(r => r.Payment)
                .HasForeignKey<Payment>(p => p.RegistrationId)
                .OnDelete(DeleteBehavior.Cascade);

            // Cấu hình 8: Quan hệ của PlacementTest (Bài thi xếp lớp)
            modelBuilder.Entity<PlacementTest>()
                .HasOne(pt => pt.Student)
                .WithMany(s => s.PlacementTests)
                .HasForeignKey(pt => pt.StudentId)
                .OnDelete(DeleteBehavior.Restrict); // Không cho xóa học viên nếu có bài thi

            modelBuilder.Entity<PlacementTest>()
                .HasOne(pt => pt.EvaluatedByTeacher)
                .WithMany(t => t.EvaluatedTests)
                .HasForeignKey(pt => pt.EvaluatedByTeacherId)
                .OnDelete(DeleteBehavior.SetNull); // Nếu xóa giáo viên thì bài thi vẫn giữ lại và để trống người chấm

            modelBuilder.Entity<ExamSession>().HasIndex(s => s.Name).IsUnique();
            modelBuilder.Entity<ExamSession>().HasOne(s => s.Teacher).WithMany()
                .HasForeignKey(s => s.TeacherId).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PlacementTest>().HasOne(t => t.ExamSession).WithMany(s => s.Tests)
                .HasForeignKey(t => t.ExamSessionId).OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<Consultation>().HasIndex(c => new { c.OwnerAccountId, c.LastMessageAt });
            modelBuilder.Entity<Consultation>().HasOne(c => c.OwnerAccount).WithMany()
                .HasForeignKey(c => c.OwnerAccountId).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<ConsultationMessage>().HasKey(m => m.MessageId);
            modelBuilder.Entity<ConsultationMessage>().HasOne(m => m.Consultation).WithMany(c => c.Messages)
                .HasForeignKey(m => m.ConsultationId).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<ConsultationMessage>().HasOne(m => m.SenderAccount).WithMany()
                .HasForeignKey(m => m.SenderAccountId).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<ConsultationMessage>().HasIndex(m => new { m.ConsultationId, m.MessageId });

            // Cấu hình 9: Quan hệ giữa Class và ClassSchedule (Lịch học chi tiết)
            // 1 lớp học có nhiều ca học trong tuần; nếu xóa lớp thì các ca học bị xóa theo (Cascade)
            modelBuilder.Entity<ClassSchedule>()
                .HasOne(cs => cs.Class)
                .WithMany(c => c.Schedules)
                .HasForeignKey(cs => cs.ClassId)
                .OnDelete(DeleteBehavior.Cascade);

            // Cấu hình 10: Quan hệ giữa Class và ClassDocument (Tài liệu bài giảng)
            modelBuilder.Entity<ClassDocument>()
                .HasOne(cd => cd.Class)
                .WithMany(c => c.Documents)
                .HasForeignKey(cd => cd.ClassId)
                .OnDelete(DeleteBehavior.Cascade);

            // Cấu hình 11: Quan hệ của CourseFeedback (Phản hồi đánh giá khóa học)
            modelBuilder.Entity<CourseFeedback>()
                .HasOne(cf => cf.Student)
                .WithMany()
                .HasForeignKey(cf => cf.StudentId)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<CourseFeedback>()
                .HasOne(cf => cf.Class)
                .WithMany()
                .HasForeignKey(cf => cf.ClassId)
                .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
