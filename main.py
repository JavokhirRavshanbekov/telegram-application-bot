from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import random

TOKEN = '8395197694:AAFGHxHuJpiabKg8k5K4udJ63PfhTZUJCgQ'
ADMIN_ID = 6136127418

# Savollar ro'yxati
questions = [
    "Ismingizni kiriting:",
    "Tug‘ilgan yilingizni yozing (masalan: 2005):",
    "Telefon raqamingizni yozing (masalan: 998901234567):",
    "Sohangizni tanlang:",
    "To‘liq manzilingizni kiriting:",
    "Millatingizni tanlang:",
    "Ma'lumotingizni tanlang:",
    "Oilaviy holatingizni tanlang:",
    "Tajribangiz haqida yozing:",
    "Oldingi ish joyingizni yozing:",
    "Qancha maoshga ishlamoqchisiz?",
    "Qancha vaqt ishlamoqchisiz?",
    "Sudlanganmisiz?",
    "Telegram username'ingizni kiriting (masalan: @sehat):",
    "Qayerdan eshitdingiz (masalan: Reklama, do‘st, internet...)?",
    "Iltimos, rasmingizni yuboring:"
]

# Variantli tugmalar
variant_keyboards = {
    3: ReplyKeyboardMarkup([["Farrosh", "Hamshira"], ["Jarrox", "Oshpaz"]], resize_keyboard=True),
    5: ReplyKeyboardMarkup([["O'zbek", "Rus"], ["Boshqa millat"]], resize_keyboard=True),
    6: ReplyKeyboardMarkup([["Oliy", "O‘rta"], ["Boshlang‘ich", "O‘qiyapman"]], resize_keyboard=True),
    7: ReplyKeyboardMarkup([["Oilali", "Ajrashgan", "Yolg‘iz"]], resize_keyboard=True),
    12: ReplyKeyboardMarkup([["Ha", "Yo‘q"]], resize_keyboard=True),
}

PHOTO_STATE = 15

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = 0
    await update.message.reply_text("Assalomu alaykum! Ro‘yxatdan o‘tish uchun kerakli ma’lumotlarni yuboring.")
    await ask_question(update, context)
    return 1


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data["step"]
    if step in variant_keyboards:
        await update.message.reply_text(questions[step], reply_markup=variant_keyboards[step])
    elif step == PHOTO_STATE:
        await update.message.reply_text(questions[step], reply_markup=ReplyKeyboardRemove())
        return PHOTO_STATE
    else:
        await update.message.reply_text(questions[step], reply_markup=ReplyKeyboardRemove())


async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data["step"]
    context.user_data[f"answer_{step}"] = update.message.text
    context.user_data["step"] += 1

    if context.user_data["step"] == PHOTO_STATE:
        await ask_question(update, context)
        return PHOTO_STATE
    elif context.user_data["step"] >= len(questions):
        return await finish(update, context)
    else:
        await ask_question(update, context)
        return 1


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo"] = update.message.photo[-1].file_id
    return await finish(update, context)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    anketa_id = f"#{random.randint(10000, 99999)}"
    username = data.get("answer_13", "@no_username")
    photo_id = data.get("photo", None)

    # Matnni tayyorlash
    text = (
        f"{anketa_id} ✅ #Yangi ariza (Ro'yxatdan o'tish)\n\n"
        f"Ismi: {data.get('answer_0')}\n"
        f"Tug'ilgan yili: {data.get('answer_1')}\n"
        f"Telefon: {data.get('answer_2')}\n"
        f"Soha: {data.get('answer_3')}\n"
        f"Manzil: {data.get('answer_4')}\n"
        f"Millati: {data.get('answer_5')}\n"
        f"Ma'lumoti: {data.get('answer_6')}\n"
        f"Oilaviy holati: {data.get('answer_7')}\n"
        f"Tajriba: {data.get('answer_8')}\n"
        f"Oldingi ish joyi: {data.get('answer_9')}\n"
        f"Maosh istagi: {data.get('answer_10')}\n"
        f"Ish vaqti: {data.get('answer_11')}\n"
        f"Sudlanganligi: {data.get('answer_12')}\n"
        f"Qayerdan eshitdi: {data.get('answer_14')}\n"
        f"Rasm: {'✅ ilova qilingan' if photo_id else 'yo‘q'}\n"
        f"{username}\n"
        f"#ariza"
    )

    # Adminga yuborish
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    if photo_id:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id)

    await update.message.reply_text("✅ Arizangiz yuborildi. Rahmat!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response)],
            PHOTO_STATE: [MessageHandler(filters.PHOTO, handle_photo)]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    print("🤖 Bot ishlayapti...")
    app.run_polling()
