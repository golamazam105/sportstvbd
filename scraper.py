import requests
import json
import re
import asyncio
import aiohttp

# ১. বিশ্বস্ত ও আপডেটেড সোর্স (যেখানে Sony, Star, Sports চ্যানেল আছে)
sources = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/bd.m3u", # বাংলাদেশ
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/in.m3u", # ইন্ডিয়া
    "https://raw.githubusercontent.com/ttoorruu/Bangladesh-IPTV/main/bd.m3u" # স্পেশাল বিডি ও ভারতীয় চ্যানেল সোর্স
]

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
                    name_match = re.search(r',([^,]+)$', line)
                    if name_match:
                        current_name = name_match.group(1).strip()
                elif line.startswith("http"):
                    url = line.strip()
                    raw_channels.append({"name": current_name, "url": url})
    except Exception as e:
        print(f"Error loading source {source}: {e}")

# ডুপ্লিকেট চ্যানেল বাদ দেওয়া
unique_channels = {ch['url']: ch for ch in raw_channels}.values()
print(f"মোট {len(unique_channels)}টি ইউনিক চ্যানেল পাওয়া গেছে। চেকিং শুরু হচ্ছে...")

valid_channels = []

# ২. সুপার ফাস্ট লিঙ্ক চেকার (Async Link Checker)
async def check_channel(session, channel):
    try:
        async with session.head(channel['url'], timeout=3, allow_redirects=True) as response:
            if response.status == 200:
                valid_channels.append(channel)
    except:
        pass

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [check_channel(session, ch) for ch in unique_channels]
        await asyncio.gather(*tasks)

# রান করা হচ্ছে
asyncio.run(main())

print(f"চেকিং শেষ! সচল চ্যানেল পাওয়া গেছে: {len(valid_channels)}টি।")

# ৩. M3U ফাইল তৈরি করা
with open("live_tv.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in valid_channels:
        f.write(f"#EXTINF:-1,{ch['name']}\n{ch['url']}\n")

# ৪. কোডুলারের জন্য JSON ফাইল তৈরি করা
with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(valid_channels, f, ensure_ascii=False, indent=4)

print("ফাইল সেভ কমপ্লিট!")
