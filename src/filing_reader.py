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
.viewport{height:635px;overflow:auto;position:relative;scroll-behavior:auto}
.paper{position:relative;width:min(780px,calc(100% - 32px));margin:20px auto 32px;padding:42px 52px 60px;background:white;min-height:940px;box-shadow:0 2px 15px #a9b1bd75}
.heading{font-size:19px;text-align:center;font-weight:bold;margin:0 0 8px}
.subheading{text-align:center;font-size:11px;color:#64748b;margin-bottom:30px}
.passage{position:relative;font-family:Georgia,'Times New Roman',serif;font-size:12.5px;line-height:1.75;margin:0 0 14px;transition:background .3s}
.passage.current{background:transparent}
.passage .category{font:700 11px Arial,sans-serif;letter-spacing:.02em;margin-bottom:4px}
mark{color:inherit;background:transparent;border-radius:1px;padding:0 1px;transition:background .25s,box-shadow .25s}mark.found{background:var(--topic);box-shadow:0 0 0 1px var(--topic)}
.overlay{position:absolute;inset:0;pointer-events:none;overflow:visible;z-index:2}
.overlay path{fill:none;stroke-width:1;opacity:.18}
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
<div id="passages"></div><svg class="overlay" id="lines" aria-hidden="true"></svg><svg class="spider" id="spider" aria-label="Eight articulated spider legs point at financial terms"><g id="legs"></g><g id="spiderBody"><rect class="body" x="-12" y="-15" width="24" height="30" rx="1.5"/><rect x="-7" y="6" width="14" height="8" fill="#ff4a9e"/><circle cx="0" cy="11" r="3" fill="#ff9ccd"/></g></svg>
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
// Prepare findings once. Visit a few representative keywords per passage.
const prepared=records.map((r,i)=>({marks:prepare(i),category:r.category}));
const findings=prepared.flatMap((p,i)=>{
 const marks=p.marks;
 if(!marks.length)return [];
 const picks=[marks[0],marks[Math.floor((marks.length-1)/2)],marks[marks.length-1]];
 return [...new Set(picks)].map(mark=>({mark,category:p.category,passage:i}));
});
let center={x:paper.clientWidth/2,y:180},position=0,playing=true,last=performance.now(),linked={};
const FOOT_MS=280,BODY_MS=280,REST_MS=65,MAX_HOP=95;
let phase="body",elapsed=0,activeLeg=0,from={...center},to={...center},target=null,footStart=null,footEnd=null,bodyDuration=BODY_MS,finalDestination=null;
const order=[0,4,1,5,2,6,3,7];
function baseFoot(leg,origin=center){
 const angle=[-1.15,-.4,.4,1.15][leg.i];
 return {x:origin.x+leg.side*(140+Math.cos(angle)*35),y:origin.y+angle*120};
}
function distance(a,b){return Math.hypot(a.x-b.x,a.y-b.y)}
function nextHop(){
 const remaining=distance(center,finalDestination);
 const ratio=Math.min(1,MAX_HOP/Math.max(1,remaining));
 from={...center};
 to={x:center.x+(finalDestination.x-center.x)*ratio,y:center.y+(finalDestination.y-center.y)*ratio};
 bodyDuration=BODY_MS;phase="body";elapsed=0;
}
function assign(i){
 if(i>=findings.length){playing=false;play.textContent="Replay";counter.textContent="Complete · "+findings.length+" findings";return;}
 target=findings[i];
 const dest=point(target.mark);
 // Approach the finding in short visible steps, rather than one giant leap.
 finalDestination={x:Math.max(110,Math.min(paper.clientWidth-110,dest.x)),y:dest.y+48};
 activeLeg=order[i%order.length];
 footEnd={...dest};
 nextHop();
 counter.textContent="Finding "+(i+1)+" / "+findings.length;
 status.textContent=target.category+" · "+target.mark.textContent;
}
function connect(mark,category){linked[category]=mark;}
function reveal(mark,category){
 if(mark.classList.contains("found"))return;
 mark.classList.add("found");connect(mark,category);
}
function frame(now){
 const delta=Math.min(45,now-last);last=now;
 if(playing&&findings.length)elapsed+=delta;
 const smooth=t=>t*t*(3-2*t);
 if(phase==="body"){
  const t=smooth(Math.min(1,elapsed/bodyDuration));
  center={x:from.x+(to.x-from.x)*t,y:from.y+(to.y-from.y)*t};
  if(playing&&elapsed>=bodyDuration){
   if(distance(center,finalDestination)>2)nextHop();
   else{phase="foot";elapsed=0;footStart=baseFoot(legs[activeLeg]);}
  }
 }
 body.setAttribute("transform","translate("+center.x+" "+center.y+")");
 // Camera follows smoothly without jumping ahead of the spider.
 if(playing){
  const wanted=Math.max(0,Math.min(viewport.scrollHeight-viewport.clientHeight,
    center.y+paper.offsetTop-viewport.clientHeight*.48));
  // Synchronize the camera with the spider every frame.
  viewport.scrollTop=wanted;
 }
 legs.forEach((leg,n)=>{
  const hip={x:center.x+leg.side*12,y:center.y+(leg.i-1.5)*8};
  let foot=baseFoot(leg);
  if(n===activeLeg&&target){
   if(phase==="foot"){
    const t=Math.min(1,elapsed/FOOT_MS),s=smooth(t);
    foot={x:footStart.x+(footEnd.x-footStart.x)*s,
          y:footStart.y+(footEnd.y-footStart.y)*s-Math.sin(Math.PI*t)*25};
   }
  }
  const dx=foot.x-hip.x,dy=foot.y-hip.y;
  const knee={x:hip.x+dx*.48+leg.side*48,y:hip.y+dy*.48-24};
  leg.path.setAttribute("points",hip.x+","+hip.y+" "+knee.x+","+knee.y+" "+foot.x+","+foot.y);
  leg.joint.setAttribute("cx",knee.x);leg.joint.setAttribute("cy",knee.y);
  leg.foot.setAttribute("cx",foot.x);leg.foot.setAttribute("cy",foot.y);
 });
 if(playing&&phase==="foot"&&elapsed>=FOOT_MS){
  reveal(target.mark,target.category);
  phase="rest";elapsed=0;
 }
 if(playing&&phase==="rest"&&elapsed>=REST_MS){position++;assign(position);}
 requestAnimationFrame(frame);
}
function reset(){
 position=0;playing=true;play.textContent="Pause";lines.replaceChildren();linked={};
 prepared.forEach(p=>p.marks.forEach(m=>m.classList.remove("found")));
 center={x:paper.clientWidth/2,y:180};from={...center};to={...center};
 viewport.scrollTop=0;
 if(findings.length)assign(0);
}
play.onclick=()=>{if(position>=findings.length)reset();else{playing=!playing;play.textContent=playing?"Pause":"Play";}};
document.getElementById("restart").onclick=reset;
if(findings.length)reset();else{counter.textContent="No matches";play.disabled=true;}
requestAnimationFrame(frame);
</script></body></html>"""
    components.html(template.replace("__DATA__", payload), height=height, scrolling=False)
