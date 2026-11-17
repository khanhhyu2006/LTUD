using BCrypt.Net;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Models;

namespace WedEnglishApp.Data
{
    public static class DbInitializer
    {
        public static void Initialize(ApplicationDbContext context)
        {
            context.Database.EnsureCreated();
            CourseEnrollmentSchema.Upgrade(context);
            ExamSessionSchema.Upgrade(context);
            ConsultationChatSchema.Upgrade(context);
            CriteriaCompletionSchema.Upgrade(context);

            // Đảm bảo cột Room tồn tại trong bảng PlacementTests
            try
            {
                context.Database.ExecuteSqlRaw(@"
                    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'PlacementTests' AND COLUMN_NAME = 'Room')
                    BEGIN
                        ALTER TABLE PlacementTests ADD Room NVARCHAR(100) NULL;
                    END
                ");
            }
            catch { }

            // Nếu đã có dữ liệu UserAccounts thì không cần seed lại
            if (context.UserAccounts.Any())
            {
                CourseEnrollmentSchema.AlignData(context);
                return;
            }

            string defaultHash = BCrypt.Net.BCrypt.HashPassword("123456");

            // 1. SEED ADMIN
            var adminUser = new UserAccount
            {
                FullName = "Quản Trị Viên Hệ Thống",
                Email = "admin@englishcenter.edu.vn",
                PasswordHash = defaultHash,
                Role = "Admin",
                AvatarUrl = "/images/avatars/admin.png",
                IsActive = true,
                CreatedAt = DateTime.Now.AddMonths(-6)
            };
            context.UserAccounts.Add(adminUser);
            context.SaveChanges();

            // 2. SEED 3 GIÁO VIÊN (TEACHERS)
            var teacherUsers = new List<UserAccount>
            {
                new UserAccount { FullName = "ThS. Trần Thị Mai", Email = "maitt@englishcenter.edu.vn", PasswordHash = defaultHash, Role = "Teacher", AvatarUrl = "/images/avatars/teacher1.png", IsActive = true, CreatedAt = DateTime.Now.AddMonths(-5) },
                new UserAccount { FullName = "Thầy John Smith", Email = "john.smith@englishcenter.edu.vn", PasswordHash = defaultHash, Role = "Teacher", AvatarUrl = "/images/avatars/teacher2.png", IsActive = true, CreatedAt = DateTime.Now.AddMonths(-5) },
                new UserAccount { FullName = "Cô Lê Thanh Hằng", Email = "hanglt@englishcenter.edu.vn", PasswordHash = defaultHash, Role = "Teacher", AvatarUrl = "/images/avatars/teacher3.png", IsActive = true, CreatedAt = DateTime.Now.AddMonths(-5) }
            };
            context.UserAccounts.AddRange(teacherUsers);
            context.SaveChanges();

            var teachers = new List<Teacher>
            {
                new Teacher { AccountId = teacherUsers[0].AccountId, Specialization = "IELTS Chuyên Sâu, Writing & Speaking", Degree = "Thạc sĩ TESOL - ĐH Melbourne", Bio = "Hơn 8 năm kinh nghiệm giảng dạy luyện thi IELTS mục tiêu 7.0+" },
                new Teacher { AccountId = teacherUsers[1].AccountId, Specialization = "Tiếng Anh Giao Tiếp & Phát Âm Bản Ngữ", Degree = "Chứng chỉ CELTA (Cambridge)", Bio = "Giảng viên bản ngữ đến từ Anh Quốc với phương pháp phản xạ tự nhiên" },
                new Teacher { AccountId = teacherUsers[2].AccountId, Specialization = "TOEIC 4 Kỹ Năng & Ngữ Pháp Thực Chiến", Degree = "Cử nhân Ngôn ngữ Anh - ĐH Sư Phạm", Bio = "Chuyên gia đào tạo TOEIC với nhiều mẹo làm bài đạt 800+ trong thời gian ngắn" }
            };
            context.Teachers.AddRange(teachers);
            context.SaveChanges();

            // 3. SEED 10 HỌC VIÊN (STUDENTS)
            var studentUsers = new List<UserAccount>();
            for (int i = 1; i <= 10; i++)
            {
                studentUsers.Add(new UserAccount
                {
                    FullName = $"Học Viên Nguyễn Văn {i}",
                    Email = $"hocvien{i}@gmail.com",
                    PasswordHash = defaultHash,
                    Role = "Student",
                    AvatarUrl = $"/images/avatars/student{i}.png",
                    IsActive = true,
                    CreatedAt = DateTime.Now.AddDays(-30 - i)
                });
            }
            context.UserAccounts.AddRange(studentUsers);
            context.SaveChanges();

            var students = new List<Student>();
            for (int i = 0; i < studentUsers.Count; i++)
            {
                students.Add(new Student
                {
                    AccountId = studentUsers[i].AccountId,
                    PhoneNumber = $"090912340{i}",
                    Address = $"{100 + i} Đỗ Xuân Hợp, TP. Thủ Đức, TP.HCM",
                    DateOfBirth = new DateTime(2002, 1 + (i % 12), 15)
                });
            }
            context.Students.AddRange(students);
            context.SaveChanges();

            // 4. SEED 5 CHƯƠNG TRÌNH HỌC (PROGRAMS)
            var programs = new List<CourseProgram>
            {
                new CourseProgram
                {
                    ProgramName = "IELTS Master Bứt Phá (Mục tiêu 6.5 - 7.5+)",
                    Level = "Advanced",
                    DurationWeeks = 12,
                    TuitionFee = 6800000,
                    Description = "Khóa học rèn luyện toàn diện 4 kỹ năng Nghe - Nói - Đọc - Viết theo tiêu chuẩn đề thi thực tế.",
                    LearningOutcomes = "Đạt band điểm IELTS 6.5 - 7.5+, thành thạo viết luận Task 2 và kỹ năng phỏng vấn học thuật.",
                    ImageUrl = "/images/courses/ielts-master.jpg",
                    IsActive = true
                },
                new CourseProgram
                {
                    ProgramName = "TOEIC 4 Kỹ Năng Cấp Tốc (Mục tiêu 750+)",
                    Level = "Intermediate",
                    DurationWeeks = 10,
                    TuitionFee = 4200000,
                    Description = "Luyện chiến thuật làm bài thi TOEIC mới nhất, rèn luyện nghe hiểu và phản xạ công sở.",
                    LearningOutcomes = "Đạt tối thiểu 750 điểm TOEIC, tự tin giao tiếp và viết email chuyên nghiệp trong môi trường doanh nghiệp.",
                    ImageUrl = "/images/courses/toeic-speed.jpg",
                    IsActive = true
                },
                new CourseProgram
                {
                    ProgramName = "Tiếng Anh Giao Tiếp Phản Xạ Quốc Tế",
                    Level = "Beginner",
                    DurationWeeks = 8,
                    TuitionFee = 3500000,
                    Description = "Dành cho người mất gốc, tập trung chuẩn hóa phát âm IPA và tăng phản xạ đàm thoại hàng ngày.",
                    LearningOutcomes = "Lấy lại căn bản, phát âm chuẩn ngữ điệu, giao tiếp tự tin các tình huống du lịch, làm việc.",
                    ImageUrl = "/images/courses/english-communication.jpg",
                    IsActive = true
                },
                new CourseProgram
                {
                    ProgramName = "Tiếng Anh Thương Mại Doanh Nghiệp (Business English)",
                    Level = "Intermediate",
                    DurationWeeks = 10,
                    TuitionFee = 5500000,
                    Description = "Kỹ năng thuyết trình, đàm phán hợp đồng, viết báo cáo và giao dịch thương mại quốc tế.",
                    LearningOutcomes = "Làm chủ từ vựng chuyên ngành kinh tế, tự tin thương thuyết và làm việc trong công ty đa quốc gia.",
                    ImageUrl = "/images/courses/business-english.jpg",
                    IsActive = true
                },
                new CourseProgram
                {
                    ProgramName = "Luyện Thi Cambridge B1/B2 Tiêu Chuẩn",
                    Level = "Intermediate",
                    DurationWeeks = 12,
                    TuitionFee = 4800000,
                    Description = "Chuẩn bị kiến thức vững vàng cho kỳ thi chứng chỉ khung tham chiếu Châu Âu CEFR B1/B2.",
                    LearningOutcomes = "Đạt chứng chỉ B1/B2 Cambridge đủ điều kiện chuẩn đầu ra tốt nghiệp đại học, cao học.",
                    ImageUrl = "/images/courses/cambridge.jpg",
                    IsActive = true
                }
            };
            context.Programs.AddRange(programs);
            context.SaveChanges();

            // 5. SEED 10 LỚP HỌC (CLASSES)
            var classes = new List<CourseClass>
            {
                new CourseClass { ProgramId = programs[0].ProgramId, TeacherId = teachers[0].TeacherId, ClassName = "IELTS-K26-T246", Room = "Phòng Lab 201", MaxStudents = 20, StartDate = DateTime.Now.AddDays(7), EndDate = DateTime.Now.AddDays(90), Status = "Planning" },
                new CourseClass { ProgramId = programs[0].ProgramId, TeacherId = teachers[0].TeacherId, ClassName = "IELTS-K27-T357", Room = "Phòng Lab 202", MaxStudents = 20, StartDate = DateTime.Now.AddDays(-14), EndDate = DateTime.Now.AddDays(70), Status = "InProgress" },
                new CourseClass { ProgramId = programs[1].ProgramId, TeacherId = teachers[2].TeacherId, ClassName = "TOEIC-K15-T246", Room = "Phòng 301", MaxStudents = 25, StartDate = DateTime.Now.AddDays(10), EndDate = DateTime.Now.AddDays(80), Status = "Planning" },
                new CourseClass { ProgramId = programs[1].ProgramId, TeacherId = teachers[2].TeacherId, ClassName = "TOEIC-K16-T357", Room = "Phòng 302", MaxStudents = 25, StartDate = DateTime.Now.AddDays(-30), EndDate = DateTime.Now.AddDays(40), Status = "InProgress" },
                new CourseClass { ProgramId = programs[2].ProgramId, TeacherId = teachers[1].TeacherId, ClassName = "COMM-K10-T246", Room = "Phòng Hội Thảo A", MaxStudents = 18, StartDate = DateTime.Now.AddDays(5), EndDate = DateTime.Now.AddDays(60), Status = "Planning" },
                new CourseClass { ProgramId = programs[2].ProgramId, TeacherId = teachers[1].TeacherId, ClassName = "COMM-K11-T357", Room = "Phòng Hội Thảo B", MaxStudents = 18, StartDate = DateTime.Now.AddDays(-20), EndDate = DateTime.Now.AddDays(35), Status = "InProgress" },
                new CourseClass { ProgramId = programs[3].ProgramId, TeacherId = teachers[0].TeacherId, ClassName = "BIZ-K05-T246", Room = "Phòng 401", MaxStudents = 15, StartDate = DateTime.Now.AddDays(15), EndDate = DateTime.Now.AddDays(85), Status = "Planning" },
                new CourseClass { ProgramId = programs[3].ProgramId, TeacherId = teachers[0].TeacherId, ClassName = "BIZ-K06-T7CN", Room = "Phòng 402", MaxStudents = 15, StartDate = DateTime.Now.AddDays(-40), EndDate = DateTime.Now.AddDays(30), Status = "InProgress" },
                new CourseClass { ProgramId = programs[4].ProgramId, TeacherId = teachers[2].TeacherId, ClassName = "CAMB-K08-T246", Room = "Phòng 102", MaxStudents = 22, StartDate = DateTime.Now.AddDays(12), EndDate = DateTime.Now.AddDays(95), Status = "Planning" },
                new CourseClass { ProgramId = programs[4].ProgramId, TeacherId = teachers[2].TeacherId, ClassName = "CAMB-K09-T357", Room = "Phòng 103", MaxStudents = 22, StartDate = DateTime.Now.AddDays(-50), EndDate = DateTime.Now.AddDays(20), Status = "InProgress" }
            };
            context.Classes.AddRange(classes);
            context.SaveChanges();

            // 6. SEED LỊCH HỌC CHO CÁC LỚP (CLASS SCHEDULES)
            var schedules = new List<ClassSchedule>();
            foreach (var cls in classes)
            {
                if (cls.ClassName.Contains("T246"))
                {
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 2, StartTime = new TimeSpan(18, 0, 0), EndTime = new TimeSpan(19, 30, 0) });
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 4, StartTime = new TimeSpan(18, 0, 0), EndTime = new TimeSpan(19, 30, 0) });
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 6, StartTime = new TimeSpan(18, 0, 0), EndTime = new TimeSpan(19, 30, 0) });
                }
                else if (cls.ClassName.Contains("T357"))
                {
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 3, StartTime = new TimeSpan(19, 30, 0), EndTime = new TimeSpan(21, 0, 0) });
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 5, StartTime = new TimeSpan(19, 30, 0), EndTime = new TimeSpan(21, 0, 0) });
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 7, StartTime = new TimeSpan(19, 30, 0), EndTime = new TimeSpan(21, 0, 0) });
                }
                else
                {
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 7, StartTime = new TimeSpan(8, 0, 0), EndTime = new TimeSpan(11, 0, 0) });
                    schedules.Add(new ClassSchedule { ClassId = cls.ClassId, DayOfWeek = 8, StartTime = new TimeSpan(8, 0, 0), EndTime = new TimeSpan(11, 0, 0) });
                }
            }
            context.ClassSchedules.AddRange(schedules);
            context.SaveChanges();

            // 7. SEED 20 LƯỢT ĐĂNG KÝ VÀ THANH TOÁN (REGISTRATIONS & PAYMENTS)
            var registrations = new List<Registration>();
            var payments = new List<Payment>();

            int regIndex = 1;
            for (int s = 0; s < students.Count; s++)
            {
                // Mỗi học viên đăng ký 2 lớp -> 10 học viên * 2 = 20 lượt đăng ký
                for (int c = 0; c < 2; c++)
                {
                    var assignedProgram = programs[(s + c) % programs.Count];
                    var assignedClass = classes.Where(cl => cl.ProgramId == assignedProgram.ProgramId).ElementAt(c % 2);

                    string regStatus = (regIndex % 3 == 0) ? "Pending" : "Confirmed";

                    var reg = new Registration
                    {
                        StudentId = students[s].StudentId,
                        ClassId = regStatus == "Confirmed" ? assignedClass.ClassId : null,
                        ProgramId = assignedProgram.ProgramId,
                        EarliestStartDate = regStatus == "Confirmed" ? assignedClass.StartDate.Date : DateTime.Today.AddDays(7),
                        PreferredDays = c % 2 == 0 ? "2,4,6" : "3,5,7",
                        PreferredSession = "Evening",
                        RegistrationDate = DateTime.Now.AddDays(-15 + (regIndex % 10)),
                        Status = regStatus
                    };
                    registrations.Add(reg);
                    reg.ProgramId = assignedClass.ProgramId;
                    context.Registrations.Add(reg);
                    context.SaveChanges(); // Lưu để có RegistrationId

                    // Tạo hóa đơn Payment tương ứng
                    string payStatus = (regStatus == "Confirmed") ? "Paid" : "Pending";
                    string payMethod = (regIndex % 2 == 0) ? "VietQR" : "Cash";

                    payments.Add(new Payment
                    {
                        RegistrationId = reg.RegistrationId,
                        Amount = assignedProgram.TuitionFee,
                        PaymentDate = DateTime.Now.AddDays(-14 + (regIndex % 10)),
                        PaymentMethod = payMethod,
                        TransactionCode = payMethod == "VietQR" ? $"HPREG{reg.RegistrationId}" : null,
                        Status = payStatus
                    });

                    regIndex++;
                }
            }
            context.Payments.AddRange(payments);
            context.SaveChanges();

            // 8. SEED 10 BẢN GHI KIỂM TRA XẾP LỚP (PLACEMENT TESTS)
            var tests = new List<PlacementTest>();
            string[] testTimes = { "08:30 AM", "10:00 AM", "02:00 PM", "04:00 PM", "06:30 PM" };
            string[] recLevels = { "IELTS Master 6.5+", "TOEIC Cấp Tốc 750", "Giao Tiếp Phản Xạ", "Cambridge B2", "Tiếng Anh Cơ Bản" };

            for (int i = 0; i < students.Count; i++)
            {
                bool isCompleted = (i < 7); // 7 bài đã chấm, 3 bài đang chờ
                tests.Add(new PlacementTest
                {
                    StudentId = students[i].StudentId,
                    EvaluatedByTeacherId = isCompleted ? teachers[i % teachers.Count].TeacherId : null,
                    TestDate = DateTime.Now.AddDays(-20 + i * 2),
                    TestTime = testTimes[i % testTimes.Length],
                    Score = isCompleted ? (decimal?)(6.0m + (i % 4) * 0.5m) : null,
                    RecommendedLevel = isCompleted ? recLevels[i % recLevels.Length] : null,
                    Status = isCompleted ? "Completed" : "Pending"
                });
            }
            context.PlacementTests.AddRange(tests);
            context.SaveChanges();

            // 9. SEED MẪU CÂU HỎI TƯ VẤN (CONSULTATIONS)
            var consultations = new List<Consultation>
            {
                new Consultation { ContactName = "Lê Hoàng Quân", ContactEmail = "quan.le@gmail.com", PhoneNumber = "0987654321", Question = "Cho em hỏi học phí khóa IELTS 6.5 có được chia làm 2 đợt đóng không ạ?", Status = "Replied", CreatedAt = DateTime.Now.AddDays(-5) },
                new Consultation { ContactName = "Phạm Thị Thảo", ContactEmail = "thao.pham@gmail.com", PhoneNumber = "0912345678", Question = "Em mất gốc tiếng Anh thì nên đăng ký bài kiểm tra xếp lớp trước hay học lớp Giao tiếp phản xạ?", Status = "Pending", CreatedAt = DateTime.Now.AddDays(-1) }
            };
            context.Consultations.AddRange(consultations);
            context.SaveChanges();

            // 10. SEED ĐÁNH GIÁ & PHẢN HỒI (COURSE FEEDBACKS)
            var feedbacks = new List<CourseFeedback>
            {
                new CourseFeedback { StudentId = students[0].StudentId, ClassId = classes[1].ClassId, Rating = 5, Comment = "Cô Mai giảng dạy rất nhiệt tình, sửa phát âm và bài viết luận Task 2 cực kỳ chi tiết!", CreatedAt = DateTime.Now.AddDays(-10) },
                new CourseFeedback { StudentId = students[1].StudentId, ClassId = classes[3].ClassId, Rating = 5, Comment = "Khóa học TOEIC giúp mình tăng hơn 200 điểm sau 2 tháng, thầy cô hướng dẫn mẹo nghe rất dễ hiểu.", CreatedAt = DateTime.Now.AddDays(-8) },
                new CourseFeedback { StudentId = students[2].StudentId, ClassId = classes[5].ClassId, Rating = 4, Comment = "Phương pháp phản xạ của thầy John giúp mình tự tin giao tiếp tiếng Anh hơn rất nhiều.", CreatedAt = DateTime.Now.AddDays(-3) }
            };
            context.CourseFeedbacks.AddRange(feedbacks);
            context.SaveChanges();

            // 11. SEED BANNER QUẢNG BÁ TRÊN TRANG CHỦ (BANNERS)
            if (!context.Banners.Any())
            {
                var banners = new List<Banner>
                {
                    new Banner
                    {
                        Title = "Khai Giảng Các Khóa Học Mới 2026",
                        Subtitle = "Chương trình đào tạo chuẩn quốc tế Cambridge, lộ trình bứt phá IELTS 7.5+, TOEIC 800+ với 100% giảng viên chuyên môn cao và giáo viên bản ngữ.",
                        ImageUrl = "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1400&q=80",
                        LinkUrl = "/Program",
                        ButtonText = "Khám phá khóa học",
                        DisplayOrder = 1,
                        IsActive = true,
                        CreatedAt = DateTime.Now
                    },
                    new Banner
                    {
                        Title = "Thi Xếp Lớp & Kiểm Tra Năng Lực Miễn Phí",
                        Subtitle = "Đánh giá chính xác trình độ tiếng Anh 4 kỹ năng của bạn cùng giảng viên khảo thí, nhận ngay tư vấn lộ trình học phù hợp nhất.",
                        ImageUrl = "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1400&q=80",
                        LinkUrl = "/PlacementTest/BookTest",
                        ButtonText = "Thi xếp lớp ngay",
                        DisplayOrder = 2,
                        IsActive = true,
                        CreatedAt = DateTime.Now
                    },
                    new Banner
                    {
                        Title = "Khóa Luyện Thi IELTS Master 6.5+ Cấp Tốc",
                        Subtitle = "Cam kết đầu ra bằng văn bản, phương pháp rèn luyện tư duy phản xạ tiếng Anh tự nhiên và chiến thuật giải đề thi thực chiến.",
                        ImageUrl = "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1400&q=80",
                        LinkUrl = "/Program/Detail/1",
                        ButtonText = "Đăng ký khóa học",
                        DisplayOrder = 3,
                        IsActive = true,
                        CreatedAt = DateTime.Now
                    }
                };
                context.Banners.AddRange(banners);
                context.SaveChanges();
            }
            CourseEnrollmentSchema.AlignData(context);
            ExamSessionSchema.Upgrade(context);
            ConsultationChatSchema.Upgrade(context);
            CriteriaCompletionSchema.Upgrade(context);
        }

    }
}
