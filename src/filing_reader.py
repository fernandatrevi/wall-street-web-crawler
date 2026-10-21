"""White-page filing reader with animated topic links and a crawling spider.

Reconstructs readable filing text, not the exact SEC HTML/PDF page layout.
"""
import json
import streamlit.components.v1 as components


def show_filing_reader(results: list[dict], height: int = 760) -> None:
    data = [
        {"category": str(row["category"]), "passage": int(row["passage"]),
         "keywords": str(row["keywords"]), "text": str(row["text"])[:1300]}
        for row in results[:100]
    ]
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<style>
*{box-sizing:border-box}
body{margin:0;background:#e9edf2;color:#162032;font-family:Arial,Helvetica,sans-serif}
.toolbar{height:57px;background:#121c2b;color:#f8fafc;display:flex;align-items:center;justify-content:space-between;padding:8px 18px;gap:10px}
.toolbar small{color:#9caec6}button{background:#304866;border:1px solid #56718e;color:white;padding:8px 12px;border-radius:7px;cursor:pointer}
.viewport{height:635px;overflow:auto;position:relative;scroll-behavior:smooth}
.paper{position:relative;width:min(780px,calc(100% - 32px));margin:20px auto 32px;padding:42px 52px 60px;background:white;min-height:940px;box-shadow:0 2px 15px #a9b1bd75}
.heading{font-size:19px;text-align:center;font-weight:bold;margin:0 0 8px}
.subheading{text-align:center;font-size:11px;color:#64748b;margin-bottom:30px}
.passage{position:relative;font-family:Georgia,'Times New Roman',serif;font-size:12.5px;line-height:1.75;margin:0 0 14px;transition:background .3s}
.passage.current{background:transparent}
.passage .category{font:700 11px Arial,sans-serif;letter-spacing:.02em;margin-bottom:4px}
mark{color:inherit;background:transparent;border-radius:1px;padding:0 1px;transition:background .25s,box-shadow .25s}mark.found{background:var(--topic);box-shadow:0 0 0 1px var(--topic)}
.overlay{position:absolute;inset:0;pointer-events:none;overflow:visible;z-index:2}
.overlay path{fill:none;stroke-width:2.2;opacity:.78}
.spider{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:3}
.spider .leg{fill:none;stroke:#f02f76;stroke-width:2.1;stroke-linejoin:round;stroke-linecap:round}
.spider .joint{fill:#ffe45e;stroke:#f02f76;stroke-width:.7}
.spider .body{fill:#161d2b;stroke:#ff3b7c;stroke-width:2}
.status{background:#121c2b;color:#cbd5e1;padding:10px 16px;font-size:12px}
@media(max-width:550px){.paper{padding:26px 20px}.toolbar{font-size:11px}.passage{font-size:11px}}
</style></head><body>
<div class="toolbar"><div><strong>🕷️ Wall Street Document Crawler</strong><br><small id="counter">Ready to analyze</small></div>
<div><button id="play">Pause</button> <button id="restart">Restart</button></div></div>
<div class="viewport" id="viewport"><article class="paper" id="paper">
<div class="heading">FINANCIAL FILING · DOCUMENT SCAN</div>
<div class="subheading">Extracted SEC filing passages · highlights appear as the spider visits each finding</div>
<div id="passages"></div><svg class="overlay" id="lines" aria-hidden="true"></svg><svg class="spider" id="spider" aria-label="Eight articulated spider legs point at financial terms"><g id="legs"></g><g id="spiderBody"><ellipse class="body" rx="8" ry="12"/><circle cx="-3" cy="-5" r="1.8" fill="#ffe066"/><circle cx="3" cy="-5" r="1.8" fill="#ffe066"/></g></svg>
</article></div><div class="status" id="status">Scanning the report for financial topics</div>
<script>
const records=__DATA__;
const palette={"Revenue":"#43e6a2","Competition":"#ff68ba","Debt & financing":"#ffc15c","Research & development":"#ad89ff","Risk":"#ff8282","Shares":"#76c9ff"};
const paper=document.getElementById("paper"),container=document.getElementById("passages");
const viewport=document.getElementById("viewport"),spider=document.getElementById("spider");
const lines=document.getElementById("lines"),counter=document.getElementById("counter");
const status=document.getElementById("status"),play=document.getElementById("play");
const ns="http://www.w3.org/2000/svg",legsGroup=document.getElementById("legs");
const body=document.getElementById("spiderBody");
const entries=[],allMarks=[];
records.forEach((r,i)=>{
 const p=document.createElement("section");p.className="passage";
 const label=document.createElement("div");label.className="category";
 label.textContent=r.category.toUpperCase()+" · PASSAGE "+r.passage;label.style.color="#64748b";
 const div=document.createElement("div");div.textContent=r.text;
 p.append(label,div);container.appendChild(p);entries.push({p,div,label,marks:[]});
});
function termsOf(r){return r.keywords.split(",").map(s=>s.trim()).filter(Boolean).sort((a,b)=>b.length-a.length)}
function prepare(i){
 const e=entries[i],r=records[i];if(e.marks.length)return e.marks;
 const text=r.text,lower=text.toLowerCase(),ranges=[];
 for(const term of termsOf(r)){let from=0,at;
  while((at=lower.indexOf(term.toLowerCase(),from))!==-1){ranges.push([at,at+term.length]);from=at+term.length;if(ranges.length>=55)break;}
 }
 ranges.sort((a,b)=>a[0]-b[0]);e.div.replaceChildren();let end=0;
 for(const [a,b] of ranges){if(a<end)continue;
  e.div.appendChild(document.createTextNode(text.slice(end,a)));
  const mark=document.createElement("mark");mark.textContent=text.slice(a,b);
  mark.style.setProperty("--topic",palette[r.category]||"#ff68ba");
  e.div.appendChild(mark);e.marks.push(mark);end=b;
 }
 e.div.appendChild(document.createTextNode(text.slice(end)));return e.marks;
}
function point(el){
 const a=el.getBoundingClientRect(),b=paper.getBoundingClientRect();
 return {x:a.left-b.left+a.width/2,y:a.top-b.top+a.height/2};
}
function make(tag,parent,cls){
 const el=document.createElementNS(ns,tag);if(cls)el.setAttribute("class",cls);
 parent.appendChild(el);return el;
}
const legs=[];
for(let side of [-1,1])for(let i=0;i<4;i++){
 const path=make("polyline",legsGroup,"leg"),joint=make("circle",legsGroup,"joint"),foot=make("circle",legsGroup,"joint");
 joint.setAttribute("r","2.5");foot.setAttribute("r","3");
 legs.push({side,i,path,joint,foot,goal:null,contact:false});
}
let center={x:350,y:220},from={...center},to={...center};
let stepStart=performance.now(),duration=2300,position=0,playing=true,elapsed=0,last=performance.now();
let targets=[],linked={};
function assign(i){
 const e=entries[i],marks=prepare(i);
 if(!marks.length)return false;
 e.p.scrollIntoView({block:"center",behavior:"smooth"});
 const locations=marks.map(m=>({mark:m,pt:point(m)}));
 const avg=locations.reduce((a,o)=>({x:a.x+o.pt.x,y:a.y+o.pt.y}),{x:0,y:0});
 avg.x/=locations.length;avg.y/=locations.length;
 from={...center};
 to={x:Math.max(75,Math.min(paper.clientWidth-75,avg.x)),y:avg.y+26};
 // Each leg gets a different word; if there are fewer than 8 words,
 // remaining legs plant around the body rather than converging to one point.
 targets=locations.slice(0,8);
 legs.forEach((leg,n)=>{leg.goal=targets[n]||null;leg.contact=false;});
 counter.textContent="Scanning "+(i+1)+" / "+records.length+" passages";
 status.textContent=records[i].category+" · "+records[i].keywords;
 return true;
}
function connect(mark,category){
 if(linked[category]){
  const a=point(linked[category]),b=point(mark),curve=make("path",lines);
  curve.setAttribute("d","M"+a.x+" "+a.y+" Q"+(a.x+b.x)/2+" "+(Math.min(a.y,b.y)-35)+" "+b.x+" "+b.y);
  curve.setAttribute("stroke",palette[category]||"#ff68ba");
 }
 linked[category]=mark;
}
function reveal(mark,category){
 if(mark.classList.contains("found"))return;
 mark.classList.add("found");connect(mark,category);
}
function frame(now){
 const delta=Math.min(50,now-last);last=now;
 if(playing&&records.length)elapsed+=delta;
 const t=Math.min(1,elapsed/duration),ease=t*t*(3-2*t);
 center.x=from.x+(to.x-from.x)*ease;center.y=from.y+(to.y-from.y)*ease;
 body.setAttribute("transform","translate("+center.x+" "+(center.y+Math.sin(now/130)*2)+")");
 const spread=[-1.2,-.4,.4,1.2];
 legs.forEach((leg,n)=>{
  const {side,i}=leg,angle=spread[i],phase=now/190+i*Math.PI*.75+(side>0?Math.PI:0);
  const hip={x:center.x+side*7,y:center.y+(i-1.5)*5};
  let foot;
  if(leg.goal){
   const p=point(leg.goal.mark);
   const distance=Math.hypot(p.x-hip.x,p.y-hip.y);
   // Reach the actual highlighted term if close; otherwise extend toward it.
   const factor=Math.min(1,200/Math.max(1,distance));
   foot={x:hip.x+(p.x-hip.x)*factor,y:hip.y+(p.y-hip.y)*factor};
   if(t>.55&&!leg.contact&&factor===1){reveal(leg.goal.mark,records[position].category);leg.contact=true;}
  }else{
   foot={x:center.x+side*(110+Math.cos(angle)*20),y:center.y+angle*105};
  }
  const walk=playing&&t<1?Math.sin(phase)*8:0;
  const lift=playing&&t<1?Math.max(0,Math.cos(phase))*7:0;
  if(!leg.contact){foot.x+=walk;foot.y-=lift;}
  const knee={x:hip.x+(foot.x-hip.x)*.58+side*24,y:hip.y+(foot.y-hip.y)*.52-16};
  leg.path.setAttribute("points",hip.x+","+hip.y+" "+knee.x+","+knee.y+" "+foot.x+","+foot.y);
  leg.joint.setAttribute("cx",knee.x);leg.joint.setAttribute("cy",knee.y);
  leg.foot.setAttribute("cx",foot.x);leg.foot.setAttribute("cy",foot.y);
 });
 if(playing&&t>=1&&records.length){
  // Reveal remaining keywords in this passage as the spider completes the scan.
  entries[position].marks.forEach(m=>reveal(m,records[position].category));
  position++;
  if(position>=records.length){playing=false;play.textContent="Replay";counter.textContent="Complete · "+records.length+" passages";}
  else{from={...center};elapsed=0;assign(position);}
 }
 requestAnimationFrame(frame);
}
function reset(){
 position=0;elapsed=0;playing=true;play.textContent="Pause";lines.replaceChildren();linked={};
 entries.forEach((e,i)=>{e.div.textContent=records[i].text;e.marks=[];});
 from={x:paper.clientWidth/2,y:180};center={...from};to={...from};
 viewport.scrollTo({top:0,behavior:"instant"});
 if(records.length)assign(0);
}
play.onclick=()=>{if(position>=records.length)reset();else{playing=!playing;play.textContent=playing?"Pause":"Play";}};
document.getElementById("restart").onclick=reset;
if(records.length)reset();else{counter.textContent="No matches";play.disabled=true;}
requestAnimationFrame(frame);
</script></body></html>"""
    components.html(template.replace("__DATA__", payload), height=height, scrolling=False)
