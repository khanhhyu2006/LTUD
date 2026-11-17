from pathlib import Path
for f in ['Controllers/StudentController.cs','Areas/Admin/Controllers/PaymentAdminController.cs','Areas/Admin/Controllers/TrashController.cs']:
 p=Path('WedEnglishApp')/f;s=p.read_text(encoding='utf8');s=s.replace('.Include(p => p.Registration).ThenInclude(r => r.Program)\n', '.Include(p => p.Registration).ThenInclude(r => r.Program)\n                .Include(p => p.Registration)\n');p.write_text(s,encoding='utf8')
for f in ['Views/Shared/_AvailableClasses.cshtml','Areas/Admin/Views/RegistrationAdmin/Index.cshtml']:
 p=Path('WedEnglishApp')/f;s=p.read_text(encoding='utf8').replace('hh\\:mm','hh\\\\:mm');p.write_text(s,encoding='utf8')
p=Path('WedEnglishApp/Data/DbInitializer.cs');s=p.read_text(encoding='utf8').replace('reg.ProgramId = cls.ProgramId','reg.ProgramId = assignedClass.ProgramId');p.write_text(s,encoding='utf8')
