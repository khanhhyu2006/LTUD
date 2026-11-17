from pathlib import Path
p=Path('session-state/check-portal-fixtures.cjs');s=p.read_text(encoding='utf-8-sig')
a="await p.goto('http://127.0.0.1:5270/Account/Login',{waitUntil:'networkidle'});const bootstrap=await p.evaluate(async()=>await(await fetch('https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css')).text());"
s=s.replace(a,"const bootstrap=await(await p.request.get('https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css')).text();")
s=s.replace('table table-hover align-middle mb-0',"table table-hover align-middle mb-0 ${folder==='TeacherManager'?'table-people':''}")
s=s.replace("table:document.querySelector('.table-responsive').scrollWidth","table:document.querySelector('.table-responsive').scrollWidth, frame:document.querySelector('.table-responsive').clientWidth, clippedButtons:[...document.querySelectorAll('td .btn')].filter(e=>{const r=e.getBoundingClientRect(),c=e.closest('td').getBoundingClientRect();return r.left<c.left-1||r.right>c.right+1}).length")
s=s.replace('x.body>x.width+1||Math.max(...x.headerHeights)>70','x.body>x.width+1||(x.width>=768&&x.table>x.frame+1)||x.clippedButtons>0')
s=s.replace("folder==='ClassManager'||folder==='TeachingClass'","folder==='TeacherManager'||folder==='TeachingClass'")
Path('session-state/check-portal-fit.cjs').write_text(s,encoding='utf8')
