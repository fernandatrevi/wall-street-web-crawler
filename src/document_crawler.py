"""Animate a crawler directly over extracted filing passages.

The display reconstructs text from the SEC filing; it does not preserve the
original SEC webpage's layout or page numbers.
"""
import json
import streamlit.components.v1 as components


def show_document_crawler(results: list[dict], height: int = 650) -> None:
    records = [
        {"category": str(r["category"]), "passage": int(r["passage"]),
         "keywords": str(r["keywords"]), "text": str(r["text"])[:1200]}
        for r in results[:120]
    ]
    payload = json.dumps(records, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = r"""<!doctype html><html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e5e7eb;font:14px system-ui}
.toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px;background:#162136;position:sticky;top:0;z-index:4}
button{background:#304766;border:1px solid #59718f;color:white;padding:7px 12px;border-radius:8px;cursor:pointer}
#viewport{height:510px;overflow:auto;padding:22px 35px;scroll-behavior:smooth;position:relative}
.passage{position:relative;line-height:1.75;padding:14px 18px;margin-bottom:14px;border-left:4px solid #334155;background:#121d2e;border-radius:8px;transition:background .3s}
.passage.active{background:#20324d;border-color:#93c5fd;box-shadow:0 0 0 1px #5279b0}
.passage.visited{border-color:var(--topic)}
.meta{font-size:12px;font-weight:650;color:#a7b8ce;margin-bottom:7px}
mark{color:#09101d;background:var(--topic);border-radius:3px;padding:1px 2px}
#spider{position:absolute;z-index:3;pointer-events:none;font-size:31px;filter:drop-shadow(0 0 8px #7dd3fc);transition:top .45s ease,left .45s ease}
#status{font-size:12px;color:#b8c7dc;padding:8px 16px}
</style></head><body>
<div class="toolbar"><div><strong>🕷️ Spider document scan</strong><div id="progress">Ready</div></div>
<div><button id="toggle">Pause</button> <button id="restart">Restart</button></div></div>
<div id="viewport"><div id="spider">🕷️</div><div id="pages"></div></div>
<div id="status">Each stop highlights keywords in a detected passage.</div>
<script>
const records=__DATA__;
const colors={"Revenue":"#34d399","Competition":"#f472b6","Debt & financing":"#fbbf24","Research & development":"#a78bfa","Risk":"#fb7185","Shares":"#38bdf8"};
const viewport=document.getElementById("viewport"),pages=document.getElementById("pages");
const spider=document.getElementById("spider"),progress=document.getElementById("progress");
const status=document.getElementById("status"),toggle=document.getElementById("toggle");
const entries=[];
records.forEach((r,i)=>{
 const card=document.createElement("section");card.className="passage";
 card.style.setProperty("--topic",colors[r.category]||"#93c5fd");
 const meta=document.createElement("div");meta.className="meta";
 meta.textContent="PASSAGE "+r.passage+" · "+r.category;card.appendChild(meta);
 const body=document.createElement("div");body.className="content";body.textContent=r.text;card.appendChild(body);
 pages.appendChild(card);entries.push({card,body});
});
let index=0,playing=true,timer=null;
function escapeRegExp(s){return s.replace(/[^a-zA-Z0-9 ]/g, "\\$&");}
function highlight(r,el){
 const terms=r.keywords.split(",").map(s=>s.trim()).filter(Boolean).sort((a,b)=>b.length-a.length);
 if(!terms.length)return;
 const pattern=new RegExp("("+terms.map(escapeRegExp).join("|")+")","gi");
 const pieces=r.text.split(pattern);el.replaceChildren();
 pieces.forEach(part=>{
  if(terms.some(t=>t.toLowerCase()===part.toLowerCase())){
   const mark=document.createElement("mark");mark.textContent=part;el.appendChild(mark);
  }else el.appendChild(document.createTextNode(part));
 });
}
function scan(){
 if(!playing||!records.length)return;
 if(index>=records.length){playing=false;toggle.textContent="Replay";progress.textContent="Completed "+records.length+" stops";return;}
 const r=records[index],entry=entries[index];
 if(index>0)entries[index-1].card.classList.remove("active");
 entry.card.classList.add("active","visited");highlight(r,entry.body);
 const target=entry.card.offsetTop-viewport.clientHeight/3;
 viewport.scrollTo({top:Math.max(0,target),behavior:"smooth"});
 spider.style.top=(entry.card.offsetTop+8)+"px";
 spider.style.left=(entry.card.offsetLeft+entry.card.clientWidth-42)+"px";
 progress.textContent="Scanning "+(index+1)+" / "+records.length;
 status.textContent=r.category+" · Passage "+r.passage+" · "+r.keywords;
 index++;
}
function reset(){
 index=0;entries.forEach(({card,body},i)=>{card.classList.remove("active","visited");body.textContent=records[i].text;});
 viewport.scrollTo({top:0,behavior:"instant"});playing=true;toggle.textContent="Pause";
 progress.textContent="Restarting";status.textContent="Searching for matches";
}
toggle.onclick=()=>{if(index>=records.length)reset();else{playing=!playing;toggle.textContent=playing?"Pause":"Play";}};
document.getElementById("restart").onclick=reset;
if(records.length){scan();timer=setInterval(scan,950);}
else{progress.textContent="No passages found";toggle.disabled=true;}
</script></body></html>""".replace("__DATA__", payload)
    components.html(page, height=height, scrolling=False)
