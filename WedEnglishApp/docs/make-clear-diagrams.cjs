const fs=require('fs'),path=require('path'),sharp=require('sharp'),{instance}=require('@viz-js/viz');
const R=path.resolve('docs/diagrams-clear');fs.mkdirSync(R,{recursive:true});
const schema=JSON.parse(fs.readFileSync('session-state/report-live-schema.json','utf8'));
const groups=Object.values(Object.groupBy(schema.foreign_keys,x=>x.name));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
(async()=>{
 const viz=await instance();let s='digraph G { graph [rankdir=LR, splines=ortho, nodesep=1.0, ranksep=1.5, pad=0.5, bgcolor="white", outputorder=edgesfirst]; node [shape=plain, fontname="Arial"]; edge [color="#347ca5",penwidth=1.5,arrowsize=0.7];\n';
 for(const name of [...new Set(schema.columns.map(x=>x.table))]){
  let rows=schema.columns.filter(x=>x.table===name).map(c=>`<TR><TD ALIGN="LEFT" PORT="${c.name}"><FONT POINT-SIZE="14">${c.is_pk?'PK':schema.foreign_keys.some(f=>f.source_table===name&&f.source_column===c.name)?'FK':'  '}  ${c.name}${c.is_nullable?' ?':''}</FONT></TD></TR>`).join('');
  s+=`"${name}" [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" COLOR="#4b94b7"><TR><TD BGCOLOR="#fff3c4" ALIGN="LEFT"><FONT POINT-SIZE="18"><B>${name}</B></FONT></TD></TR>${rows}</TABLE>>];\n`;
 }
 groups.forEach((f,i)=>s+=`"${f[0].target_table}" -> "${f[0].source_table}" [id="r${i+1}"];\n`);
 s+='}';fs.writeFileSync(path.join(R,'erd-layout.dot'),s);const svg=viz.renderString(s,{format:'svg'});fs.writeFileSync(path.join(R,'erd-test.svg'),svg);await sharp(Buffer.from(svg),{density:90}).png().toFile(path.join(R,'erd-test.png'));console.log(R);
})();
