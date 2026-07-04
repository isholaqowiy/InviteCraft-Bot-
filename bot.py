import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import database
import handlers
from config import BOT_TOKEN

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(database.init_db())

    if not BOT_TOKEN:
        print("Fatal Error: Missing BOT_TOKEN")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.start_creation, pattern="^menu_create$")],
        states={
            handlers.EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_event_type)],
            handlers.TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_title)],
            handlers.HOST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_host)],
            handlers.DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_date)],
            handlers.TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_time)],
            handlers.VENUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_venue)],
            handlers.RSVP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_rsvp)]
        },
        fallbacks=[CommandHandler("start", handlers.start)]
    )

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("stats", handlers.admin_stats))
    app.add_handler(CallbackQueryHandler(handlers.menu_routing, pattern="^(menu_|tpl_|go_home)"))
    app.add_handler(conv_handler)

    print("InviteCraft Engine Online...")
    app.run_polling()

if __name__ == '__main__':
    main()

