let lang='tr', selected=1;const $=s=>document.querySelector(s);const t=(tr,en)=>lang==='tr'?tr:en;const coefficients={AA:4,BA:3.5,BB:3,CB:2.5,CC:2,DC:1.5,DD:1,FD:.5,FF:0};
function normalize(s){return s.toLocaleLowerCase(lang==='tr'?'tr-TR':'en-US')}
function showGuide(){const query=normalize($('#guide-search').value);const list=$('#guide-topics');list.replaceChildren();let matches=GUIDE.filter(s=>normalize(s[lang]).includes(query));for(const s of matches){const b=document.createElement('button');b.className='topic'+(s.id===selected?' active':'');b.textContent=s[lang].split('\n')[0];b.onclick=()=>{selected=s.id;showGuide()};list.append(b)}if(!matches.length){const p=document.createElement('p');p.textContent=t('Konu bulunamadı.','No matching topics.');list.append(p)}const s=GUIDE.find(s=>s.id===selected);const [heading,...body]=s[lang].split('\n');$('#guide-title').textContent=heading;$('#guide-body').textContent=body.join('\n')}
function showCourses(){const q=$('#course-search').value.toLowerCase().trim();const rows=$('#course-rows');rows.replaceChildren();const matches=COURSES.filter(c=>[c.ders_kodu,c.ders_adi,c.ders_adi_en].some(x=>x.toLowerCase().includes(q)));for(const c of matches){const row=document.createElement('tr');for(const v of [c.ders_kodu,lang==='tr'?c.ders_adi:c.ders_adi_en,c.akts,(lang==='tr'?c.gun:c.gun_en)+' '+c.saat,c.derslik]){const td=document.createElement('td');td.textContent=v;row.append(td)}rows.append(row)}if(!matches.length){const row=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent=t('Ders bulunamadı.','No courses found.');row.append(td);rows.append(row)}}
function clearResult(){$('#gpa-value').textContent='—';$('#gpa-total').textContent='';$('#gpa-error').textContent=''}
function addGrade(grade='AA',credits=6){const row=document.createElement('div');row.className='grade-row';const select=document.createElement('select');select.setAttribute('aria-label',t('Harf notu','Letter grade'));for(const [g,c] of Object.entries(coefficients)){const op=document.createElement('option');op.value=g;op.textContent=g+' · '+c.toFixed(2);select.append(op)}select.value=grade;const input=document.createElement('input');input.type='number';input.min='0.01';input.step='any';input.value=credits;input.setAttribute('aria-label','ECTS / AKTS');const remove=document.createElement('button');remove.textContent='×';remove.setAttribute('aria-label',t('Dersi kaldır','Remove course'));remove.onclick=()=>{row.remove();clearResult()};select.onchange=input.oninput=clearResult;row.append(select,input,remove);$('#grade-rows').append(row);clearResult()}
function calculate(){let weighted=0,total=0;const rows=[...document.querySelectorAll('.grade-row')];for(const row of rows){const credits=Number(row.querySelector('input').value);const grade=row.querySelector('select').value;if(!Number.isFinite(credits)||credits<=0||!(grade in coefficients)){$('#gpa-error').textContent=t('Her ders için pozitif bir AKTS değeri gir.','Enter positive ECTS values for every course.');$('#gpa-value').textContent='—';$('#gpa-total').textContent='';return}total+=credits;weighted+=credits*coefficients[grade]}if(!rows.length||!Number.isFinite(total)||!Number.isFinite(weighted)){$('#gpa-error').textContent=t('En az bir geçerli ders ekle.','Add at least one valid course.');return}$('#gpa-error').textContent='';$('#gpa-value').textContent=(weighted/total).toFixed(2);$('#gpa-total').textContent=t('Toplam AKTS: ','Total ECTS: ')+total}
function renderMetrics(){const metrics=[['Türkçe · RAG','Turkish · RAG',.50,.47],['İngilizce · RAG','English · RAG',.60,1.00],['Türkçe · doğru araç','Turkish · correct tool',0,.67],['İngilizce · doğru araç','English · correct tool',0,.60]];$('#metrics').replaceChildren();for(const [tr,en,before,after] of metrics){const d=document.createElement('div');d.className='metric';const label=document.createElement('div');label.className='metric-label';const name=document.createElement('span');name.textContent=t(tr,en);const values=document.createElement('span');values.textContent=before.toFixed(2)+' → '+after.toFixed(2);label.append(name,values);d.append(label);for(const [value,cls] of [[before,'bar'],[after,'bar after']]){const bar=document.createElement('div');bar.className=cls;const fill=document.createElement('i');fill.style.width=(value*100)+'%';bar.append(fill);d.append(bar)}$('#metrics').append(d)}}
function renderLanguage(){document.documentElement.lang=lang;document.querySelectorAll('[data-tr]').forEach(el=>{if(el.dataset[lang].includes('<'))el.innerHTML=el.dataset[lang];else el.textContent=el.dataset[lang]});$('#language').textContent=lang==='tr'?'EN ↗':'TR ↗';$('#portal-query').placeholder=t('Rehberde ara…','Search the guide…');$('#guide-search').placeholder=t('Burs, sınav, yaz okulu…','Scholarships, exams, summer school…');$('#course-search').placeholder=t('BIL412 / Derin Öğrenme','BIL412 / Deep Learning');showGuide();showCourses();renderMetrics();document.querySelectorAll('.grade-row').forEach(row=>{row.querySelector('select').setAttribute('aria-label',t('Harf notu','Letter grade'));row.querySelector('button').setAttribute('aria-label',t('Dersi kaldır','Remove course'))});if($('#gpa-value').textContent!=='—')calculate()}
$('#language').onclick=()=>{lang=lang==='tr'?'en':'tr';$('#guide-search').value='';renderLanguage()};$('#guide-search').oninput=showGuide;$('#course-search').oninput=showCourses;$('#add-grade').onclick=()=>addGrade();$('#calculate').onclick=calculate;document.querySelectorAll('[data-panel]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-panel]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-selected',x===b?'true':'false')});document.querySelectorAll('.panel').forEach(x=>x.hidden=x.id!==b.dataset.panel)});addGrade('AA',6);addGrade('BB',4);renderLanguage();

// University portal navigation uses the same working student hub.
function openPanel(name){const tab=document.querySelector('[data-panel="'+name+'"]');if(tab)tab.click()}
document.querySelectorAll('[data-open]').forEach(link=>link.addEventListener('click',()=>openPanel(link.dataset.open)));
document.querySelectorAll('[data-topic]').forEach(link=>link.addEventListener('click',()=>{selected=Number(link.dataset.topic);$('#guide-search').value='';openPanel('guide');showGuide()}));
$('#portal-search').addEventListener('submit',event=>{event.preventDefault();const query=$('#portal-query').value.trim();openPanel('guide');$('#guide-search').value=query;const match=GUIDE.find(s=>normalize(s[lang]).includes(normalize(query)));if(match)selected=match.id;showGuide();$('#explore').scrollIntoView({behavior:'smooth'});$('#guide-search').focus({preventScroll:true})});
const tabButtons=[...document.querySelectorAll('[data-panel]')];tabButtons.forEach((tab,i)=>{tab.id='tab-'+tab.dataset.panel;tab.setAttribute('aria-controls',tab.dataset.panel);document.getElementById(tab.dataset.panel).setAttribute('aria-labelledby',tab.id);tab.addEventListener('keydown',event=>{let target;if(event.key==='ArrowRight')target=tabButtons[(i+1)%tabButtons.length];if(event.key==='ArrowLeft')target=tabButtons[(i+tabButtons.length-1)%tabButtons.length];if(target){event.preventDefault();target.click();target.focus()}})});

// Embedded real Gradio model, with an external fallback and native dialog focus handling.
const promDialog = document.getElementById('prom-chat');
const promFrameArea = document.getElementById('prom-frame-area');
let promOpener = null;
function promDemoUrl(){
  try {
    const url = new URL(window.PROM_DEMO?.url || '');
    if(url.protocol !== 'https:' || url.username || url.password ||
       !(/^[-a-z0-9]+\.gradio\.live$/.test(url.hostname) || /^[-a-z0-9]+\.hf\.space$/.test(url.hostname))) return null;
    return url.href;
  } catch { return null; }
}
function mountPromDemo(){
  const url = promDemoUrl();
  promFrameArea.replaceChildren();
  const external = document.getElementById('prom-demo-external');
  external.hidden = !url;
  document.getElementById('prom-demo-retry').disabled = !url;
  if(!url){
    const note=document.createElement('p');note.className='prom-no-demo';
    note.textContent=t('Demo bağlantısı henüz ayarlanmadı. Rehber ve hesaplayıcıyı kullanabilirsin.','The demo is not configured yet. You can use the guide and calculator.');
    promFrameArea.append(note);return;
  }
  external.href=url;
  const frame=document.createElement('iframe');
  frame.src=url;frame.title='Prom — model demo / model demosu';
  frame.referrerPolicy='strict-origin-when-cross-origin';
  promFrameArea.append(frame);
}
document.querySelectorAll('[data-prom-open]').forEach(button=>button.addEventListener('click',event=>{
  event.preventDefault();promOpener=button;
  if(!promFrameArea.firstChild)mountPromDemo();
  if(!promDialog.open)promDialog.showModal();
  document.getElementById('prom-chat-close').focus();
}));
document.getElementById('prom-chat-close').addEventListener('click',()=>promDialog.close());
document.getElementById('prom-demo-retry').addEventListener('click',mountPromDemo);
promDialog.addEventListener('click',event=>{if(event.target===promDialog)promDialog.close()});
promDialog.addEventListener('close',()=>promOpener?.focus());
