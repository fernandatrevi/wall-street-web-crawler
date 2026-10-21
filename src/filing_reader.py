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
.passage.current{background:#eaf3ff}
.passage .category{font:700 11px Arial,sans-serif;letter-spacing:.02em;margin-bottom:4px}
mark{color:#121212;border-radius:1px;padding:0 1px}
.overlay{position:absolute;inset:0;pointer-events:none;overflow:visible;z-index:2}
.overlay path{fill:none;stroke-width:2.2;opacity:.78}
.spider{position:absolute;z-index:3;pointer-events:none;width:180px;height:180px;overflow:visible;filter:drop-shadow(0 2px 3px #ff3b7c55);transform:translate(-50%,-50%)}
.spider .leg{fill:none;stroke:#ff477e;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.spider .joint{fill:#ffe066;stroke:none}
.spider .body{fill:#17202d;stroke:#ff477e;stroke-width:1.6}
.status{background:#121c2b;color:#cbd5e1;padding:10px 16px;font-size:12px}
@media(max-width:550px){.paper{padding:26px 20px}.toolbar{font-size:11px}.passage{font-size:11px}}
</style></head><body>
<div class="toolbar"><div><strong>🕷️ Wall Street Document Crawler</strong><br><small id="counter">Ready to analyze</small></div>
<div><button id="play">Pause</button> <button id="restart">Restart</button></div></div>
<div class="viewport" id="viewport"><article class="paper" id="paper">
<div class="heading">FINANCIAL FILING · DOCUMENT SCAN</div>
<div class="subheading">Extracted SEC filing passages · highlights appear as the spider visits each finding</div>
<div id="passages"></div><svg class="overlay" id="lines" aria-hidden="true"></svg><svg class="spider" id="spider" viewBox="-90 -90 180 180" aria-label="Animated eight-legged spider">
<g id="legs"></g><ellipse class="body" rx="8" ry="12"/><circle cx="-3" cy="-5" r="1.8" fill="#ffe066"/><circle cx="3" cy="-5" r="1.8" fill="#ffe066"/></svg>
</article></div><div class="status" id="status">Scanning the report for financial topics</div>
<script>
const records=__DATA__;
const palette={"Revenue":"#43e6a2","Competition":"#ff68ba","Debt & financing":"#ffc15c",
"Research & development":"#ad89ff","Risk":"#ff8282","Shares":"#76c9ff"};
const paper=document.getElementById("paper"),container=document.getElementById("passages");
const viewport=document.getElementById("viewport"),spider=document.getElementById("spider");
const svg=document.getElementById("lines"),counter=document.getElementById("counter");
const status=document.getElementById("status"),play=document.getElementById("play");
const entries=[];
records.forEach((r,i)=>{
 const p=document.createElement("section");p.className="passage";p.id="passage-"+i;
 const label=document.createElement("div");label.className="category";
 label.textContent=r.category.toUpperCase()+"  ·  PASSAGE "+r.passage;label.style.color="#64748b";
 const body=document.createElement("div");body.textContent=r.text;
 p.append(label,body);container.appendChild(p);entries.push({p,body,label});
});
const ns="http://www.w3.org/2000/svg";
const previous={};let position=0,playing=true;
const legGroup=document.getElementById("legs");
const legs=[];
for(let side of [-1,1])for(let i=0;i<4;i++){
 const path=document.createElementNS(ns,"polyline");path.setAttribute("class","leg");legGroup.appendChild(path);
 const joint=document.createElementNS(ns,"circle");joint.setAttribute("class","joint");joint.setAttribute("r","2.5");legGroup.appendChild(joint);
 const foot=document.createElementNS(ns,"circle");foot.setAttribute("class","joint");foot.setAttribute("r","2");legGroup.appendChild(foot);
 legs.push({side,i,path,joint,foot});
}
let spiderX=100,spiderY=180,fromX=100,fromY=180,toX=100,toY=180,moveStart=performance.now(),moveDuration=1100;
function animateSpider(now){
 const t=Math.min(1,(now-moveStart)/moveDuration),ease=t*t*(3-2*t);
 spiderX=fromX+(toX-fromX)*ease;spiderY=fromY+(toY-fromY)*ease;
 spider.style.left=spiderX+"px";spider.style.top=spiderY+"px";
 const moving=playing&&t<1;
 for(const leg of legs){
  const {side,i,path,joint,foot}=leg;
  const spread=[-1.05,-.38,.38,1.05][i];
  const phase=now/125+i*Math.PI*.8+(side===1?Math.PI:0);
  const step=moving?Math.sin(phase)*12:Math.sin(phase)*1.4;
  const lift=moving?Math.max(0,Math.cos(phase))*11:0;
  const hipX=side*6,hipY=(i-1.5)*5;
  const kneeX=side*(35+Math.cos(spread)*12),kneeY=spread*34+step*.35;
  const footX=side*(68+Math.cos(spread)*8)+step,footY=spread*55+step*.6-lift;
  path.setAttribute("points",hipX+","+hipY+" "+kneeX+","+kneeY+" "+footX+","+footY);
  joint.setAttribute("cx",kneeX);joint.setAttribute("cy",kneeY);
  foot.setAttribute("cx",footX);foot.setAttribute("cy",footY);
 }
 requestAnimationFrame(animateSpider);
}
requestAnimationFrame(animateSpider);
function termsOf(r){return r.keywords.split(",").map(s=>s.trim()).filter(Boolean).sort((a,b)=>b.length-a.length)}
function highlight(r,body){
 const terms=termsOf(r),text=r.text;
 if(!terms.length)return null;
 const lower=text.toLowerCase(),ranges=[];
 for(const term of terms){let from=0,idx;while((idx=lower.indexOf(term.toLowerCase(),from))!==-1){
  ranges.push([idx,idx+term.length]);from=idx+term.length;if(ranges.length>70)break;
 }}
 ranges.sort((a,b)=>a[0]-b[0]);body.replaceChildren();let end=0,first=null;
 for(const [a,b] of ranges){if(a<end)continue;
  body.appendChild(document.createTextNode(text.slice(end,a)));
  const mark=document.createElement("mark");mark.textContent=text.slice(a,b);
  mark.style.background=palette[r.category]||"#a5b4fc";body.appendChild(mark);
  if(!first)first=mark;end=b;
 }
 body.appendChild(document.createTextNode(text.slice(end)));return first;
}
function point(el){const a=el.getBoundingClientRect(),b=paper.getBoundingClientRect();
 return {x:a.left-b.left+a.width/2,y:a.top-b.top+a.height/2};}
function connect(a,b,color){
 const p=point(a),q=point(b),dx=q.x-p.x,dy=q.y-p.y;
 const curve=document.createElementNS(ns,"path");
 curve.setAttribute("d","M"+p.x+" "+p.y+" Q"+(p.x+q.x)/2+" "+(Math.min(p.y,q.y)-Math.min(55,Math.abs(dy)*.25)-18)+" "+q.x+" "+q.y);
 curve.setAttribute("stroke",color);svg.appendChild(curve);
}
function tick(){
 if(!playing||!records.length)return;
 if(position>=records.length){playing=false;play.textContent="Replay";counter.textContent="Complete · "+records.length+" findings";return;}
 const r=records[position],e=entries[position];
 if(position)entries[position-1].p.classList.remove("current");
 e.p.classList.add("current");e.label.style.color="#334155";
 const mark=highlight(r,e.body);
 const target=mark||e.p;
 if(mark&&previous[r.category])connect(previous[r.category],mark,palette[r.category]||"#60a5fa");
 if(mark)previous[r.category]=mark;
 const pt=point(target);
 fromX=spiderX;fromY=spiderY;
 toX=Math.max(70,Math.min(pt.x+28,paper.clientWidth-70));
 toY=pt.y-18;moveStart=performance.now();
 viewport.scrollTo({top:Math.max(0,e.p.offsetTop-viewport.clientHeight/3),behavior:"smooth"});
 counter.textContent="Found "+(position+1)+" / "+records.length+" matches";
 status.textContent=r.category+" · Passage "+r.passage+" · "+r.keywords;
 position++;
}
function reset(){
 position=0;playing=true;play.textContent="Pause";svg.replaceChildren();
 Object.keys(previous).forEach(k=>delete previous[k]);
 entries.forEach((e,i)=>{e.body.textContent=records[i].text;e.p.classList.remove("current");e.label.style.color="#64748b"});
 viewport.scrollTo({top:0,behavior:"instant"});fromX=spiderX;fromY=spiderY;tick();
}
play.onclick=()=>{if(position>=records.length)reset();else{playing=!playing;play.textContent=playing?"Pause":"Play";}};
document.getElementById("restart").onclick=reset;
if(records.length){tick();setInterval(tick,1200);}else{counter.textContent="No matches";play.disabled=true;}
</script></body></html>"""
    components.html(template.replace("__DATA__", payload), height=height, scrolling=False)
