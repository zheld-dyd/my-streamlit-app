"""원본 로고와 실제 재생 음량에 반응하는 에이블 음성 패널."""
import base64
from pathlib import Path

import streamlit as st


def voice_panel(audio=None, autoplay=False):
    source = Path(__file__).parent / "assets" / "aivle-reference.png"
    if source.exists():
        logo = base64.b64encode(source.read_bytes()).decode()
        identity = f'<div class="logo-crop"><img alt="AIVLE 심벌" src="data:image/png;base64,{logo}"></div>'
    else:
        identity = '<span style="font-size:52px;color:#009da4">✦</span>'
    audio_tag = ""
    if audio:
        encoded = base64.b64encode(audio).decode()
        audio_tag = f'<audio id="speech" controls {"autoplay" if autoplay else ""} src="data:audio/mp3;base64,{encoded}"></audio>'
    page = """<!doctype html><html lang="ko"><meta charset="utf-8"><style>
    *{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;color:#234541}
    .panel{background:linear-gradient(125deg,#e0f7f0,#f1fbf8);border:1px solid #cbece1;border-radius:24px;padding:22px;display:flex;gap:22px;align-items:center;min-height:195px}
    .orb{position:relative;width:154px;height:154px;min-width:154px;display:grid;place-items:center;border-radius:50%;background:#c5f1e5;box-shadow:0 0 0 9px #b7e9da44;transition:box-shadow .1s,transform .1s}
    .ring{position:absolute;inset:-6px;border:1px solid #14b8a677;border-radius:50%;pointer-events:none}
    .logo-crop{position:relative;width:148px;height:116px;overflow:hidden;border-radius:38%;mix-blend-mode:multiply}
    .logo-crop img{position:absolute;max-width:none;width:552.32px;height:auto;left:-47px;top:-77px}
    .copy{min-width:0;flex:1}.eyebrow{font-size:10px;letter-spacing:.22em;color:#408c7d}.name{font-size:26px;font-weight:750;margin:4px 0}
    #state{font-size:12px;color:#508176;margin-bottom:9px}.bars{height:28px;display:flex;align-items:center;gap:3px}
    .bar{width:4px;height:3px;border-radius:5px;background:#19a995;transition:height .07s}
    audio{display:block;width:min(100%,420px);height:32px;margin-top:8px}.notice{font-size:10px;color:#5c8076;margin-top:8px}
    @media(max-width:500px){.panel{padding:16px;gap:15px}.orb{width:112px;height:112px;min-width:112px}.logo-crop{transform:scale(.73)}.name{font-size:22px}.bar{width:3px;gap:2px}}
    @media(prefers-reduced-motion:reduce){.orb{transform:none!important}.ring{display:none}}
    </style><div class="panel"><div class="orb" id="orb"><div class="ring" id="ring"></div>IDENTITY</div><div class="copy"><div class="eyebrow">AIVLE · PERSONAL ASSISTANT</div><div class="name">에이블</div><div id="state" aria-live="polite">말씀을 기다리고 있어요</div><div class="bars" aria-hidden="true">BARS</div>AUDIO<div class="notice">AI가 생성한 음성 · 자동 재생이 안 되면 재생 버튼을 눌러주세요.</div></div></div>
    <script>
    const audio=document.getElementById('speech'),orb=document.getElementById('orb'),ring=document.getElementById('ring'),state=document.getElementById('state');
    const bars=[...document.querySelectorAll('.bar')];let ctx,analyser,data,frame;
    function idle(label){cancelAnimationFrame(frame);state.textContent=label;orb.style.transform='scale(1)';orb.style.boxShadow='0 0 0 9px #b7e9da44';ring.style.transform='scale(1)';bars.forEach(b=>b.style.height='3px');}
    function draw(){if(!audio||audio.paused)return;analyser.getByteFrequencyData(data);let power=0;bars.forEach((bar,i)=>{let v=data[Math.floor(i*data.length/bars.length)]/255;power+=v;bar.style.height=(3+v*25)+'px';});power/=bars.length;orb.style.transform='scale('+(1+power*.05)+')';orb.style.boxShadow='0 0 '+(12+power*40)+'px '+(9+power*22)+'px #34c7ab44';ring.style.transform='scale('+(1+power*.19)+')';frame=requestAnimationFrame(draw);}
    if(audio){state.textContent='답변이 준비됐어요';audio.addEventListener('play',async()=>{try{if(!ctx){ctx=new (window.AudioContext||window.webkitAudioContext)();analyser=ctx.createAnalyser();analyser.fftSize=128;const source=ctx.createMediaElementSource(audio);source.connect(analyser);analyser.connect(ctx.destination);data=new Uint8Array(analyser.frequencyBinCount);}await ctx.resume();state.textContent='에이블이 말씀드리고 있어요';draw();}catch(e){state.textContent='답변을 재생하고 있어요';}});audio.addEventListener('pause',()=>idle('일시 정지했어요'));audio.addEventListener('ended',()=>idle('다음 말씀을 기다리고 있어요'));audio.addEventListener('error',()=>idle('음성을 재생하지 못했어요'));}
    </script></html>"""
    page = page.replace("IDENTITY", identity).replace("BARS", '<span class="bar"></span>'*24).replace("AUDIO", audio_tag)
    st.iframe(page, height=225)
