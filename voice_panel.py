import base64
from pathlib import Path
from streamlit.components.v2 import component

HTML = """
<div class="profile">
  <button id="logo" aria-label="에이블 녹음 시작 또는 종료">
    <span class="crop"><img id="image" alt="에이블 로고"></span>
  </button>
  <h2>에이블</h2>
  <p id="status" aria-live="polite">로고를 눌러 말씀하세요</p>
  <button id="replay" hidden>답변 다시 듣기</button>
</div>
"""
CSS = """
.profile{text-align:center;padding:18px 8px;color:#20584e}
#logo{width:168px;height:168px;border-radius:50%;border:2px solid #63cfb7;background:#dbf7ef;cursor:pointer;display:grid;place-items:center;margin:auto;box-shadow:0 0 0 9px #54ccb21a;transition:transform .08s,box-shadow .08s}
#logo:focus-visible{outline:3px solid #158b80;outline-offset:5px}
#logo[data-mode=recording]{border-color:#ed6868;box-shadow:0 0 0 12px #ed686822}
#logo:disabled{cursor:wait;opacity:.65}
.crop{position:relative;display:block;width:148px;height:116px;overflow:hidden;border-radius:38%;mix-blend-mode:multiply}
.crop img{position:absolute;width:552.32px;max-width:none;left:-47px;top:-77px}
h2{margin:16px 0 5px;font-size:24px}p{font-size:12px;min-height:32px;margin:5px 0;line-height:1.6}
#replay{background:white;color:#218776;border:1px solid #9bd9cc;border-radius:10px;padding:6px 13px;cursor:pointer}
@media(prefers-reduced-motion:reduce){#logo{transform:none!important}}
"""
JS = """
export default function(component) {
  const {parentElement:root, data, setTriggerValue} = component;
  const button=root.querySelector('#logo'), status=root.querySelector('#status');
  const replay=root.querySelector('#replay');
  const s=root._able||(root._able={reply:'',recording:false,starting:false,busy:false});
  s.emit=setTriggerValue;
  s.chat=data.chat_id;
  root.querySelector('#image').src=data.logo;
  function idle(text){cancelAnimationFrame(s.frame);button.style.transform='scale(1)';button.style.boxShadow='';button.dataset.mode='idle';status.textContent=text;}
  function stopVoice(){if(s.source){try{s.source.stop();}catch(e){}s.source=null;}idle('로고를 눌러 말씀하세요');}
  async function context(){s.ctx=s.ctx||new(window.AudioContext||window.webkitAudioContext)();await s.ctx.resume();return s.ctx;}
  function animate(){if(!s.source)return;s.analyser.getByteFrequencyData(s.values);let power=s.values.reduce((a,b)=>a+b,0)/s.values.length/255;button.style.transform=`scale(${1+power*.13})`;button.style.boxShadow=`0 0 ${20+power*60}px ${9+power*25}px #2cc5a65c`;s.frame=requestAnimationFrame(animate);}
  async function play(){
    if(!s.buffer)return;
    stopVoice();
    const ctx=await context();
    if(ctx.state!=='running'){status.textContent='답변 다시 듣기를 눌러주세요';return;}
    s.analyser=ctx.createAnalyser();s.analyser.fftSize=128;s.values=new Uint8Array(s.analyser.frequencyBinCount);
    const source=ctx.createBufferSource();source.buffer=s.buffer;source.connect(s.analyser);s.analyser.connect(ctx.destination);s.source=source;
    source.onended=()=>{if(s.source===source){s.source=null;idle('다음 말씀을 기다리고 있어요');}};
    source.start();status.textContent='에이블이 말씀드리고 있어요';animate();
  }
  replay.onclick=()=>play().catch(()=>idle('브라우저의 소리 재생 권한을 확인해주세요'));
  button.onclick=async()=>{
    if(s.busy||s.starting)return;
    if(s.recording){status.textContent='녹음을 마무리하고 있어요';s.recorder.stop();return;}
    s.starting=true;button.disabled=true;
    try{
      stopVoice();await context();
      const stream=await navigator.mediaDevices.getUserMedia({audio:true});
      const mime=['audio/webm;codecs=opus','audio/mp4'].find(t=>MediaRecorder.isTypeSupported(t));
      const recorder=new MediaRecorder(stream,mime?{mimeType:mime}:undefined);
      const chunks=[];let size=0;const chatId=s.chat;
      s.recorder=recorder;s.stream=stream;s.recording=true;s.tooLarge=false;
      recorder.ondataavailable=e=>{if(e.data.size){chunks.push(e.data);size+=e.data.size;if(size>24000000&&recorder.state==='recording'){s.tooLarge=true;recorder.stop();}}};
      recorder.onstop=async()=>{
        stream.getTracks().forEach(t=>t.stop());s.recording=false;
        if(s.tooLarge){button.disabled=false;idle('24MB를 넘었어요. 짧게 나눠 녹음해주세요.');return;}
        if(chatId!==s.chat){button.disabled=false;idle('대화가 바뀌어 녹음을 취소했어요');return;}
        s.busy=true;button.disabled=true;status.textContent='에이블이 처리하고 있어요';
        const blob=new Blob(chunks,{type:recorder.mimeType});const reader=new FileReader();
        reader.onload=()=>s.emit('recording',{id:crypto.randomUUID(),chat_id:chatId,mime:blob.type,audio:reader.result.split(',')[1]});
        reader.onerror=()=>{s.busy=false;button.disabled=false;idle('녹음 파일을 읽지 못했어요. 다시 시도해주세요');};
        reader.readAsDataURL(blob);
      };
      recorder.start(250);button.dataset.mode='recording';status.textContent='듣고 있어요 · 로고를 다시 누르면 종료';
    }catch(e){s.stream?.getTracks().forEach(t=>t.stop());s.recording=false;idle('마이크 권한과 HTTPS 접속을 확인해주세요');}
    finally{s.starting=false;if(!s.busy)button.disabled=false;}
  };
  if(s.previousChat&&s.previousChat!==data.chat_id){stopVoice();s.buffer=null;replay.hidden=true;s.busy=false;button.disabled=false;}
  s.previousChat=data.chat_id;
  if(!data.enabled&&s.source)stopVoice();
  if(data.reply_id&&data.reply_id!==s.reply){
    stopVoice();s.reply=data.reply_id;s.busy=false;button.disabled=false;
    if(data.audio&&data.enabled){
      replay.hidden=false;
      const bytes=Uint8Array.from(atob(data.audio),c=>c.charCodeAt(0));
      s.ctx=s.ctx||new(window.AudioContext||window.webkitAudioContext)();
      s.ctx.decodeAudioData(bytes.buffer).then(buffer=>{s.buffer=buffer;return play();}).catch(()=>idle('음성 재생에 실패했어요. 답변 다시 듣기를 눌러주세요'));
    }else{replay.hidden=true;s.buffer=null;idle(data.notice||'답변을 준비했어요. 다음 말씀을 들려주세요');}
  }
}
"""

_profile = component("able_profile", html=HTML, css=CSS, js=JS)


def able_profile(chat_id, audio=None, reply_id="", enabled=True, notice=""):
    logo = Path(__file__).parent / "assets" / "aivle-reference.png"
    image = "data:image/png;base64," + base64.b64encode(logo.read_bytes()).decode()
    return _profile(
        key="able_profile",
        data={"chat_id": chat_id, "logo": image,
              "audio": base64.b64encode(audio).decode() if audio else "",
              "reply_id": reply_id, "enabled": enabled, "notice": notice},
        on_recording_change=lambda: None,
    )
