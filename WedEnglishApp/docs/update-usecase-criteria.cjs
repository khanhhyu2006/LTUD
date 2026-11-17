const fs=require('fs'),path=require('path'),sharp=require('sharp');
const OUT=path.resolve('docs/diagrams-clear');fs.mkdirSync(OUT,{recursive:true});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function base(w,h){return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial,'Segoe UI',sans-serif;fill:#172b3a}path,line,ellipse{stroke-linejoin:round;stroke-linecap:round}</style><defs><marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1L9 5L1 9" fill="none" stroke="#263c4b" stroke-width="1.6"/></marker></defs>`;}
function text(x,y,t,size=24,anchor='start',bold=false){return `<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}"${bold?' font-weight="bold"':''}>${esc(t)}</text>`;}
async function save(name,s,w){fs.writeFileSync(path.join(OUT,name+'.svg'),s);await sharp(Buffer.from(s)).resize({width:w}).png().toFile(path.join(OUT,name+'.png'));await sharp(Buffer.from(s)).resize({width:1400}).png().toFile(path.join(OUT,name+'-preview.png'));}
async function usecase(){
 const data=JSON.parse(fs.readFileSync('docs/diagrams-clear/overview-criteria.json','utf8'));const W=2320,H=3150;let s=base(W,H);
 s+=text(W/2,52,'SƠ ĐỒ USE CASE TỔNG QUÁT',36,'middle',true)+text(W/2,91,'Hệ thống trung tâm ngoại ngữ NHK English times',28,'middle');
 s+='<rect x="170" y="125" width="1980" height="2900" fill="none" stroke="#263c4b" stroke-width="2.3"/>';
 s+='<path d="M1160 145V3005M190 1335H2130" stroke="#d3dbe0" stroke-width="1.5" fill="none" stroke-dasharray="8 9"/>';
 const roles=[['Guest','KHÁCH',210,1210,180,1010],['Teacher','GIÁO VIÊN',210,1285,2140,1310],['Student','HỌC VIÊN',1400,2980,180,1010],['Admin','QUẢN TRỊ VIÊN',1400,2980,2140,1310]];
 for(const [role,label,top,bottom,_,cx]of roles){
  const right=['Teacher','Admin'].includes(role),ax=right?2230:90;
  const items=data.nodes.filter(n=>n.role===role).map(n=>({...n}));
  if(role==='Student')items.push({id:role+'register',lines:['Đăng ký tài khoản học viên'],auth:true});
  if(role==='Admin')items.push({id:'AdmincreateTeacher',lines:['Tạo / cấp tài khoản giáo viên'],auth:true});
  items.push({id:role+'login',lines:[role==='Guest'?'Đăng nhập tài khoản đã có':role==='Student'?'Đăng nhập tài khoản học viên':role==='Teacher'?'Đăng nhập tài khoản giáo viên':'Đăng nhập tài khoản Admin'],auth:true});
  if(role!=='Guest')items.push({id:role+'pass',lines:['Đổi mật khẩu']},{id:role+'logout',lines:['Đăng xuất']});
  for(const item of items)if(item.id==='g3'||item.id.endsWith('pass')||item.id.endsWith('logout'))item.auth=true;
  items.sort((a,b)=>Number(!!b.auth)-Number(!!a.auth));
  const y0=top+80,step=Math.min(106,(bottom-y0-45)/(items.length-1)),ay=(y0+y0+(items.length-1)*step)/2;
  s+=text(right?1640:680,top+8,label,27,'middle',true);
  const note=role==='Teacher'?'Tài khoản do Admin cấp':role==='Admin'?'Tài khoản Admin được khởi tạo sẵn':role==='Student'?'Học viên được tự đăng ký tài khoản':'Đăng ký học viên hoặc đăng nhập tài khoản đã có';
  s+=text(right?1640:680,top+41,note,20,'middle');
  const byid={};items.forEach((n,i)=>{n.x=right?1580:740;n.y=y0+i*step;n.rx=310;n.ry=n.lines.length>1?37:31;byid[n.id]=n;});
  const inc=data.includes.filter(([a])=>byid[a]);const targets=new Set(inc.map(x=>x[1]));
  for(const n of items){if(targets.has(n.id))continue;const edge=n.x+(right?1:-1)*n.rx;
   s+=`<path d="M${ax+(right?-20:20)} ${ay}L${edge} ${n.y}" fill="none" stroke="#627580" stroke-width="1.6"/>`;
  }
  for(const [a,b]of inc){const n=byid[a],m=byid[b],x=n.x+(right?-1:1)*n.rx,lane=x+(right?-1:1)*55;
   s+=`<path d="M${x} ${n.y}H${lane}V${m.y}H${x}" fill="none" stroke="#263c4b" stroke-width="1.8" stroke-dasharray="7 5" marker-end="url(#arr)"/>`;
   s+=`<rect x="${lane-49}" y="${(n.y+m.y)/2-11}" width="98" height="23" fill="white"/>`+text(lane,(n.y+m.y)/2+6,'«include»',17,'middle');
  }
  for(const n of items){s+=`<ellipse cx="${n.x}" cy="${n.y}" rx="${n.rx}" ry="${n.ry}" fill="${n.auth?'#edf5ff':'white'}" stroke="${n.auth?'#235d91':'#263c4b'}" stroke-width="${n.auth?2.2:1.7}"/>`;n.lines.forEach((t,j)=>s+=text(n.x,n.y+8+(j-(n.lines.length-1)/2)*27,t,23,'middle'));}
  s+=`<g fill="white" stroke="#263c4b" stroke-width="2.6"><circle cx="${ax}" cy="${ay-50}" r="19"/><path d="M${ax} ${ay-31}v67m-33-45h66m-33 45l-29 38m29-38l29 38" fill="none"/></g>`;
  const actorlabel={Guest:'Khách',Student:'Học viên',Teacher:'Giáo viên',Admin:'Admin'}[role];s+=text(ax,ay+108,actorlabel,24,'middle',true);
 }
 s+=text(W/2,3072,'Đường liền: tương tác với tác nhân.  «include»: chức năng con bắt buộc.',23,'middle');
 s+=text(W/2,3111,'Chức năng tài khoản dùng chung được lặp theo từng tác nhân để tránh đường nối chéo.',22,'middle');
 await save('Use_case_tong_quat_du_tieu_chi',s+'</svg>',3480);
}
class Heap{constructor(){this.a=[];}push(item){let a=this.a;a.push(item);let i=a.length-1;while(i){let p=(i-1)>>1;if(a[p][0]<=item[0])break;a[i]=a[p];i=p;}a[i]=item;}pop(){let a=this.a,r=a[0],v=a.pop();if(a.length){let i=0;while(i*2+1<a.length){let j=i*2+1;if(j+1<a.length&&a[j+1][0]<a[j][0])j++;if(a[j][0]>=v[0])break;a[i]=a[j];i=j;}a[i]=v;}return r;}}
async function erd(){
 const schema=JSON.parse(fs.readFileSync('session-state/report-live-schema.json','utf8'));
 const grid=[['UserAccounts','Students','Teachers','TeacherSalaries'],['Consultations','Programs','Classes','ExamSessions'],['ConsultationMessages','Registrations','ClassSchedules','ClassDocuments'],['Banners','Payments','PlacementTests','CourseFeedbacks']];
 const W=3500,H=3190,pos={};let rowY=[145,895,1645,2395];
 grid.forEach((row,ri)=>row.forEach((name,ci)=>{let fields=schema.columns.filter(c=>c.table===name);pos[name]={x:125+ci*865,y:rowY[ri],w:550,h:55+fields.length*32,fields};}));
 const fks=Object.values(Object.groupBy(schema.foreign_keys,x=>x.name));
 const colors=['#245c8f','#964622','#3e6d42','#754f91','#8a671e','#236e78'];
 const counts={};const ports=[];
 for(const [i,parts]of fks.entries()){
  const f=parts[0],a=pos[f.target_table],b=pos[f.source_table];const ai=a.fields.findIndex(c=>c.name===f.target_column),bi=b.fields.findIndex(c=>c.name===f.source_column);
  const parentKey=f.target_table+'.'+f.target_column;const k=counts[parentKey]||0;counts[parentKey]=k+1;
  const sourceKey=f.source_table+'.'+f.source_column;const kk=counts[sourceKey]||0;counts[sourceKey]=kk+1;
  const ay=a.y+55+ai*32+16+(k%5-2)*5,by=b.y+55+bi*32+16+(kk%5-2)*5;
  const right=b.x>=a.x;const ax=a.x+(right?a.w:0),bx=b.x+(right?0:b.w);let sx=ax+(right?36:-36),ex=bx+(right?-36:36);
  if(a.x===b.x){sx=a.x+a.w+36;ex=b.x+b.w+36;}
  ports.push({i,parts,a,b,ax:a.x===b.x?a.x+a.w:ax,ay,bx:a.x===b.x?b.x+b.w:bx,by,sx,ex,color:colors[i%colors.length]});
 }
 let X=[28,W-28],Y=[112,H-170];
 for(let col=0;col<=4;col++){let l=col===0?28:125+(col-1)*865+550+24,r=col===4?W-28:125+col*865-24;for(let x=l;x<=r;x+=18)X.push(x);}
 for(let row=0;row<=4;row++){let l=row===0?112:Math.max(...grid[row-1].map(n=>pos[n].y+pos[n].h))+24,r=row===4?H-170:rowY[row]-24;for(let y=l;y<=r;y+=18)Y.push(y);}
 for(const p of ports){X.push(p.sx,p.ex);Y.push(p.ay,p.by);}
 X=[...new Set(X)].sort((a,b)=>a-b);Y=[...new Set(Y)].sort((a,b)=>a-b);
 const nx=X.length,ny=Y.length,N=nx*ny,valid=new Uint8Array(N);const boxes=Object.values(pos);
 for(let yi=0;yi<ny;yi++)for(let xi=0;xi<nx;xi++)valid[yi*nx+xi]=!boxes.some(b=>X[xi]>b.x-18&&X[xi]<b.x+b.w+18&&Y[yi]>b.y-18&&Y[yi]<b.y+b.h+18);
 const reserved=new Set(ports.flatMap(p=>[Y.indexOf(p.ay)*nx+X.indexOf(p.sx),Y.indexOf(p.by)*nx+X.indexOf(p.ex)]));
 const usedEdges=new Set(),occupied=new Uint8Array(N),segments=[],paths=[];
 function edgekey(a,b){return a<b?a+':'+b:b+':'+a;}
 const clearCache=new Map();function clearEdge(u,v){const key=edgekey(u,v);if(clearCache.has(key))return clearCache.get(key);const x1=X[u%nx],y1=Y[(u/nx)|0],x2=X[v%nx],y2=Y[(v/nx)|0];const hit=boxes.some(b=>y1===y2?(y1>b.y-18&&y1<b.y+b.h+18&&Math.max(x1,x2)>b.x-18&&Math.min(x1,x2)<b.x+b.w+18):(x1>b.x-18&&x1<b.x+b.w+18&&Math.max(y1,y2)>b.y-18&&Math.min(y1,y2)<b.y+b.h+18));clearCache.set(key,!hit);return !hit;}

 function route(p){
  const start=Y.indexOf(p.ay)*nx+X.indexOf(p.sx),end=Y.indexOf(p.by)*nx+X.indexOf(p.ex),q=new Heap(),dist=new Float64Array(N*2);dist.fill(Infinity);const prev=new Int32Array(N*2);prev.fill(-1);
  const heuristic=n=>Math.abs(X[n%nx]-p.ex)+Math.abs(Y[(n/nx)|0]-p.by);dist[start*2]=0;q.push([heuristic(start),start*2]);let final=-1;
  while(q.a.length){const [score,state]=q.pop(),u=state>>1,di=state&1,cost=dist[state];if(score>cost+heuristic(u)+.001)continue;if(u===end){final=state;break;}
   let xi=u%nx,yi=(u/nx)|0;for(const [v,dir]of [[xi?u-1:-1,0],[xi<nx-1?u+1:-1,0],[yi?u-nx:-1,1],[yi<ny-1?u+nx:-1,1]]){
    if(v<0||!valid[v]||!clearEdge(u,v)||usedEdges.has(edgekey(u,v))||(reserved.has(v)&&v!==end&&v!==start))continue;
    if(occupied[u]&&dir!==di)continue;
    if(occupied[v]===3)continue;
    const len=Math.abs(X[v%nx]-X[xi])+Math.abs(Y[(v/nx)|0]-Y[yi]);let nc=cost+len+(dir!==di?28:0)+(occupied[v]?1200:0);
    let vs=v*2+dir;if(nc<dist[vs]){dist[vs]=nc;prev[vs]=state;q.push([nc+heuristic(v),vs]);}
   }
  }
  if(final<0)throw Error('No route '+p.i);
  let ids=[];for(let st=final;st>=0;st=prev[st])ids.push(st>>1);ids.reverse();let pts=ids.map(n=>[X[n%nx],Y[(n/nx)|0]]);
  for(let i=1;i<ids.length;i++){usedEdges.add(edgekey(ids[i-1],ids[i]));let dir=pts[i][0]===pts[i-1][0]?1:0;occupied[ids[i-1]]|=1<<dir;occupied[ids[i]]|=1<<dir;}
  // Keep bend points; leave space at crossing points so later lines can jump cleanly.
  let poly=[[p.ax,p.ay],pts[0]];for(let i=1;i<pts.length-1;i++)if((pts[i-1][0]===pts[i][0])!==(pts[i][0]===pts[i+1][0]))poly.push(pts[i]);poly.push(pts.at(-1),[p.bx,p.by]);
  paths.push({...p,poly});
 }
 // Dense parent/child relations first, then peripheral edges.
 const order=[...ports].sort((a,b)=>((a.a.x===a.b.x)?0:1)-((b.a.x===b.b.x)?0:1)||Math.abs(a.ay-a.by)-Math.abs(b.ay-b.by));
 for(const p of order)route(p);
 let s=base(W,H)+text(W/2,52,'NHK English times — Sơ đồ quan hệ cơ sở dữ liệu',37,'middle',true)+text(W/2,91,'16 bảng nghiệp vụ · 149 trường · 21 ràng buộc khóa ngoại',25,'middle');
 // Each FK uses its own track. White halos separate perpendicular crossings.
 const priorSegments=[];let bridgeCount=0;
 for(const p of paths){let ds='M'+p.poly[0].join(' ');
  for(let k=1;k<p.poly.length;k++){
   const a=p.poly[k-1],b=p.poly[k],hor=a[1]===b[1],dir=(hor?b[0]-a[0]:b[1]-a[1])>0?1:-1,start=hor?a[0]:a[1],end=hor?b[0]:b[1],fixed=hor?a[1]:a[0];let hits=[];
   for(const [c,d]of priorSegments){if((c[1]===d[1])===hor)continue;const point=hor?c[0]:c[1];const low=hor?Math.min(c[1],d[1]):Math.min(c[0],d[0]),high=hor?Math.max(c[1],d[1]):Math.max(c[0],d[0]);if(point>Math.min(start,end)+10&&point<Math.max(start,end)-10&&fixed>low&&fixed<high)hits.push(point);}
   hits=[...new Set(hits)].sort((x,y)=>x-y);let ranges=[];for(const v of hits){if(ranges.length&&v-7<=ranges.at(-1)[1]+3)ranges.at(-1)[1]=v+7;else ranges.push([v-7,v+7]);bridgeCount++;}
   if(dir<0)ranges.reverse();
   for(const r of ranges){const u=dir>0?r[0]:r[1],v=dir>0?r[1]:r[0];if(hor)ds+=` L${u} ${fixed} C${u} ${fixed-10} ${v} ${fixed-10} ${v} ${fixed}`;else ds+=` L${fixed} ${u} C${fixed+10} ${u} ${fixed+10} ${v} ${fixed} ${v}`;}
   ds+=' L'+b.join(' ');
  }
  s+=`<path d="${ds}" fill="none" stroke="white" stroke-width="9"/><path d="${ds}" fill="none" stroke="${p.color}" stroke-width="2.2"/>`;
  for(let k=1;k<p.poly.length;k++)priorSegments.push([p.poly[k-1],p.poly[k]]);
 }

 for(const [name,b]of Object.entries(pos)){
  s+=`<rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" fill="white" stroke="#4b94b7" stroke-width="2"/><rect x="${b.x}" y="${b.y}" width="${b.w}" height="49" fill="#fff3c4" stroke="#4b94b7" stroke-width="1"/>`+text(b.x+14,b.y+34,name,28,'start',true);
  b.fields.forEach((c,i)=>{const fk=schema.foreign_keys.some(f=>f.source_table===name&&f.source_column===c.name);s+=text(b.x+13,b.y+55+i*32+23,`${c.is_pk?'PK':fk?'FK':'   '}  ${c.name}${c.is_nullable?' ?':''}`,23);});
 }
 const labelRects=[];
 for(const p of paths){const last=p.poly.at(-1),prev=p.poly.at(-2),dir=last[0]>prev[0]?1:-1;s+=`<path d="M${last[0]-dir*10} ${last[1]-5}L${last[0]} ${last[1]}L${last[0]-dir*10} ${last[1]+5}" fill="none" stroke="${p.color}" stroke-width="2.3"/>`;
 const label='R'+String(p.i+1).padStart(2,'0');let choices=[];for(let k=1;k<p.poly.length;k++){const a=p.poly[k-1],b=p.poly[k],len=Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]);choices.push({a,b,len,score:len+(a[0]===b[0]&&len>200?5000:0)});}choices.sort((a,b)=>b.score-a.score);let spot;for(const q of choices){const vertical=q.a[0]===q.b[0];for(const f of [.5,.32,.68,.2,.8,.1,.9]){let mx=q.a[0]+(q.b[0]-q.a[0])*f,my=q.a[1]+(q.b[1]-q.a[1])*f,w=vertical?18:48,h=vertical?48:18,rect={x:mx-w/2,y:my-h/2,w,h};if(q.len>70&&!labelRects.some(r=>rect.x<r.x+r.w+6&&rect.x+rect.w+6>r.x&&rect.y<r.y+r.h+6&&rect.y+rect.h+6>r.y)){spot={mx,my,rotate:vertical?-90:0,rect};break;}}if(spot)break;}if(!spot)throw Error('No room for label');labelRects.push(spot.rect);const {mx,my,rotate}=spot;
 s+=`<g transform="translate(${mx} ${my}) rotate(${rotate})"><rect x="-24" y="-9" width="48" height="18" fill="white"/>${text(0,6,label,16,'middle',true)}</g>`;

 }
 s+=text(125,H-109,'PK: khóa chính · FK: khóa ngoại vật lý · ?: cho phép NULL. Mũi tên đi từ khóa được tham chiếu tới khóa ngoại.',24);
 s+=text(125,H-67,'Mã R phân biệt các ràng buộc khóa ngoại. Cầu vượt tại chỗ giao cắt: hai đường không liên kết với nhau. Các quan hệ không dùng chung đoạn nối.',23);
 s+=text(125,H-28,'Registrations có cả FK ClassId và FK ghép (ClassId, ProgramId) tới Classes; DesiredTeacherId là cột cũ, không có FK vật lý.',22);
 await save('So_do_co_so_du_lieu_ro_duong',s+'</svg>',5250);
 const audit={tables:16,columns:schema.columns.length,relations:fks.length,shared_grid_edges:0,bridges:bridgeCount,paths:paths.map(p=>({id:'R'+String(p.i+1).padStart(2,'0'),fk:p.parts.map(f=>f.source_table+'.'+f.source_column+' → '+f.target_table+'.'+f.target_column),points:p.poly}))};fs.writeFileSync(path.join(OUT,'routing-audit.json'),JSON.stringify(audit,null,2));
 console.log('ERD grid',nx,ny,'relationships',paths.length);
}
(async()=>{await usecase();console.log('Updated authentication use cases');})();
