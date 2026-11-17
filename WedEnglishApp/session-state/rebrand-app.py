from pathlib import Path
import hashlib, json

root=Path(__file__).resolve().parents[1]
app=root/'WedEnglishApp'
changed=[]
replacements=[
 ('<span>HITC</span> English','@WedEnglishApp.Services.SiteBrand.Name'),
 ('TRUNG TÂM NGOẠI NGỮ QUỐC TẾ HITC','Trung tâm ngoại ngữ @WedEnglishApp.Services.SiteBrand.Name'),
 ('Trung Tâm Ngoại Ngữ Quốc Tế HITC','Trung tâm ngoại ngữ @WedEnglishApp.Services.SiteBrand.Name'),
 ('Trung Tâm Ngoại Ngữ HITC','Trung tâm ngoại ngữ @WedEnglishApp.Services.SiteBrand.Name'),
 ('HITC ENGLISH CENTER','@WedEnglishApp.Services.SiteBrand.Name'),
 ('HITC English Center','@WedEnglishApp.Services.SiteBrand.Name'),
 ('HITC English','@WedEnglishApp.Services.SiteBrand.Name'),
 ('contact@hitc.edu.vn','@WedEnglishApp.Services.SiteBrand.ContactEmail'),
 ('tuyensinh@hitc.edu.vn','@WedEnglishApp.Services.SiteBrand.AdmissionsEmail'),
 ('HITC/2026','@(WedEnglishApp.Services.SiteBrand.ReceiptPrefix)/@DateTime.Now.Year'),
 ('TRUNG%20TAM%20NGOAI%20NGU%20HITC','@Uri.EscapeDataString(WedEnglishApp.Services.SiteBrand.PaymentAccountName)'),
 ('TRUNG TAM NGOAI NGU HITC','@WedEnglishApp.Services.SiteBrand.PaymentAccountName'),
]
for p in app.rglob('*.cshtml'):
 if any(x in p.parts for x in ('bin','obj')):continue
 s=p.read_text(encoding='utf-8-sig');new=s
 for a,b in replacements:new=new.replace(a,b)
 if new!=s:
  p.write_text(new,encoding='utf-8');changed.append(str(p.relative_to(root)))
# A longer brand must wrap within the narrow portal sidebar.
p=app/'wwwroot/css/portal-layout.css'
s=p.read_text(encoding='utf-8')
s+='\n/* Keep the full center name readable in both portal sidebars. */\n.portal-shell .sidebar-brand > div { min-width: 0; }\n.portal-shell .sidebar-brand .fw-bold { line-height: 1.35; overflow-wrap: anywhere; }\n'
p.write_text(s,encoding='utf-8')
# Capture pre-refresh image hashes so DOCX media can be replaced without changing content.
assets=root/'docs/report-work/final-refresh/assets'
manifest={hashlib.sha256(p.read_bytes()).hexdigest():p.name for p in assets.glob('*.png')}
(root/'session-state/rebrand-media-before.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(root/'session-state/rebrand-app-files.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
print('Updated views:',len(changed))
