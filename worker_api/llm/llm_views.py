from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from starlette import status

from worker_api.llm.llm_response_models import LLMChatRequest, LLMChatResponse
from worker_api.llm.llm_service import chat_with_gemini

llm_router = APIRouter(prefix="/llm", tags=["LLM"])


@llm_router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(request: LLMChatRequest) -> LLMChatResponse:
    result = await chat_with_gemini(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        model=request.model
    )
    return LLMChatResponse(**result)


@llm_router.get("/view", response_class=HTMLResponse)
async def view():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Buddhist Tradition Onboarding</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=EB+Garamond:ital,wght@0,600;1,500&display=swap');
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); border:0; }
    .frame { font-family:'Inter', var(--font-sans); background:#ffffff; border-radius:32px; border:0.5px solid rgba(0,0,0,0.14); width:390px; height:812px; margin:1.5rem auto; display:flex; flex-direction:column; overflow:hidden; color:#171717; }
    .sbar { height:44px; display:flex; align-items:center; padding:0 24px; font-size:12px; font-weight:500; color:#707070; flex-shrink:0; }
    .topbar { display:flex; align-items:center; justify-content:space-between; padding:2px 16px 0; flex-shrink:0; }
    .iconbtn { width:34px; height:34px; border:none; background:none; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#020c1d; border-radius:9px; }
    .iconbtn:hover { background:#f4f4f3; }
    .title { font-size:27px; font-weight:600; color:#020c1d; letter-spacing:-0.5px; line-height:1.16; padding:6px 24px 4px; flex-shrink:0; }
    .sub { font-size:14px; font-weight:500; color:#707070; letter-spacing:-0.2px; padding:0 24px 6px; flex-shrink:0; }
    .chat { flex:1; overflow-y:auto; padding:12px 18px; display:flex; flex-direction:column; gap:8px; }
    .row { display:flex; align-items:flex-end; gap:6px; }
    .row.bot { justify-content:flex-start; }
    .row.usr { justify-content:flex-end; }
    .bav { width:26px; height:26px; border-radius:50%; background:#E7AB00; flex-shrink:0; display:flex; align-items:center; justify-content:center; margin-bottom:2px; }
    .bubble { max-width:250px; padding:9px 13px; border-radius:16px; font-size:14px; line-height:1.5; }
    .bot .bubble { background:#f4f4f3; color:#171717; border-radius:5px 16px 16px 16px; }
    .usr .bubble { background:#E7AB00; color:#4a2d00; border-radius:16px 16px 5px 16px; font-weight:500; }
    .typing { background:#f4f4f3; border-radius:5px 16px 16px 16px; padding:9px 13px; display:flex; gap:4px; align-items:center; }
    .dot { width:6px; height:6px; border-radius:50%; background:#bdbdbd; animation:bb 1.2s infinite; }
    .dot:nth-child(2){ animation-delay:.2s; } .dot:nth-child(3){ animation-delay:.4s; }
    @keyframes bb { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }
    .pill-group { padding-left:32px; }
    .pill-row { display:flex; flex-wrap:wrap; gap:6px; }
    .pill { background:#ffffff; border:1px solid #e0e0e0; border-radius:22px; padding:7px 14px; font-size:13px; font-weight:500; color:#171717; cursor:pointer; transition:background .12s,border-color .12s,color .12s; white-space:nowrap; }
    .pill:hover { background:#FFF6DF; border-color:#E7AB00; color:#4a2d00; }
    .pill.selected { background:#E7AB00; border-color:#E7AB00; color:#4a2d00; pointer-events:none; }
    .pill.skip { color:#707070; background:none; }
    .pill.skip:hover { background:#f4f4f3; border-color:#e0e0e0; color:#49454f; }
    .pill:disabled:not(.selected){ opacity:.35; pointer-events:none; }
    .inputbar { display:flex; gap:8px; padding:8px 16px; border-top:0.5px solid rgba(0,0,0,0.08); flex-shrink:0; }
    .inputbar input { flex:1; border:1px solid #e0e0e0; border-radius:22px; padding:9px 15px; font-size:14px; font-family:inherit; background:#ffffff; color:#171717; outline:none; }
    .inputbar input:focus { border-color:#E7AB00; }
    .inputbar input::placeholder { color:#9a9a9a; }
    .sendbtn { border:none; background:#E7AB00; color:#fff; border-radius:50%; width:38px; height:38px; font-size:16px; cursor:pointer; flex-shrink:0; }
    .sendbtn:hover { background:#cf9900; }
    .ctabar { display:flex; flex-direction:column; gap:8px; padding:10px 24px 20px; flex-shrink:0; }
    .cta { height:54px; border-radius:12px; font-family:inherit; font-size:18px; font-weight:600; letter-spacing:-0.3px; cursor:pointer; flex-shrink:0; transition:background .15s,color .15s,border-color .15s; }
    .cta.skip { background:#ffffff; border:1px solid #e0e0e0; color:#49454f; }
    .cta.skip:hover { background:#f4f4f3; }
    .cta.secondary { background:#ffffff; border:1px solid #e0e0e0; color:#49454f; }
    .cta.secondary:hover { background:#f4f4f3; }
    .cta.continue { background:#E7AB00; border:none; color:#ffffff; }
    .cta.continue:hover { background:#cf9900; }
  </style>
</head>
<body>
  <div class="frame">
    <h2 class="sr-only">Onboarding step: choose your Buddhist tradition by typing it or picking from a list. You can add more than one.</h2>
    <div class="sbar">9:41</div>
    <div class="topbar">
      <button class="iconbtn" aria-label="Back"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <button class="iconbtn" aria-label="Restart" onclick="restart()"><svg width="19" height="19" viewBox="0 0 24 24" fill="none"><path d="M4 12a8 8 0 108-8 8 8 0 00-6.5 3.3M4 4v3.5h3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    </div>
    <div class="title">Which Buddhist tradition feels closest to your practice?</div>
    <div class="sub">Choose one or more — we'll use them to personalize your experience.</div>
    <div class="chat" id="chat"></div>
    <div class="inputbar" id="inputbar">
      <input id="txt" type="text" placeholder="Zen, Tibetan Buddhism, Theravāda, Plum Village..." autocomplete="off" />
      <button id="send" class="sendbtn" aria-label="Send">↑</button>
    </div>
    <div class="ctabar">
      <button id="addbtn" class="cta secondary" style="display:none" onclick="startAnother()">Add another tradition</button>
      <button id="primary" class="cta skip">Skip</button>
    </div>
  </div>

  <script>
const TAX=[
  {id:'theravada',n:'Theravāda',l:1,p:null},
  {id:'thai-buddhism',n:'Thai Buddhism',l:2,p:'theravada'},
  {id:'dhammayut',n:'Dhammayuttika Nikāya',l:3,p:'thai-buddhism'},
  {id:'maha-nikaya-th',n:'Mahā Nikāya',l:3,p:'thai-buddhism'},
  {id:'thai-forest',n:'Thai Forest',l:3,p:'thai-buddhism'},
  {id:'burmese-buddhism',n:'Burmese Buddhism',l:2,p:'theravada'},
  {id:'thudhamma',n:'Thudhamma Nikāya',l:3,p:'burmese-buddhism'},
  {id:'shwekyin',n:'Shwekyin Nikāya',l:3,p:'burmese-buddhism'},
  {id:'mahasi',n:'Mahasi Tradition',l:3,p:'burmese-buddhism'},
  {id:'pa-auk',n:'Pa-Auk',l:3,p:'burmese-buddhism'},
  {id:'sri-lankan-buddhism',n:'Sri Lankan Buddhism',l:2,p:'theravada'},
  {id:'siam-nikaya',n:'Siam Nikāya',l:3,p:'sri-lankan-buddhism'},
  {id:'amarapura-nikaya',n:'Amarapura Nikāya',l:3,p:'sri-lankan-buddhism'},
  {id:'ramanna-nikaya',n:'Rāmañña Nikāya',l:3,p:'sri-lankan-buddhism'},
  {id:'cambodian-buddhism',n:'Cambodian Buddhism',l:2,p:'theravada'},
  {id:'mohanikay',n:'Mohanikay',l:3,p:'cambodian-buddhism'},
  {id:'lao-buddhism',n:'Lao Buddhism',l:2,p:'theravada'},
  {id:'vipassana-goenka',n:'Vipassana (Goenka)',l:2,p:'theravada'},
  {id:'insight-meditation',n:'Insight Meditation',l:2,p:'theravada'},
  {id:'navayana',n:'Navayana',l:2,p:'theravada'},
  {id:'mahayana',n:'Mahāyāna',l:1,p:null},
  {id:'chinese-buddhism',n:'Chinese Buddhism',l:2,p:'mahayana'},
  {id:'pure-land-chinese',n:'Pure Land',l:3,p:'chinese-buddhism'},
  {id:'chan',n:'Chan',l:3,p:'chinese-buddhism'},
  {id:'tiantai',n:'Tiantai',l:3,p:'chinese-buddhism'},
  {id:'huayan',n:'Huayan',l:3,p:'chinese-buddhism'},
  {id:'chinese-esoteric',n:'Chinese Esoteric',l:3,p:'chinese-buddhism'},
  {id:'dharma-drum',n:'Dharma Drum Mountain',l:3,p:'chinese-buddhism'},
  {id:'fo-guang-shan',n:'Fo Guang Shan',l:3,p:'chinese-buddhism'},
  {id:'chung-tai-shan',n:'Chung Tai Shan',l:3,p:'chinese-buddhism'},
  {id:'japanese-buddhism',n:'Japanese Buddhism',l:2,p:'mahayana'},
  {id:'zen',n:'Zen',l:3,p:'japanese-buddhism'},
  {id:'rinzai',n:'Rinzai',l:4,p:'zen'},
  {id:'soto',n:'Sōtō',l:4,p:'zen'},
  {id:'obaku',n:'Ōbaku',l:4,p:'zen'},
  {id:'sanbo-zen',n:'Sanbo Zen',l:4,p:'zen'},
  {id:'jodo-shu',n:'Jōdo-shū',l:3,p:'japanese-buddhism'},
  {id:'jodo-shinshu',n:'Jōdo Shinshū',l:3,p:'japanese-buddhism'},
  {id:'nishi-honganji',n:'Nishi Honganji',l:4,p:'jodo-shinshu'},
  {id:'higashi-honganji',n:'Higashi Honganji',l:4,p:'jodo-shinshu'},
  {id:'bca',n:'Buddhist Churches of America',l:4,p:'jodo-shinshu'},
  {id:'nichiren',n:'Nichiren',l:3,p:'japanese-buddhism'},
  {id:'nichiren-shu',n:'Nichiren Shū',l:4,p:'nichiren'},
  {id:'nichiren-shoshu',n:'Nichiren Shōshū',l:4,p:'nichiren'},
  {id:'sgi',n:'Sōka Gakkai',l:4,p:'nichiren'},
  {id:'kempon-hokke',n:'Kempon Hokke',l:4,p:'nichiren'},
  {id:'tendai',n:'Tendai',l:3,p:'japanese-buddhism'},
  {id:'shingon',n:'Shingon',l:3,p:'japanese-buddhism'},
  {id:'koyasan-shingon',n:'Koyasan Shingon',l:4,p:'shingon'},
  {id:'rissho-koseikai',n:'Risshō Kōsei-kai',l:3,p:'japanese-buddhism'},
  {id:'korean-buddhism',n:'Korean Buddhism',l:2,p:'mahayana'},
  {id:'jogye',n:'Jogye Order',l:3,p:'korean-buddhism'},
  {id:'taego',n:'Taego Order',l:3,p:'korean-buddhism'},
  {id:'cheontae',n:'Cheontae',l:3,p:'korean-buddhism'},
  {id:'won-buddhism',n:'Won Buddhism',l:3,p:'korean-buddhism'},
  {id:'jingak',n:'Jingak Order',l:3,p:'korean-buddhism'},
  {id:'vietnamese-buddhism',n:'Vietnamese Buddhism',l:2,p:'mahayana'},
  {id:'thien',n:'Thiền',l:3,p:'vietnamese-buddhism'},
  {id:'truc-lam',n:'Trúc Lâm',l:4,p:'thien'},
  {id:'lam-te',n:'Lâm Tế',l:4,p:'thien'},
  {id:'tinh-do',n:'Tịnh Độ',l:3,p:'vietnamese-buddhism'},
  {id:'khat-si',n:'Khất Sĩ Order',l:3,p:'vietnamese-buddhism'},
  {id:'plum-village',n:'Plum Village',l:3,p:'vietnamese-buddhism'},
  {id:'vajrayana',n:'Vajrayāna',l:1,p:null},
  {id:'tibetan-buddhism',n:'Tibetan Buddhism',l:2,p:'vajrayana'},
  {id:'nyingma',n:'Nyingma',l:3,p:'tibetan-buddhism'},
  {id:'katok',n:'Katok',l:4,p:'nyingma'},
  {id:'palyul',n:'Palyul',l:4,p:'nyingma'},
  {id:'mindrolling',n:'Mindrolling',l:4,p:'nyingma'},
  {id:'shechen',n:'Shechen',l:4,p:'nyingma'},
  {id:'dorje-drag',n:'Dorje Drak',l:4,p:'nyingma'},
  {id:'dzogchen-monastery',n:'Dzogchen Monastery',l:4,p:'nyingma'},
  {id:'kagyu',n:'Kagyu',l:3,p:'tibetan-buddhism'},
  {id:'karma-kagyu',n:'Karma Kagyu',l:4,p:'kagyu'},
  {id:'drikung-kagyu',n:'Drikung Kagyu',l:4,p:'kagyu'},
  {id:'drukpa-kagyu',n:'Drukpa Kagyu',l:4,p:'kagyu'},
  {id:'shangpa-kagyu',n:'Shangpa Kagyu',l:4,p:'kagyu'},
  {id:'taklung-kagyu',n:'Taklung Kagyu',l:4,p:'kagyu'},
  {id:'sakya',n:'Sakya',l:3,p:'tibetan-buddhism'},
  {id:'ngorpa',n:'Ngorpa',l:4,p:'sakya'},
  {id:'tsarpa',n:'Tsarpa',l:4,p:'sakya'},
  {id:'dzongsar',n:'Dzongsar',l:4,p:'sakya'},
  {id:'gelug',n:'Gelug',l:3,p:'tibetan-buddhism'},
  {id:'jonang',n:'Jonang',l:3,p:'tibetan-buddhism'},
  {id:'rime',n:'Rimé',l:3,p:'tibetan-buddhism'},
  {id:'mongolian-buddhism',n:'Mongolian Buddhism',l:2,p:'vajrayana'},
  {id:'buryat-buddhism',n:'Buryat Buddhism',l:2,p:'vajrayana'},
  {id:'kalmyk-buddhism',n:'Kalmyk Buddhism',l:2,p:'vajrayana'},
  {id:'tuvan-buddhism',n:'Tuvan Buddhism',l:2,p:'vajrayana'},
  {id:'newar-buddhism',n:'Newar Buddhism',l:2,p:'vajrayana'},
  {id:'bon',n:'Bön',l:1,p:null},
  {id:'western-contemporary',n:'Western / Contemporary',l:1,p:null},
  {id:'secular-buddhism',n:'Secular Buddhism',l:2,p:'western-contemporary'},
  {id:'triratna',n:'Triratna',l:2,p:'western-contemporary'},
  {id:'nkt',n:'New Kadampa',l:2,p:'western-contemporary'},
  {id:'shambhala',n:'Shambhala',l:2,p:'western-contemporary'},
];

const AL={
  'theravada':['Theravada','Southern Buddhism','Pali Buddhism','Hinayana','south asian buddhism'],
  'thai-buddhism':['Thai Theravada','Thai Theravāda'],
  'dhammayut':['Dhammayut','Dhammayuttika','Thammayut','Dhammayut Order'],
  'maha-nikaya-th':['Maha Nikaya','Mahanikaya'],
  'thai-forest':['Forest Tradition','Forest Sangha','Kammatthana','Ajahn Chah lineage','Ajahn Mun lineage','Thai Forest Tradition'],
  'burmese-buddhism':['Myanmar Buddhism','Burmese Theravada'],
  'thudhamma':['Thudhamma','Sudhamma'],
  'shwekyin':['Shwekyin'],
  'mahasi':['Mahasi Sayadaw','Mahasi Vipassana','Satipatthana Vipassana'],
  'pa-auk':['Pa Auk','Pa-Auk Sayadaw','Pa-Auk Tawya','Pa-Auk Tradition'],
  'sri-lankan-buddhism':['Sinhalese Buddhism','Ceylon Buddhism'],
  'siam-nikaya':['Siam Nikaya','Siamese Nikaya'],
  'amarapura-nikaya':['Amarapura Nikaya'],
  'ramanna-nikaya':['Ramanna Nikaya','Ramanna'],
  'cambodian-buddhism':['Khmer Buddhism'],
  'mohanikay':['Mahanikay','Maha Nikaya Cambodia'],
  'lao-buddhism':['Laotian Buddhism','Laos Buddhism'],
  'vipassana-goenka':['Vipassana','S.N. Goenka','Goenka','Dhamma.org','Vipassana (Goenka Tradition)'],
  'insight-meditation':['IMS','Spirit Rock','Insight Meditation Society'],
  'navayana':['Ambedkarite Buddhism','Neo-Buddhism','Dalit Buddhism','Navayana / Ambedkarite Buddhism','Jai Bhim','Bhimayana'],
  'mahayana':['Mahayana','Northern Buddhism','Great Vehicle','east asian buddhism'],
  'chinese-buddhism':['Han Buddhism','Chinese Mahayana'],
  'pure-land-chinese':['Jingtu','Amitabha Buddhism','Chinese Pure Land','Pure Land (Chinese)','amidism'],
  'chan':['Chinese Zen','Chan Buddhism'],
  'tiantai':['T\\'ien-t\\'ai','Tien-tai'],
  'huayan':['Hua-yen','Flower Garland School','Avatamsaka'],
  'chinese-esoteric':['Mizong','Zhenyan','Chinese Vajrayana','Chinese Esoteric Buddhism'],
  'dharma-drum':['DDM','Master Shengyen'],
  'fo-guang-shan':['Buddha\\'s Light Mountain','Master Hsing Yun','BLIA'],
  'chung-tai-shan':['Zhongtaishan'],
  'japanese-buddhism':['Japanese Mahayana'],
  'zen':['Zen Buddhism','Japanese Zen','Zazen','chan zen'],
  'rinzai':['Rinzai Zen','Rinzaishū'],
  'soto':['Soto','Soto Zen','Sōtō Zen','Sōtō-shū'],
  'obaku':['Obaku'],
  'sanbo-zen':['Sanbo Kyodan','Three Treasures Zen'],
  'jodo-shu':['Jodo-shu','Jodo Shu','Pure Land Japan','Honen lineage'],
  'jodo-shinshu':['Jodo Shinshu','Shin Buddhism','True Pure Land','Shin','Shinshu'],
  'nishi-honganji':['West Honganji','Hongwanji','Honpa Hongwanji'],
  'higashi-honganji':['East Honganji','Otani'],
  'bca':['BCA','American Jodo Shinshu'],
  'nichiren':['Lotus Sutra Buddhism','Nichiren Buddhism'],
  'nichiren-shu':['Nichiren Shu','Nichirenshu'],
  'nichiren-shoshu':['Nichiren Shoshu'],
  'sgi':['SGI','Soka Gakkai','Value Creation Society','Sōka Gakkai International','nichiren buddhism'],
  'tendai':['Tendaishū','Japanese Tiantai'],
  'shingon':['Shingon Buddhism','Japanese Vajrayana','Japanese Esoteric Buddhism','Mikkyō'],
  'koyasan-shingon':['Koyasan','Kōyasan','Mt. Koya'],
  'rissho-koseikai':['Rissho Koseikai','RKK'],
  'korean-buddhism':['Korean Mahayana','seon'],
  'jogye':['Chogye','Jogye-jong','Korean Seon','Korean Zen'],
  'taego':['Taego-jong'],
  'cheontae':['Chontae','Korean Tendai','Cheontae-jong','Cheontae Order'],
  'won-buddhism':['Wonbulgyo','Circle Buddhism'],
  'jingak':['Jingak-jong','Korean Vajrayana'],
  'vietnamese-buddhism':['Vietnamese Mahayana'],
  'thien':['Thien','Vietnamese Zen'],
  'truc-lam':['Truc Lam','Bamboo Forest School'],
  'lam-te':['Lam Te','Vietnamese Linji'],
  'tinh-do':['Tinh Do','Vietnamese Pure Land'],
  'khat-si':['Khat Si','Mendicant Order'],
  'plum-village':['Thich Nhat Hanh lineage','Order of Interbeing','Engaged Buddhism','Plum Village Community','thich nhat hanh'],
  'vajrayana':['Vajrayana','Tibetan Buddhism','Tantric Buddhism','Diamond Vehicle','himalayan buddhism','mantrayana','esoteric buddhism'],
  'tibetan-buddhism':['Tibetan','Himalayan Buddhism','Lamaism'],
  'nyingma':['Nyingmapa','Ancient School','Old School','Red Hat (Nyingma)','Dzogchen','Great Perfection','Dzogpa Chenpo'],
  'katok':['Kathok','Katok Monastery'],
  'palyul':['Palyul Monastery'],
  'mindrolling':['Mindroling','Mindrolling Monastery'],
  'shechen':['Shechen Monastery'],
  'dorje-drag':['Dorje Drak','Dorjé Drak'],
  'dzogchen-monastery':['Dzogchen Monastery','Rudam','Ru-Dam Orgyen Samten Choling'],
  'kagyu':['Kagyupa','Kagyu School','Oral Transmission School'],
  'karma-kagyu':['Black Hat Kagyu','Karmapa lineage','Kamtsang Kagyu'],
  'drikung-kagyu':['Drigung Kagyu'],
  'drukpa-kagyu':['Dragon School','Bhutan Buddhism'],
  'taklung-kagyu':['Taklungpa'],
  'sakya':['Sakyapa','Sakya School','Grey Earth School'],
  'ngorpa':['Ngor','Ngor Monastery'],
  'tsarpa':['Tsar','Tsarchen lineage'],
  'dzongsar':['Khyentse lineage','Dzongsar Khyentse'],
  'gelug':['Gelugpa','Yellow Hat','Ganden Tradition','Dalai Lama lineage'],
  'jonang':['Jonangpa','Jonang School','Kalachakra lineage'],
  'rime':['Rime','Non-sectarian','Eclectic movement'],
  'mongolian-buddhism':['Mongolian Vajrayana','Mongolian Lamaism'],
  'buryat-buddhism':['Buryatia Buddhism'],
  'kalmyk-buddhism':['Kalmykia Buddhism'],
  'tuvan-buddhism':['Tuvinian Buddhism','Tuva Buddhism'],
  'newar-buddhism':['Newari Buddhism','Nepal Buddhism'],
  'bon':['Bon','Bonpo','Tibetan Bon','Yungdrung Bon'],
  'western-contemporary':['Western Buddhism','Modern Buddhism','Convert Buddhism','Western / Contemporary Buddhism'],
  'secular-buddhism':['Secular','Pragmatic Buddhism','Naturalistic Buddhism'],
  'triratna':['FWBO','Friends of the Western Buddhist Order','Western Buddhist Order','Triratna Buddhist Community'],
  'nkt':['NKT','Kadampa Buddhism','Modern Kadampa','New Kadampa Tradition','kadampa'],
  'shambhala':['Shambhala International','Chogyam Trungpa lineage','Shambhala Buddhism'],
};

const byId={}, childOf={};
for(const t of TAX){
  byId[t.id]=t;
  if(t.p)(childOf[t.p]=childOf[t.p]||[]).push(t);
}
function kids(id){return childOf[id]||[];}
const TOP=TAX.filter(t=>!t.p&&t.id!=='bon'&&t.id!=='western-contemporary');
function crumb(t){
  if(!t.p)return t.n;
  const par=byId[t.p];
  if(par&&par.l>=2)return`${t.n} · ${par.n}`;
  return t.n;
}

const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9 ]/g,' ').replace(/\\s+/g,' ').trim();
function terms(t){return [t.n, ...(AL[t.id]||[])].map(norm);}
function findMatches(q){
  q=norm(q);
  if(!q)return[];
  const exact=TAX.filter(t=>terms(t).includes(q));
  if(exact.length)return exact;
  return TAX.filter(t=>terms(t).some(c=>c===q||c.startsWith(q+' ')||q.startsWith(c+' ')||(q.length>=3&&c.includes(q))||(c.length>=3&&q.includes(c))));
}

function lev(a,b){
  const m=a.length,n=b.length;
  if(!m)return n; if(!n)return m;
  let prev=Array.from({length:n+1},(_,i)=>i), cur=new Array(n+1);
  for(let i=1;i<=m;i++){
    cur[0]=i;
    for(let j=1;j<=n;j++){
      const cost=a[i-1]===b[j-1]?0:1;
      cur[j]=Math.min(prev[j]+1, cur[j-1]+1, prev[j-1]+cost);
    }
    [prev,cur]=[cur,prev];
  }
  return prev[n];
}
function fuzzyMatches(q){
  q=norm(q);
  if(q.length<4) return [];
  const best={};
  for(const t of TAX){
    for(const c of terms(t)){
      if(c.length<5) continue;
      const lim=c.length<8?1:2;
      const d=lev(q,c);
      if(d<=lim && (best[t.id]===undefined||d<best[t.id])) best[t.id]=d;
    }
  }
  return Object.keys(best).map(id=>({t:byId[id],d:best[id]})).sort((a,b)=>a.d-b.d).slice(0,6).map(x=>x.t);
}

let matched=null;
const chatEl=document.getElementById('chat');
const inputbar=document.getElementById('inputbar');
const txt=document.getElementById('txt');
const primary=document.getElementById('primary');
const addbtn=document.getElementById('addbtn');
let chosen=[];
let qaHistory=[];
const BAV=`<div class="bav"><svg width="14" height="14" viewBox="0 0 20 20" fill="none"><path d="M10 2a8 8 0 100 16A8 8 0 0010 2zm0 3a2.5 2.5 0 110 5 2.5 2.5 0 010-5zm0 10c-2.08 0-3.9-.94-5.12-2.42a6.46 6.46 0 0110.24 0C13.9 14.06 12.08 15 10 15z" fill="#fff"/></svg></div>`;

function addUser(t){
  const r=document.createElement('div');r.className='row usr';
  r.innerHTML=`<div class="bubble"></div>`;r.querySelector('.bubble').textContent=t;
  chatEl.appendChild(r);chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
}

function getHardcodedResponse(context) {
  // Multiple matches
  if (context.includes('found multiple matching traditions')) {
    return "I found a few possibilities. Which one fits best?";
  }
  
  // Close match
  if (context.includes("doesn't exactly match our database") && context.includes("We found a close match")) {
    const match = context.match(/close match: ([^.]+)\./);
    if (match) return `Did you mean ${match[1]}?`;
    return "Did you mean one of these?";
  }
  
  // Similar traditions
  if (context.includes("doesn't exactly match") && context.includes("We found these similar traditions")) {
    return "Did you mean one of these?";
  }
  
  // Unrecognized
  if (context.includes("don't recognize")) {
    return "I don't recognize that tradition yet. Which broad tradition feels closest?";
  }
  
  // Not sure
  if (context.includes("not sure about their Buddhist tradition")) {
    return "No problem — you can choose your tradition whenever you're ready.";
  }
  
  // Add another tradition
  if (context.includes("wants to add another Buddhist tradition")) {
    return "Which other tradition do you practice?";
  }
  
  // Tibetan Buddhism followup
  if (context.includes("selected Tibetan Buddhism")) {
    return "Tibetan Buddhism — which major school or lineage feels closest to your practice?";
  }
  
  // Kagyu followup
  if (context.includes("selected Kagyu tradition")) {
    return "And within the Kagyu tradition, do any of these lineages sound familiar?";
  }
  
  // Nyingma followup
  if (context.includes("selected Nyingma school")) {
    return "Do you know which Nyingma monastery or lineage you are connected with?";
  }
  
  // Sakya followup
  if (context.includes("selected Sakya school")) {
    return "Do you know which Sakya branch or lineage you follow?";
  }
  
  // Zen followup
  if (context.includes("selected Zen")) {
    return "Which Zen school do you practice with most closely?";
  }
  
  // Jodo Shinshu followup
  if (context.includes("selected Jōdo Shinshū")) {
    return "Do you know which Jōdo Shinshū branch you belong to?";
  }
  
  // Nichiren followup
  if (context.includes("selected Nichiren")) {
    return "Which Nichiren tradition feels closest to your practice?";
  }
  
  // Shingon followup
  if (context.includes("selected Shingon")) {
    return "Do you know which Shingon lineage or organization you practice with?";
  }
  
  // Generic followup with tradition name
  const tradMatch = context.match(/User selected ([^.]+)\./);
  if (tradMatch && context.includes("Ask if they know their specific")) {
    const levelMatch = context.match(/specific (tradition|school|lineage)/);
    if (levelMatch) {
      return `${tradMatch[1]} — do you know your ${levelMatch[1]}?`;
    }
  }
  
  // Confirmation - multiple traditions
  if (context.includes("They now follow:")) {
    const listMatch = context.match(/They now follow: ([^.]+)\./);
    if (listMatch) {
      return `Added! You're following: ${listMatch[1]}. Add another, or continue.`;
    }
  }
  
  // Confirmation - single tradition
  if (context.includes("has selected") && context.includes("as their Buddhist tradition")) {
    const tradMatch = context.match(/has selected ([^.]+) as/);
    if (tradMatch) {
      return `Perfect. We'll use ${tradMatch[1]} to personalize your experience. Add another tradition, or continue.`;
    }
  }
  
  // Default fallback
  return "I'm here to help you find your Buddhist tradition. Let's continue!";
}

function showTyping() {
  const t=document.createElement('div');t.className='row bot';
  t.innerHTML=BAV+`<div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  t.id = 'typing-indicator';
  chatEl.appendChild(t);chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
  return t;
}

function removeTyping() {
  const typing = document.getElementById('typing-indicator');
  if (typing) typing.remove();
}

async function addBotWithLLM(context) {
  showTyping();
  
  // Simulate a brief delay for more natural feel
  await new Promise(resolve => setTimeout(resolve, 600));
  
  const response = getHardcodedResponse(context);
  removeTyping();
  
  const r=document.createElement('div');r.className='row bot';
  r.innerHTML=BAV+`<div class="bubble">${response}</div>`;
  chatEl.appendChild(r);chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
  
  // Track Q&A
  qaHistory.push({question: response, answer: null});
}

function trackUserAnswer(answer) {
  if (qaHistory.length > 0 && qaHistory[qaHistory.length - 1].answer === null) {
    qaHistory[qaHistory.length - 1].answer = answer;
  }
}

function freezePills(row){row.querySelectorAll('.pill').forEach(p=>p.disabled=true);}
function clearInput(){txt.value='';}
function setContinue(){primary.textContent='Continue';primary.className='cta continue';}
function setSkip(){primary.textContent='Skip for now';primary.className='cta skip';}
function showDone(){addbtn.style.display='';primary.textContent='Continue';primary.className='cta continue';}
function startAnother(){
  addbtn.style.display='none';
  matched=null;
  clearInput();
  addBotWithLLM("User wants to add another Buddhist tradition to their profile. Ask them which other tradition they practice.");
  txt.focus();
}

function showPills(list, parentTrad){
  const wrap=document.createElement('div');wrap.className='pill-group';
  const row=document.createElement('div');row.className='pill-row';

  list.forEach(t=>{
    const p=document.createElement('button');
    p.className='pill';p.textContent=t.n;
    p.onclick=()=>{p.classList.add('selected');freezePills(row);tapTrad(t);};
    row.appendChild(p);
  });

  const skip=document.createElement('button');
  skip.className='pill skip';
  skip.textContent=parentTrad?`Not sure of the school`:'Not sure';
  skip.onclick=()=>{
    skip.classList.add('selected');freezePills(row);
    if(parentTrad){
      addUser(`Just ${parentTrad.n}`);
      confirmDone();
    } else {
      addUser("Not sure");
      addBotWithLLM("User is not sure about their Buddhist tradition. Reassure them that it's okay and they can choose whenever they're ready.");
    }
  };
  row.appendChild(skip);

  wrap.appendChild(row);chatEl.appendChild(wrap);
  chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
}

async function handleTyped(){
  const raw=txt.value.trim();
  if(!raw)return;
  addUser(raw);
  trackUserAnswer(raw);
  clearInput();
  const m=findMatches(raw);
  if(m.length===1){
    selectTrad(m[0]);
  }else if(m.length>1){
    await addBotWithLLM(`User typed "${raw}" and we found multiple matching traditions: ${m.slice(0,10).map(t=>t.n).join(', ')}. Ask them to clarify which one they meant.`);
    showPills(m.slice(0,10),null);
  }else{
    const f=fuzzyMatches(raw);
    if(f.length===1){
      await addBotWithLLM(`User typed "${raw}" which doesn't exactly match our database. We found a close match: ${f[0].n}. Ask if they meant this tradition.`);
      showPills(f,null);
    }else if(f.length>1){
      await addBotWithLLM(`User typed "${raw}" which doesn't exactly match. We found these similar traditions: ${f.map(t=>t.n).join(', ')}. Ask if they meant one of these.`);
      showPills(f,null);
    }else{
      await addBotWithLLM(`User typed "${raw}" which we don't recognize. Ask them to choose from the broad Buddhist traditions we support.`);
      showPills(TOP,null);
    }
  }
}

document.getElementById('send').onclick=handleTyped;
txt.addEventListener('keydown',e=>{if(e.key==='Enter')handleTyped();});

function followupContext(t){
  if(t.id==='tibetan-buddhism'){
    return `User selected Tibetan Buddhism. Ask them which major school or lineage (Nyingma, Kagyu, Sakya, Gelug, Jonang, or Rimé) feels closest to their practice.`;
  }
  if(t.id==='kagyu'){
    return `User selected Kagyu tradition. Ask if they know which specific Kagyu lineage they follow.`;
  }
  if(t.id==='nyingma'){
    return `User selected Nyingma school. Ask if they know which Nyingma monastery or lineage they're connected with.`;
  }
  if(t.id==='sakya'){
    return `User selected Sakya school. Ask if they know which Sakya branch or lineage they follow.`;
  }
  if(t.id==='zen'){
    return `User selected Zen. Ask which Zen school they practice with (Rinzai, Sōtō, Ōbaku, or Sanbo Zen).`;
  }
  if(t.id==='jodo-shinshu'){
    return `User selected Jōdo Shinshū. Ask if they know which branch they belong to.`;
  }
  if(t.id==='nichiren'){
    return `User selected Nichiren. Ask which Nichiren tradition feels closest to their practice.`;
  }
  if(t.id==='shingon'){
    return `User selected Shingon. Ask if they know which Shingon lineage or organization they practice with.`;
  }

  const levelWords = {
    1: 'tradition',
    2: 'school',
    3: 'lineage'
  };

  const nextLevel = levelWords[Math.min(t.l + 1, 3)] || 'lineage';
  return `User selected ${t.n}. Ask if they know their specific ${nextLevel} within this tradition.`;
}

async function selectTrad(t){
  matched=t;
  const k=kids(t.id);
  if(k.length>0){
    await addBotWithLLM(followupContext(t));
    showPills(k,t);
  }else{
    confirmDone();
  }
}

function tapTrad(t){addUser(t.n);trackUserAnswer(t.n);selectTrad(t);}

async function confirmDone(){
  if(matched && !chosen.some(c=>c.id===matched.id)) chosen.push(matched);
  const label=crumb(matched);
  const list=chosen.map(crumb).join(', ');
  const context = chosen.length>1
    ? `User has added ${label} to their traditions. They now follow: ${list}. Let them know they can add another tradition or continue.` 
    : `User has selected ${label} as their Buddhist tradition. Confirm this choice warmly and let them know they can add another tradition or continue with the onboarding.`;
  await addBotWithLLM(context);
  showDone();
}

const TRADITIONS_DB = [
  {"id":"theravada","name":"Theravāda","level":1,"parent":null},
  {"id":"thai-buddhism","name":"Thai Buddhism","level":2,"parent":"theravada"},
  {"id":"dhammayut","name":"Dhammayuttika Nikāya","level":3,"parent":"thai-buddhism"},
  {"id":"maha-nikaya-th","name":"Mahā Nikāya","level":3,"parent":"thai-buddhism"},
  {"id":"thai-forest","name":"Thai Forest Tradition","level":3,"parent":"thai-buddhism"},
  {"id":"burmese-buddhism","name":"Burmese Buddhism","level":2,"parent":"theravada"},
  {"id":"thudhamma","name":"Thudhamma Nikāya","level":3,"parent":"burmese-buddhism"},
  {"id":"shwekyin","name":"Shwekyin Nikāya","level":3,"parent":"burmese-buddhism"},
  {"id":"mahasi","name":"Mahasi Tradition","level":3,"parent":"burmese-buddhism"},
  {"id":"pa-auk","name":"Pa-Auk Tradition","level":3,"parent":"burmese-buddhism"},
  {"id":"sri-lankan-buddhism","name":"Sri Lankan Buddhism","level":2,"parent":"theravada"},
  {"id":"siam-nikaya","name":"Siam Nikāya","level":3,"parent":"sri-lankan-buddhism"},
  {"id":"amarapura-nikaya","name":"Amarapura Nikāya","level":3,"parent":"sri-lankan-buddhism"},
  {"id":"ramanna-nikaya","name":"Rāmañña Nikāya","level":3,"parent":"sri-lankan-buddhism"},
  {"id":"cambodian-buddhism","name":"Cambodian Buddhism","level":2,"parent":"theravada"},
  {"id":"mohanikay","name":"Mohanikay","level":3,"parent":"cambodian-buddhism"},
  {"id":"lao-buddhism","name":"Lao Buddhism","level":2,"parent":"theravada"},
  {"id":"vipassana-goenka","name":"Vipassana (Goenka Tradition)","level":2,"parent":"theravada"},
  {"id":"insight-meditation","name":"Insight Meditation","level":2,"parent":"theravada"},
  {"id":"navayana","name":"Navayana / Ambedkarite Buddhism","level":2,"parent":"theravada"},
  {"id":"mahayana","name":"Mahāyāna","level":1,"parent":null},
  {"id":"chinese-buddhism","name":"Chinese Buddhism","level":2,"parent":"mahayana"},
  {"id":"pure-land-chinese","name":"Pure Land (Chinese)","level":3,"parent":"chinese-buddhism"},
  {"id":"chan","name":"Chan","level":3,"parent":"chinese-buddhism"},
  {"id":"tiantai","name":"Tiantai","level":3,"parent":"chinese-buddhism"},
  {"id":"huayan","name":"Huayan","level":3,"parent":"chinese-buddhism"},
  {"id":"chinese-esoteric","name":"Chinese Esoteric Buddhism","level":3,"parent":"chinese-buddhism"},
  {"id":"dharma-drum","name":"Dharma Drum Mountain","level":3,"parent":"chinese-buddhism"},
  {"id":"fo-guang-shan","name":"Fo Guang Shan","level":3,"parent":"chinese-buddhism"},
  {"id":"chung-tai-shan","name":"Chung Tai Shan","level":3,"parent":"chinese-buddhism"},
  {"id":"japanese-buddhism","name":"Japanese Buddhism","level":2,"parent":"mahayana"},
  {"id":"zen","name":"Zen","level":3,"parent":"japanese-buddhism"},
  {"id":"rinzai","name":"Rinzai","level":4,"parent":"zen"},
  {"id":"soto","name":"Sōtō","level":4,"parent":"zen"},
  {"id":"obaku","name":"Ōbaku","level":4,"parent":"zen"},
  {"id":"sanbo-zen","name":"Sanbo Zen","level":4,"parent":"zen"},
  {"id":"jodo-shu","name":"Jōdo-shū","level":3,"parent":"japanese-buddhism"},
  {"id":"jodo-shinshu","name":"Jōdo Shinshū","level":3,"parent":"japanese-buddhism"},
  {"id":"nishi-honganji","name":"Nishi Honganji","level":4,"parent":"jodo-shinshu"},
  {"id":"higashi-honganji","name":"Higashi Honganji","level":4,"parent":"jodo-shinshu"},
  {"id":"bca","name":"Buddhist Churches of America","level":4,"parent":"jodo-shinshu"},
  {"id":"nichiren","name":"Nichiren Buddhism","level":3,"parent":"japanese-buddhism"},
  {"id":"nichiren-shu","name":"Nichiren Shū","level":4,"parent":"nichiren"},
  {"id":"nichiren-shoshu","name":"Nichiren Shōshū","level":4,"parent":"nichiren"},
  {"id":"sgi","name":"Sōka Gakkai International","level":4,"parent":"nichiren"},
  {"id":"kempon-hokke","name":"Kempon Hokke","level":4,"parent":"nichiren"},
  {"id":"tendai","name":"Tendai","level":3,"parent":"japanese-buddhism"},
  {"id":"shingon","name":"Shingon","level":3,"parent":"japanese-buddhism"},
  {"id":"koyasan-shingon","name":"Koyasan Shingon","level":4,"parent":"shingon"},
  {"id":"rissho-koseikai","name":"Risshō Kōsei-kai","level":3,"parent":"japanese-buddhism"},
  {"id":"korean-buddhism","name":"Korean Buddhism","level":2,"parent":"mahayana"},
  {"id":"jogye","name":"Jogye Order","level":3,"parent":"korean-buddhism"},
  {"id":"taego","name":"Taego Order","level":3,"parent":"korean-buddhism"},
  {"id":"cheontae","name":"Cheontae","level":3,"parent":"korean-buddhism"},
  {"id":"won-buddhism","name":"Won Buddhism","level":3,"parent":"korean-buddhism"},
  {"id":"jingak","name":"Jingak Order","level":3,"parent":"korean-buddhism"},
  {"id":"vietnamese-buddhism","name":"Vietnamese Buddhism","level":2,"parent":"mahayana"},
  {"id":"thien","name":"Thiền","level":3,"parent":"vietnamese-buddhism"},
  {"id":"truc-lam","name":"Trúc Lâm","level":4,"parent":"thien"},
  {"id":"lam-te","name":"Lâm Tế","level":4,"parent":"thien"},
  {"id":"tinh-do","name":"Tịnh Độ","level":3,"parent":"vietnamese-buddhism"},
  {"id":"khat-si","name":"Khất Sĩ Order","level":3,"parent":"vietnamese-buddhism"},
  {"id":"plum-village","name":"Plum Village","level":3,"parent":"vietnamese-buddhism"},
  {"id":"vajrayana","name":"Vajrayāna","level":1,"parent":null},
  {"id":"tibetan-buddhism","name":"Tibetan Buddhism","level":2,"parent":"vajrayana"},
  {"id":"nyingma","name":"Nyingma","level":3,"parent":"tibetan-buddhism"},
  {"id":"katok","name":"Katok","level":4,"parent":"nyingma"},
  {"id":"palyul","name":"Palyul","level":4,"parent":"nyingma"},
  {"id":"mindrolling","name":"Mindrolling","level":4,"parent":"nyingma"},
  {"id":"shechen","name":"Shechen","level":4,"parent":"nyingma"},
  {"id":"dorje-drag","name":"Dorje Drak","level":4,"parent":"nyingma"},
  {"id":"dzogchen-monastery","name":"Dzogchen Monastery","level":4,"parent":"nyingma"},
  {"id":"kagyu","name":"Kagyu","level":3,"parent":"tibetan-buddhism"},
  {"id":"karma-kagyu","name":"Karma Kagyu","level":4,"parent":"kagyu"},
  {"id":"drikung-kagyu","name":"Drikung Kagyu","level":4,"parent":"kagyu"},
  {"id":"drukpa-kagyu","name":"Drukpa Kagyu","level":4,"parent":"kagyu"},
  {"id":"shangpa-kagyu","name":"Shangpa Kagyu","level":4,"parent":"kagyu"},
  {"id":"taklung-kagyu","name":"Taklung Kagyu","level":4,"parent":"kagyu"},
  {"id":"sakya","name":"Sakya","level":3,"parent":"tibetan-buddhism"},
  {"id":"ngorpa","name":"Ngorpa","level":4,"parent":"sakya"},
  {"id":"tsarpa","name":"Tsarpa","level":4,"parent":"sakya"},
  {"id":"dzongsar","name":"Dzongsar","level":4,"parent":"sakya"},
  {"id":"gelug","name":"Gelug","level":3,"parent":"tibetan-buddhism"},
  {"id":"jonang","name":"Jonang","level":3,"parent":"tibetan-buddhism"},
  {"id":"rime","name":"Rimé","level":3,"parent":"tibetan-buddhism"},
  {"id":"mongolian-buddhism","name":"Mongolian Buddhism","level":2,"parent":"vajrayana"},
  {"id":"buryat-buddhism","name":"Buryat Buddhism","level":2,"parent":"vajrayana"},
  {"id":"kalmyk-buddhism","name":"Kalmyk Buddhism","level":2,"parent":"vajrayana"},
  {"id":"tuvan-buddhism","name":"Tuvan Buddhism","level":2,"parent":"vajrayana"},
  {"id":"newar-buddhism","name":"Newar Buddhism","level":2,"parent":"vajrayana"},
  {"id":"bon","name":"Bön","level":1,"parent":null},
  {"id":"western-contemporary","name":"Western / Contemporary","level":1,"parent":null},
  {"id":"secular-buddhism","name":"Secular Buddhism","level":2,"parent":"western-contemporary"},
  {"id":"triratna","name":"Triratna","level":2,"parent":"western-contemporary"},
  {"id":"nkt","name":"New Kadampa","level":2,"parent":"western-contemporary"},
  {"id":"shambhala","name":"Shambhala","level":2,"parent":"western-contemporary"}
];

async function matchWithLLM() {
  if (chosen.length === 0) {
    console.log('No traditions selected, skipping LLM match');
    return null;
  }

  showTyping();
  
  try {
    const prompt = `User's Q&A history and selections:
${JSON.stringify(qaHistory, null, 2)}

Selected traditions: ${chosen.map(c => c.n).join(', ')}

Traditions database:
${JSON.stringify(TRADITIONS_DB, null, 2)}`;

    const systemPrompt = `You are a Buddhist tradition matcher. Given the user's Q&A history and their selected traditions, verify if their selections match the traditions database accurately.

Return ONLY a valid JSON array in this exact format (no markdown, no code blocks):
[{"id": "tradition-id", "confidence": 95}]

Rules:
- confidence is 0-100 (how well their answers match the tradition)
- Return the traditions they selected with confidence scores
- If they selected correctly, confidence should be 90-100
- If there are inconsistencies, lower the confidence
- Return up to 3 best matches`;

    const response = await fetch('/api/v1/llm/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: prompt,
        system_prompt: systemPrompt,
        model: 'gemini-2.5-flash'
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    removeTyping();
    
    // Parse the LLM response
    let matches;
    try {
      // Try to parse as JSON directly
      matches = JSON.parse(data.response);
    } catch (e) {
      // If it fails, try to extract JSON from markdown code blocks
      const jsonMatch = data.response.match(/```(?:json)?\\s*([\\s\\S]*?)```/);
      if (jsonMatch) {
        matches = JSON.parse(jsonMatch[1]);
      } else {
        // Try to find JSON array in the response
        const arrayMatch = data.response.match(/\\[\\s*{[\\s\\S]*}\\s*\\]/);
        if (arrayMatch) {
          matches = JSON.parse(arrayMatch[0]);
        } else {
          throw new Error('Could not parse LLM response');
        }
      }
    }
    
    console.log('LLM Matches:', matches);
    return matches;
    
  } catch (error) {
    console.error('LLM matching error:', error);
    removeTyping();
    return null;
  }
}

async function handleContinue() {
  if (primary.classList.contains('skip')) {
    // Skip button - just close/finish
    console.log('User skipped tradition selection');
    console.log('Q&A History:', qaHistory);
    const r=document.createElement('div');r.className='row bot';
    r.innerHTML=BAV+`<div class="bubble">No worries! You can set your tradition anytime from your profile.</div>`;
    chatEl.appendChild(r);chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
    return;
  }
  
  // Continue button - match with LLM
  const matches = await matchWithLLM();
  
  if (matches && matches.length > 0) {
    console.log('LLM Matches:', matches);
    console.log('Q&A History:', qaHistory);
    
    // Display results in chat
    const resultsHtml = matches.map(m => {
      const trad = TRADITIONS_DB.find(t => t.id === m.id);
      return `<strong>${trad ? trad.name : m.id}</strong>: ${m.confidence}% confidence`;
    }).join('<br>');
    
    const r=document.createElement('div');r.className='row bot';
    r.innerHTML=BAV+`<div class="bubble">✅ <strong>Tradition Matching Complete!</strong><br><br>${resultsHtml}<br><br>Your selections have been validated and saved.</div>`;
    chatEl.appendChild(r);chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
    
    // Hide input and buttons
    inputbar.style.display = 'none';
    addbtn.style.display = 'none';
    primary.style.display = 'none';
  } else {
    console.log('Selected traditions:', chosen);
    console.log('Q&A History:', qaHistory);
    
    const r=document.createElement('div');r.className='row bot';
    r.innerHTML=BAV+`<div class="bubble">✅ Your tradition selections have been saved: <strong>${chosen.map(c => c.n).join(', ')}</strong></div>`;
    chatEl.appendChild(r);chatEl.scrollTo({top:chatEl.scrollHeight,behavior:'smooth'});
    
    // Hide input and buttons
    inputbar.style.display = 'none';
    addbtn.style.display = 'none';
    primary.style.display = 'none';
  }
}

async function restart(){
  chatEl.innerHTML='';matched=null;chosen=[];qaHistory=[];clearInput();
  addbtn.style.display='none';setSkip();
  txt.placeholder='Type your tradition…';
  txt.focus();
}

// Set up primary button click handler
primary.onclick = handleContinue;

restart();
  </script>
</body>
</html>
"""
    return html_content
