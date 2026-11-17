from pathlib import Path
p=Path('WedEnglishApp/Views/Program/Detail.cshtml');s=p.read_text(encoding='utf8').replace('row g-5','row g-4 g-lg-5');p.write_text(s,encoding='utf8')
p=Path('WedEnglishApp/Views/Shared/_AvailableClasses.cshtml');s=p.read_text(encoding='utf8');a=s.index('@foreach (var group');b=s.index('                <div class="col-lg-6">',a);s=s[:a]+'''<div class="row g-3">
    @foreach (var cls in current.OrderBy(c => c.StartDate.Date < today).ThenBy(c => c.StartDate))
    {
        var isUpcoming = cls.StartDate.Date >= today;
'''+s[b:];a=s.rindex('            }');s=s[:a]+'''    }
</div>
''';s=s.replace('    var upcoming = current.Where(c => c.StartDate.Date >= today).OrderBy(c => c.StartDate).ToList();\n','').replace('    var ongoing = current.Where(c => c.StartDate.Date < today).OrderBy(c => c.EndDate).ToList();\n','');p.write_text(s,encoding='utf8')
p=Path('session-state/check-class-preview.cjs');s=p.read_text(encoding='utf-8-sig').replace("section.getByRole('heading',{name:'Sắp khai giảng',exact:true})","section.locator('article .badge').filter({hasText:'Sắp khai giảng'})");s=s.replace("await section.screenshot", "await p.addStyleTag({content:'.sticky-top { position: static !important; }'});await section.screenshot");p.write_text(s,encoding='utf8')
