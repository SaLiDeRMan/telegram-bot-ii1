from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ChatMemberHandler, filters, ContextTypes
import json
import os
import time
from datetime import datetime
from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
def fa(text):
    if not text:
        return ""
    return get_display(arabic_reshaper.reshape(str(text)))
def load_font(name, size):
    for p in [name, os.path.join(os.path.dirname(__file__), name)]:
        try:
            return ImageFont.truetype(p, size)
        except:
            pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

TOKEN = "8895372308:AAE-AuFZHeYjaOj3WyRNHbMa1KHwwR3C0aM"
DATA_FILE = "user_stats.json"
CREATOR = "@SaLiDeR_Man 👑"
BAD_WORDS = ["فحش1", "فحش2", "کثافت", "احمق"]
spam_tracker = {}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_stats = json.load(f)
else:
    user_stats = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_stats, f, ensure_ascii=False, indent=2)

def get_level(count):
    if count >= 500: return "اسطوره 👑"
    if count >= 100: return "حرفه‌ای ⭐"
    if count >= 10: return "فعال 🔥"
    return "تازه‌کار 🌱"

def get_rank(user_id):
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1].get("count", 0), reverse=True)
    for i, (uid, _) in enumerate(sorted_users):
        if uid == user_id: return i+1, len(sorted_users)
    return None, len(sorted_users)

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    user = update.effective_user
    uid = str(user.id)
    txt = update.message.text or ""
    now = time.time()
    if uid not in spam_tracker: spam_tracker[uid] = []
    spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 10]
    spam_tracker[uid].append(now)
    if len(spam_tracker[uid]) > 5:
        try:
            await update.message.delete()
            await update.message.reply_text(f"⚠️ {user.first_name} عزیز! لطفاً اسپم نکن 🙏🛡️")
            spam_tracker[uid] = []
            return
        except: pass
    for w in BAD_WORDS:
        if w in txt:
            try:
                await update.message.delete()
                await update.message.reply_text(f"🚫 {user.first_name}! این حرف زشت رو نزن! 🛡️")
                return
            except: pass
            break
    if uid not in user_stats:
        user_stats[uid] = {"name": user.full_name, "username": user.username, "count": 0, "last_message": "", "week_count": 0}
    user_stats[uid]["count"] += 1
    user_stats[uid]["week_count"] = user_stats[uid].get("week_count", 0) + 1
    user_stats[uid]["last_message"] = txt
    user_stats[uid]["name"] = user.full_name
    user_stats[uid]["username"] = user.username
    save_data()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 سلام رفیق! من ربات آمار گروهتم 🤖✨\n👑 ساخته شده توسط {CREATOR}\n\n📌 دستورات:\n📊 /stats - آمار + لِوِل + رتبه\n🎮 /levels - سطوح لِوِل‌بندی\n👥 /members - تعداد اعضا\n🏆 /top - تاپ ۱۰\n📋 /list - لیست کاربرا\n📁 /export - اکسل\n🖼️ /me - پروفایل تصویری\n📅 /weekly - گزارش هفتگی")

async def levels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    my_count = user_stats.get(uid, {}).get("count", 0)
    my_level = get_level(my_count)
    text = (
        "🎮 سیستم لِوِل‌بندی گروه 🏆\n\n"
        "معیار لِوِل = تعداد کل پیام‌هایی که فرستادی 💬\n\n"
        "🌱 تازه‌کار: 0 تا 9 پیام\n"
        "🔥 فعال: 10 تا 99 پیام\n"
        "⭐ حرفه‌ای: 100 تا 499 پیام\n"
        "👑 اسطوره: 500 پیام به بالا\n\n"
        f"📊 وضعیت تو: {my_count} پیام\n"
        f"🎮 لِوِل تو: {my_level} ✅\n\n"
        "💪 بیشتر پیام بده، لِوِل‌آپ شو! 🔥\n"
        f"👑 سازنده: {CREATOR}"
    )
    await update.message.reply_text(text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in user_stats:
        await update.message.reply_text("😅 هنوز پیامی ازت ثبت نشده!")
        return
    s = user_stats[uid]
    level = get_level(s['count'])
    rank, total_u = get_rank(uid)
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1].get("count", 0), reverse=True)
    if rank > 1:
        above_count = sorted_users[rank-2][1]['count']
        diff = above_count - s['count'] + 1
        next_msg = f"\n🎯 {diff} پیام دیگه بده میشی نفر {rank-1}! 🔥"
    else:
        next_msg = "\n👑 تو نفر اولی! سلطان! 🔥"
    await update.message.reply_text(f"📊 آمار تو:\n\n👤 {s['name']}\n💬 پیام‌ها: {s['count']}\n🎮 لِوِل: {level}\n📈 رتبه: نفر {rank} از {total_u} نفر{next_msg}\n📝 آخرین پیام: {s['last_message']}\n\n👑 سازنده: {CREATOR}")

async def members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        c = await context.bot.get_chat_member_count(update.effective_chat.id)
        await update.message.reply_text(f"👥 اعضای گروه: {c} نفر 🎉\n👑 سازنده ربات: {CREATOR}")
    except:
        await update.message.reply_text("⚠️ منو ادمین کن 🙏")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_stats:
        await update.message.reply_text("📭 دیتایی نیست!")
        return
    su = sorted(user_stats.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:10]
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    t = "🏆 تاپ ۱۰ گروه:\n\n"
    for i,(uid,d) in enumerate(su):
        u = f"@{d['username']}" if d.get('username') else d.get('name')
        t += f"{medals[i]} {u} - {d['count']} پیام | {get_level(d['count'])}\n"
    t += f"\n🔥 دمتون گرم! ❤️\n👑 سازنده: {CREATOR}"
    await update.message.reply_text(t)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_stats:
        await update.message.reply_text("📭 کاربری نیست!")
        return
    try: total = await context.bot.get_chat_member_count(update.effective_chat.id)
    except: total = len(user_stats)
    t = f"📋 لیست:\n👥 کل: {total} | 👀 رصد: {len(user_stats)}\n\n"
    i=1
    for uid,d in user_stats.items():
        u = f"{d.get('name')}, @{d.get('username')}" if d.get('username') else f"{d.get('name')}, ID:{uid}"
        t += f"{i}-{u}\n"
        i+=1
        if len(t)>3500:
            await update.message.reply_text(t); t=""
    if t: await update.message.reply_text(t + f"\n👑 سازنده: {CREATOR}")

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_stats:
        await update.message.reply_text("📭 دیتایی نیست!")
        return
    await update.message.reply_text("⏳ دارم آماده می‌کنم... 📁")
    fn="export.xlsx"; wb=Workbook(); ws=wb.active; ws.title="Users"
    ws.append(["ID","Name","Username","Count","Level","Last Message"])
    su=sorted(user_stats.items(), key=lambda x: x[1].get("count",0), reverse=True)
    for uid,d in su:
        ws.append([uid,d.get("name",""),d.get("username",""),d.get("count",0),get_level(d.get("count",0)),d.get("last_message","")])
    wb.save(fn)
    await update.message.reply_document(open(fn,"rb"), filename=fn, caption=f"📁 آماده‌ست! 🎉 {len(user_stats)} کاربر ✅\n👑 سازنده: {CREATOR}")
    os.remove(fn)

async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in user_stats:
        await update.message.reply_text("😅 اول یه پیام بده!")
        return
    s = user_stats[uid]
    my_count = s.get("count", 0)
    my_level = get_level(my_count)
    rank, total_u = get_rank(uid)
    level_en = my_level.replace("👑","").replace("⭐","").replace("🔥","").replace("🌱","").strip()
    avatar_img = None
    try:
        photos = await context.bot.get_user_profile_photos(update.effective_user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            tg_file = await context.bot.get_file(file_id)
            await tg_file.download_to_drive("avatar.jpg")
            avatar_img = Image.open("avatar.jpg").convert("RGB")
    except:
        avatar_img = None
    W, H = 700, 500
    img = Image.new('RGB', (W, H), (18, 18, 35))
    d = ImageDraw.Draw(img, 'RGBA')
    for y in range(H):
        r = int(18 + y * 0.12)
        g = int(18 + y * 0.05)
        b = int(55 + y * 0.08)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    d.rectangle([0, 0, W, 110], fill=(124, 58, 237))
    d.rectangle([0, 110, W, 116], fill=(250, 204, 21))
    f_big = load_font("Vazirmatn-Bold.ttf", 38)
    f_med = load_font("Vazirmatn-Regular.ttf", 26)
    f_small = load_font("Vazirmatn-Regular.ttf", 22)
    d.text((40, 28), "GROUP PROFILE", font=f_big, fill=(255,255,255))
    d.text((40, 68), "Season Stats Card", font=f_small, fill=(255,235,150))
    ax, ay, asize = 40, 145, 110
    d.ellipse([ax-5, ay-5, ax+asize+5, ay+asize+5], fill=(250,204,21))
    if avatar_img:
        avatar_img = avatar_img.resize((asize, asize))
        mask = Image.new('L', (asize, asize), 0)
        ImageDraw.Draw(mask).ellipse((0,0,asize,asize), fill=255)
        img.paste(avatar_img, (ax, ay), mask)
    else:
        d.ellipse([ax, ay, ax+asize, ay+asize], fill=(60,60,90))
        first_char = (s.get('name','U') or 'U')[0]
        d.text((ax+35, ay+25), fa(first_char), font=f_big, fill=(255,255,255))
    d.text((170, 165), fa(s.get('name','User')), font=f_med, fill=(255,255,255), anchor="ra")
    uname = f"@{s.get('username','no_username')}" if s.get('username') else f"ID:{uid}"
    d.text((170, 200), fa(uname), font=f_small, fill=(180,180,200), anchor="ra")
    cards = [("MESSAGES", str(my_count)), ("LEVEL", fa(level_en)), ("RANK", f"#{rank} / {total_u}")]
    x = 30
    for title, val in cards:
        d.rounded_rectangle([x, 280, x+200, 385], radius=18, fill=(255,255,255), outline=(250,204,21), width=3)
        d.text((x+20, 295), title, font=f_small, fill=(120,50,180))
        d.text((x+20, 327), val, font=f_med, fill=(20,20,20))
        x += 215
    d.text((40, 410), fa("Last message:"), font=f_small, fill=(180,180,200))
    last = fa((s.get("last_message","") or "")[:55])
    d.text((40, 435), last, font=f_med, fill=(255,255,255), anchor="ra")
    d.text((40, 465), "Creator: SaLiDeR_Man", font=f_small, fill=(250,204,21))
    img.save("profile.png")
    caption = f"🖼️ پروفایل تو {s.get('name')} جان! 😍\n💬 {my_count} پیام | 🎮 {my_level} | 📈 رتبه #{rank}\n👑 سازنده: @SaLiDeR_Man"
    await update.message.reply_photo(open("profile.png","rb"), caption=caption)
    os.remove("profile.png")
    if os.path.exists("avatar.jpg"):
        os.remove("avatar.jpg")

async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: total = await context.bot.get_chat_member_count(update.effective_chat.id)
    except: total="?"
    week_total=sum([v.get("week_count",0) for v in user_stats.values()])
    su=sorted(user_stats.items(), key=lambda x: x[1].get("week_count",0), reverse=True)
    top3=su[:3]
    t=f"📊 گزارش هفتگی گروه 🎉\n📅 {datetime.now().strftime('%Y-%m-%d')}\n\n👥 اعضا: {total} نفر\n💬 پیام این هفته: {week_total} تا\n\n🏆 برترین‌های هفته:\n"
    medals=["🥇","🥈","🥉"]
    for i,(uid,d) in enumerate(top3):
        u=f"@{d['username']}" if d.get('username') else d.get('name')
        t+=f"{medals[i]} {u} با {d.get('week_count',0)} پیام\n"
    t+=f"\n🔥 هفته بعد بترکونید! ❤️\n👑 سازنده: {CREATOR}"
    await update.message.reply_text(t)

async def on_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    old=update.chat_member.old_chat_member.status
    new=update.chat_member.new_chat_member.status
    m=update.chat_member.new_chat_member.user
    if old in ["left","kicked"] and new in ["member","administrator"]:
        try:
            await context.bot.send_message(update.chat_member.chat.id, f"🎉 خوش اومدی {m.mention_html()}! ❤️\nبزن /start 🤖✨\n👑 ساخته شده توسط {CREATOR}", parse_mode="HTML")
        except: pass

async def setup_commands(app: Application):
    from telegram import BotCommand
    await app.bot.set_my_commands([
        BotCommand("start","🎉 شروع"),
        BotCommand("stats","📊 آمار + لِوِل"),
        BotCommand("levels","🎮 سطوح و لِوِل‌ها"),
        BotCommand("top","🏆 تاپ ۱۰"),
        BotCommand("list","📋 لیست"),
        BotCommand("export","📁 اکسل"),
        BotCommand("me","🖼️ پروفایل تصویری"),
        BotCommand("weekly","📅 گزارش هفتگی"),
        BotCommand("members","👥 اعضا"),
    ])

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start_command))
    app.add_handler(CommandHandler("stats",stats_command))
    app.add_handler(CommandHandler("levels",levels_command))
    app.add_handler(CommandHandler("members",members_command))
    app.add_handler(CommandHandler("top",top_command))
    app.add_handler(CommandHandler("list",list_command))
    app.add_handler(CommandHandler("export",export_command))
    app.add_handler(CommandHandler("me",me_command))
    app.add_handler(CommandHandler("weekly",weekly_command))
    app.add_handler(MessageHandler(filters.ALL,on_message))
    app.add_handler(ChatMemberHandler(on_member_update,ChatMemberHandler.CHAT_MEMBER))
    app.post_init=setup_commands
    print("🤖 ربات غول روشن شد ✅")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
    main()