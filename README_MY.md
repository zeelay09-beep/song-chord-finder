# Song Chord Finder — Deployable Web App

ဒီ package က Web UI နဲ့ AI backend ကို server တစ်ခုတည်းမှာ run လုပ်နိုင်အောင် ပြင်ဆင်ထားပါတယ်။ Public website ကို ဒီနေရာကနေ တိုက်ရိုက် publish မလုပ်နိုင်ပါ။ Hosting account မှာ deploy လုပ်ရပါမယ်။

## လုပ်ဆောင်ချက်များ
- MP3/WAV/M4A/FLAC/OGG upload (40 MB အထိ)
- Key, tempo, intro chord နဲ့ chord changes ခန့်မှန်းခြင်း
- Whisper model ဖြင့် အသံမှ စာသားဖော်ထုတ်ရန် ကြိုးစားခြင်း
- Browser မှ Print → Save as PDF

## အွန်လိုင်းတင်နည်း (Render)
1. ZIP ကို ဖြည်ပါ။
2. Folder အတွင်းရှိဖိုင်အားလုံးကို GitHub repository အသစ်တစ်ခုထဲ upload လုပ်ပါ။
3. Render.com မှာ account ဝင်ပြီး **New + → Blueprint** ကိုရွေးပါ။
4. GitHub repository ကို ချိတ်ပါ။ `render.yaml` ကိုဖတ်ပြီး service တည်ဆောက်ပါ။
5. Deploy ပြီးလျှင် Render ကပေးသော `https://...onrender.com` URL ကိုဖွင့်ပါ။
6. URL နောက်မှာ `/health` ထည့်ဖွင့်ပြီး `ok: true` ပြန်လာမလာ စစ်ပါ။

## သတိပြုရန်
- ဒီ chat ကနေ public website ကို တိုက်ရိုက် publish မလုပ်ထားပါ။
- Free hosting သည် အိပ်ပျော်သွားနိုင်ပြီး ပထမဆုံး run မှာ AI model download ကြောင့် ကြာနိုင်သည်။
- Free plan ရဲ့ RAM/CPU ကန့်သတ်ချက်ကြောင့် သီချင်းရှည်/ဖိုင်ကြီးတွေမှာ အလုပ်မလုပ်နိုင်တာရှိနိုင်ပါတယ်။
- `tiny` Whisper model သည် memory ပိုသက်သာသော်လည်း မြန်မာစာ transcription အရည်အသွေး အာမခံမရပါ။
- Key/Chord detection သည် ခန့်မှန်းချက်သာဖြစ်သည်။ နားထောင်ပြီး စစ်ဆေးပါ။
- Public အသုံးပြုမှုမတိုင်မီ login/rate limit နှင့် upload abuse ကာကွယ်မှု ထပ်ထည့်ရန်လိုသည်။
- PDF ထုတ်ရန် browser print dialog တွင် **Save as PDF** ရွေးပါ။ မြန်မာစာပုံစံသည် device/browser font ပေါ် မူတည်နိုင်ပါတယ်။
