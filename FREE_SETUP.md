# J.A.R.V.I.S. Web - FREE Features Setup

**100% Free - No Paid APIs Required!**

## Free API Setup (5 minutes)

### 1. Groq API (Chat - FREE)
- Go to [console.groq.com/keys](https://console.groq.com/keys)
- Sign up with Google/GitHub
- Create API key
- Copy key

### 2. HuggingFace API (Image Generation - FREE)
- Go to [huggingface.co](https://huggingface.co)
- Sign up (free account)
- Go to [Settings → Access Tokens](https://huggingface.co/settings/tokens)
- Create "Fine-grained token" with "Inference API" permission
- Copy token

### 3. Deploy on Render

#### Environment Variables:
```
GROQ_API_KEY=your_groq_key_here
HF_API_KEY=your_huggingface_token_here
CORS_ORIGINS=*
```

#### Features (ALL FREE):
- 💬 **Chat** - Using Groq Mixtral (fastest free LLM)
- 🎤 **Voice** - Browser Web Speech API (built-in, 100% free)
- 🎨 **Image** - HuggingFace Stable Diffusion (free tier)
- 🌍 **Globe** - Three.js (open-source, free)
- ♟ **Chess** - Pure JavaScript engine (no backend needed)

## Features in Detail

| Feature | Free API | Rate Limit | Notes |
|---------|----------|-----------|-------|
| Chat | Groq Mixtral | 30 req/min | Super fast |
| Images | HF Inference | 15 req/min | Stable Diffusion |
| Voice Input | Web Speech API | Unlimited | Browser built-in |
| 3D Globe | Three.js | Unlimited | Client-side only |
| Chess | js-chess | Unlimited | Local AI engine |

## No Credit Card Needed!
- ✅ Groq: Free tier (sign-up only)
- ✅ HuggingFace: Free tier (no card)
- ✅ Web Speech: Built-in browser API
- ✅ Three.js: Open-source library
- ✅ Chess engine: JavaScript library

## Get Started
1. Create Groq key
2. Create HuggingFace token
3. Add to Render environment
4. Deploy
5. Use on phone/desktop/tablet with public URL

No bills. Ever.
