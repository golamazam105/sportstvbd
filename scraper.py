import requests
import json
import re
import asyncio
import aiohttp

# ১. বিশ্বস্ত ও আপডেটেড সোর্স (যেখানে Sony, Star, Sports চ্যানেল আছে)
sources = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/bd.m3u", # বাংলাদেশ
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/in.m3u", # ইন্ডিয়া
    "https://raw.githubusercontent.com/ttoorruu/Bangladesh-IPTV/main/bd.m3u"  # স্পেশাল বিডি ও ভারতীয় সোর্স
]

# 🏷️ চ্যানেলের নাম দেখে নিখুঁতভাবে ক্যাটাগরি নির্ধারণ করার ফাংশন
def detect_category(channel_name):
    name_lower = channel_name.lower()
    
    # ১. স্পোর্টস ক্যাটাগরি (সবচেয়ে আগে স্পোর্টস কি-ওয়ার্ড চেক হবে)
    if any(k in name_lower for k in ['sports', 'sony ten', 'star sports', 't sports', 'cricket', 'football', 'willow', 'tsports', 'ten hd']):
        return "Sports"
    
    # ২. নিউজ ক্যাটাগরি
    elif any(k in name_lower for k in ['news', 'somoy', 'jamuna', 'independent', 'ekattor', 'atn news', 'dbc', 'aaj tak', 'ndtv', 'wion', 'calcutta news', 'bharat24', 'live24', 'khabor']):
        return "News"
    
    # ৩. বিনোদন বা এন্টারটেইনমেন্ট (মুভি, সিরিয়াল, মিউজিক ইত্যাদি)
    elif any(k in name_lower for k in ['star plus', 'sony jalsa', 'zee', 'colors', 'entertainment', 'cinema', 'gold', 'anmol', 'dangal', '9x', 'tashan', 'jhakaas', 'shemaroo', 'b4u', 'music', 'bhojpuri', 'comedy']):
        return "Entertainment"
        
    # ৪. বাংলাদেশ ক্যাটাগরি (নিউজ বা স্পোর্টস বাদে বাকি সব বাংলাদেশি চ্যানেল)
    elif any(k in name_lower for k in ['btv', 'ekhon', 'mohona', 'desh tv', 'rtv', 'channel 24', 'boishakhi', 'deepto', 'duronto', 'ekushey', 'atn bangla', 'bangla vision', 'my tv', 'maasranga', 'ananda', 'bangla tv', 'sa tv', 'channel i', 'gazi tv', 'gtv', 'asian tv', 'bijoy', 'deshi tv', 'rongo']):
        return "Bangladesh"
        
    # ৫. ইন্ডিয়া ক্যাটাগরি (নিউজ, স্পোর্টস বা এন্টারটেইনমেন্ট বাদে বাকি ভারতীয় আঞ্চলিক/ধর্মীয় চ্যানেল)
    elif any(k in name_lower for k in ['aastha', 'punjab', 'shubh', 'delhi', 'tv9', 'polimer', 'sathiyam', 'prudent', 'telugu', 'salvation', 'kolkata', 'chardikla', 'arputhar', 'indywood', 'ccv', 'salaam', 'zainabia', 'ptc', 'etv', 'starnet', 'goodness', 'ctvn', 'isai', 'joy tv', 'vijay', 'roja', 'kannur', 'inh', 'malai', 'ayush', 'sanskar', 'nepal']):
        return "India"
        
    # কোনোটার সাথে না মিললে General ক্যাটাগরি
    else:
        return "General"

raw_channels = []

print("সোর্স থেকে চ্যানেল কালেক্ট করা হচ্ছে...")
for source in sources:
    try:
        response = requests.get(source, timeout=10)
        if response.status_code == 200:
            lines = response.text.split('\n')
            current_name = "Unknown Channel"
            
            for line in lines:
                if line.startswith("#EXTINF"):
                    # চ্যানেলের নাম খুঁজে বের করার রেগুলার এক্সপ্রেশন
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        current_name = name_match.group(1).strip()
                elif line.startswith("http"):
                    url = line.strip()
                    # নামের ওপর ভিত্তি করে ক্যাটাগরি অটো-ডিটেক্ট করা
                    category = detect_category(current_name)
                    raw_channels.append({"name": current_name, "url": url, "category": category})
    except Exception as e:
        print(f"Error loading source {source}: {e}")

# ডুপ্লিকেট ইউআরএল (URL) ফিল্টার করা
unique_channels = {ch['url']: ch for ch in raw_channels}.values()
print(f"মোট {len(unique_channels)}টি ইউনিক চ্যানেল পাওয়া গেছে। চেকিং শুরু হচ্ছে...")

valid_channels = []

# ২. সুপার ফাস্ট লিঙ্ক চেকার (Async Link Checker)
async def check_channel(session, channel):
    try:
        # HEAD রিকোয়েস্ট পাঠিয়ে শুধু লিঙ্কটি সচল (200 OK) কিনা চেক করা হচ্ছে
        async with session.head(channel['url'], timeout=3, allow_redirects=True) as response:
            if response.status == 200:
                valid_channels.append(channel)
    except:
        pass

async def main():
    # SSL ভেরিফিকেশন ইগনোর করা হচ্ছে যাতে কিছু লিঙ্কের সার্টিফিকেট এরর থাকলেও কানেক্ট হয়
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_channel(session, ch) for ch in unique_channels]
        await asyncio.gather(*tasks)

# এসিনক্রোনাস লুপ রান করা
asyncio.run(main())

print(f"চেকিং শেষ! সচল চ্যানেল পাওয়া গেছে: {len(valid_channels)}টি।")

# ৩. M3U ফাইল তৈরি করা
with open("live_tv.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in valid_channels:
        # M3U ফাইলে গ্রুপ-টাইটেল বা ক্যাটাগরি অ্যাড করা হচ্ছে
        f.write(f'#EXTINF:-1 group-title="{ch["category"]}",{ch["name"]}\n{ch["url"]}\n')

# ৪. ওয়েব অ্যাপ বা কোডুলারের জন্য JSON ফাইল তৈরি করা
with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(valid_channels, f, ensure_ascii=False, indent=4)

print("ফাইল সেভ কমপ্লিট! 'live_tv.m3u' এবং 'channels.json' সফলভাবে তৈরি হয়েছে।")
