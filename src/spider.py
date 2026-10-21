"""Animated spider-like crawl visualization for a filing's detected passages."""
import html
import json
import streamlit.components.v1 as components


def show_crawler(results: list[dict], height: int = 420) -> None:
    """Render a self-contained animation; no external services or scripts."""
    data = [
        {"category": str(r["category"]), "passage": int(r["passage"]),
         "keywords": str(r["keywords"])[:100]}
        for r in results[:75]
    ]
    payload = json.dumps(data).replace("<", "\\u003c")
    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
:root{color-scheme:dark}body{margin:0;background:#0c1424;color:#e2e8f0;font:13px system-ui}
header{padding:12px 16px;display:flex;align-items:center;justify-content:space-between;gap:10px}
button{background:#233452;color:#fff;border:1px solid #496080;border-radius:8px;padding:7px 12px;cursor:pointer}
small{color:#94a3b8}svg{display:block;width:100%;height:320px}
.edge{stroke:#334155;stroke-width:1.2}.edge.active{stroke:#60a5fa;stroke-width:2}
.node{fill:#64748b}.node.visited{fill:var(--node-color)}
#spider{transition:transform .45s ease;filter:drop-shadow(0 0 7px #60a5fa)}
#status{padding:0 16px 12px;min-height:18px;color:#cbd5e1}
</style></head><body>
<header><div><strong>🕷️ Filing crawler</strong><br><small id="progress">Ready to scan</small></div>
<div><button id="toggle">Pause</button> <button id="restart">Restart</button></div></header>
<svg viewBox="0 0 760 320" role="img" aria-label="Spider scans connected filing passages">
<g id="edges"></g><g id="nodes"></g>
<g id="spider" transform="translate(380 160)">
<g stroke="#b4c6e5" stroke-width="2.5" stroke-linecap="round">
<path d="M-7 -5L-23 -14L-34 -8 M7 -5L23 -14L34 -8 M-8 1L-25 0L-36 9 M8 1L25 0L36 9 M-7 7L-23 16L-30 25 M7 7L23 16L30 25 M-5 -10L-16 -23L-26 -23 M5 -10L16 -23L26 -23"/></g>
<ellipse rx="13" ry="16" fill="#60a5fa"/><circle cx="-4" cy="-5" r="2.5" fill="#fff"/><circle cx="4" cy="-5" r="2.5" fill="#fff"/>
</g></svg><div id="status" aria-live="polite"></div>
<script>
const records=__DATA__;
const colors={"Revenue":"#34d399","Competition":"#f472b6","Debt & financing":"#fbbf24",
"Research & development":"#a78bfa","Risk":"#fb7185","Shares":"#38bdf8"};
const svgNS="http://www.w3.org/2000/svg";
const edges=document.getElementById("edges"),nodes=document.getElementById("nodes");
const spider=document.getElementById("spider"),progress=document.getElementById("progress");
const status=document.getElementById("status");
const coords=records.map((r,i)=>({x:55+(i%12)*59,y:35+Math.floor(i/12)*44}));
const circles=[],lines=[];
function make(tag,attrs,parent){const el=document.createElementNS(svgNS,tag);
Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));parent.appendChild(el);return el;}
coords.forEach((p,i)=>{
 if(i){lines.push(make("line",{x1:coords[i-1].x,y1:coords[i-1].y,x2:p.x,y2:p.y,class:"edge"},edges));}
 const circle=make("circle",{cx:p.x,cy:p.y,r:6,class:"node"},nodes);
 const tip=make("title",{},circle);tip.textContent=records[i].category+" · passage "+records[i].passage;
 circles.push(circle);
});
let index=0,playing=true,timer=null;
function tick(){
 if(!playing||!records.length)return;
 if(index>=records.length){playing=false;document.getElementById("toggle").textContent="Play";
 progress.textContent="Scan complete · "+records.length+" findings visited";return;}
 const p=coords[index],r=records[index];
 spider.setAttribute("transform",`translate(${p.x} ${p.y})`);
 circles[index].classList.add("visited");
 circles[index].style.setProperty("--node-color",colors[r.category]||"#60a5fa");
 if(index>0)lines[index-1].classList.add("active");
 status.textContent=r.category+" · passage "+r.passage+" · "+r.keywords;
 progress.textContent="Scanning "+(index+1)+" / "+records.length+" findings";
 index++;
}
function start(){clearInterval(timer);timer=setInterval(tick,550);}
document.getElementById("toggle").onclick=()=>{
 playing=!playing;document.getElementById("toggle").textContent=playing?"Pause":"Play";
 if(playing&&index>=records.length){index=0;circles.forEach(c=>c.classList.remove("visited"));lines.forEach(l=>l.classList.remove("active"));}
};
document.getElementById("restart").onclick=()=>{
 index=0;playing=true;circles.forEach(c=>c.classList.remove("visited"));lines.forEach(l=>l.classList.remove("active"));
 document.getElementById("toggle").textContent="Pause";progress.textContent="Restarting";status.textContent="";
};
if(!records.length){progress.textContent="No findings to scan";document.getElementById("toggle").disabled=true;}
else{tick();start();}
</script></body></html>""".replace("__DATA__", payload)
    components.html(page, height=height, scrolling=False)
