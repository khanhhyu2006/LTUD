from pathlib import Path
base=Path('WedEnglishApp')
def edit(f,a,b):
 p=base/f;s=p.read_text(encoding='utf8');assert a in s,(f,a);p.write_text(s.replace(a,b),encoding='utf8')
edit('Views/Shared/_AvailableClasses.cshtml','<h5>@cls.ClassName</h5>','<div class="text-primary small mb-1">@cls.Program.ProgramName</div><h5>@cls.ClassName</h5>')
edit('Views/Program/Index.cshtml','Xem chi tiết & Lớp mở','Xem khóa học và đăng ký')
edit('Models/Registration.cs','// Mục đích: Cầu nối liên kết giữa Học viên (Student) và Lớp học (Class), lưu trạng thái ghi danh','// Mục đích: Ghi danh khóa học và lưu nguyện vọng; ClassId được gán sau khi Admin xếp lớp.')
edit('Models/Registration.cs','// Trạng thái đơn: "Pending" (Chờ thanh toán), "Confirmed" (Đã duyệt vào lớp), "Cancelled" (Đã hủy)','// Pending: chờ xếp lớp; Confirmed: Admin đã xếp lớp; Cancelled: đã hủy. Độc lập trạng thái học phí.')
edit('Controllers/StudentController.cs','            // Tạo bản ghi CourseFeedback mới','''            if (!await _context.Registrations.AnyAsync(r => r.StudentId == studentId && r.ClassId == classId && !r.IsDeleted && r.Status == "Confirmed"))
                return Forbid();

            // Tạo bản ghi CourseFeedback mới''')
edit('Areas/Admin/Controllers/TrashController.cs','if (program.Classes.Any(c => !c.IsDeleted))','if (program.Classes.Any(c => !c.IsDeleted) || await _context.Registrations.AnyAsync(r => r.ProgramId == id))')
edit('Areas/Admin/Controllers/TrashController.cs','Không thể xóa vĩnh viễn chương trình vì vẫn còn lớp học liên kết chưa xóa!','Không thể xóa vĩnh viễn khóa học vì vẫn còn lớp học hoặc đơn đăng ký liên kết!')
edit('Areas/Admin/Controllers/TrashController.cs','var safePrograms = deletedPrograms.Where(p => !p.Classes.Any(c => !c.IsDeleted)).ToList();','''var retainedProgramIds = await _context.Registrations.Where(r => !r.IsDeleted).Select(r => r.ProgramId).Distinct().ToListAsync();
            var safePrograms = deletedPrograms.Where(p => !p.Classes.Any(c => !c.IsDeleted) && !retainedProgramIds.Contains(p.ProgramId)).ToList();''')
# Avoid loading the same program repeatedly in the student query.
p=base/'Controllers/StudentController.cs';s=p.read_text(encoding='utf8');s=s.replace('                .Include(r => r.Program)\n                .Include(r => r.Class)','                .Include(r => r.Class)');s=s.replace('var registrations = await _context.Registrations\n','var registrations = await _context.Registrations\n                .Include(r => r.Program)\n');p.write_text(s,encoding='utf8')
