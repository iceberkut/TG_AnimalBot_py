from flask import Flask, request
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

app = Flask(__name__)

API_URL = "https://api.api-ninjas.com/v1/animals"
API_KEY = "GDnuIl7TawRTbZ92vPaR7A==9cl9lswhzB9sCsew"
TELEGRAM_TOKEN = "7854055828:AAHid7tuB9E6utH-A7jHms16n3oJOKAvtBM"

application = Application.builder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, напиши имя животного (eng), в ответ получишь крутую инфу! Например 'Lion', 'Afghan Hound', 'Icelandic Sheepdog' ")


async def get_animal_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animal_name = update.message.text.strip()
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(API_URL, headers=headers, params={"name": animal_name})

    if response.status_code == 200:
        data = response.json()
        print(data)
        if data:
            result = data[0]

            full_name = result.get('name', 'Unknown Animal')

            taxonomy = result.get('taxonomy', {})
            taxonomy_details = "\n".join([
                f"Kingdom: {taxonomy.get('kingdom', 'N/A')}",
                f"Phylum: {taxonomy.get('phylum', 'N/A')}",
                f"Class: {taxonomy.get('class', 'N/A')}",
                f"Order: {taxonomy.get('order', 'N/A')}",
                f"Family: {taxonomy.get('family', 'N/A')}",
                f"Genus: {taxonomy.get('genus', 'N/A')}",
                f"Scientific Name: {taxonomy.get('scientific_name', 'N/A')}"
            ])

            characteristics = result.get('characteristics', {})
            characteristics_details = "\n".join([
                f"Name of Young: {characteristics.get('name_of_young', 'N/A')}",
                f"Distinctive Feature: {characteristics.get('most_distinctive_feature', 'N/A')}",
                f"Temperament: {characteristics.get('temperament', 'N/A')}",
                f"Litter Size: {characteristics.get('litter_size', 'N/A')}",
                f"Diet: {characteristics.get('diet', 'N/A')}",
                f"Origin: {characteristics.get('origin', 'N/A')}",
                f"Top Speed: {characteristics.get('top_speed', 'N/A')}",
                f"Lifespan: {characteristics.get('lifespan', 'N/A')}"
            ])

            locations = ", ".join(result.get('locations', ['N/A']))

            message = (
                f"*Animal Information: {full_name}*\n\n"
                f"*Taxonomy:*\n{taxonomy_details}\n\n"
                f"*Characteristics:*\n{characteristics_details}\n\n"
                f"*Locations:*\n{locations}"
            )

            await update.message.reply_text(message, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                f"Sorry, I couldn't find any information about *{animal_name}*.",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text("Sorry, I couldn't retrieve the information. Please try again later.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("An error occurred. Please try again later!")


@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


if __name__ == '__main__':
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_animal_info))
    application.run_polling()
    app.run(debug=True, port=5000)
