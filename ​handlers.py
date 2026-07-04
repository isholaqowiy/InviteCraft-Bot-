import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
import database
import invitation_generator
import utils
from config import ADMIN_ID

EVENT_TYPE, TITLE, HOST, DATE, TIME, VENUE, RSVP = range(7)

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎉 Create Invitation", callback_data="menu_create")],
        [InlineKeyboardButton("🎨 Choice Template", callback_data="menu_template"),
         InlineKeyboardButton("👀 Preview Card", callback_data="menu_preview")],
        [InlineKeyboardButton("💾 Download Invitation", callback_data="menu_download"),
         InlineKeyboardButton("❓ Help", callback_data="menu_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utils.ensure_temp_directory()
    uid = update.effective_user.id
    await database.register_user(uid)
    
    welcome = (
        "👋 Welcome to *InviteCraft Bot*!\n"
        "Design beautiful digital invitations in minutes for any occasion.\n\n"
        "🎉 *Create invitations for weddings, birthdays, and more*\n"
        "🎨 *Choose from premium layout templates*\n"
        "🖼 *Add personalized details seamlessly*\n"
        "📍 *Generate automated RSVP QR codes*\n\n"
        "Tap a button below to start creating your invitation."
    )
    if update.message:
        await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode="Markdown")
    return ConversationHandler.END

async def start_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['invite_build'] = {}
    await query.message.reply_text("🎂 Enter the *Event Type* (e.g. Birthday Party, Wedding, Graduation):", parse_mode="Markdown")
    return EVENT_TYPE

async def get_event_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['invite_build']['event_type'] = update.message.text
    await update.message.reply_text("✨ Enter the *Event Title* (e.g. David's 25th Bash):", parse_mode="Markdown")
    return TITLE

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['invite_build']['title'] = update.message.text
    await update.message.reply_text("🪪 Enter the *Host Name*:", parse_mode="Markdown")
    return HOST

async def get_host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['invite_build']['host'] = update.message.text
    await update.message.reply_text("📅 Enter the *Date* of the event (e.g. October 12, 2026):", parse_mode="Markdown")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['invite_build']['date_str'] = update.message.text
    await update.message.reply_text("🕒 Enter the *Time* of the event (e.g. 4:00 PM WAT):", parse_mode="Markdown")
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['invite_build']['time_str'] = update.message.text
    await update.message.reply_text("📍 Enter the *Venue Address*:", parse_mode="Markdown")
    return VENUE

async def get_venue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['invite_build']['venue'] = update.message.text
    await update.message.reply_text("📱 Enter *RSVP Contact Information*:", parse_mode="Markdown")
    return RSVP

async def get_rsvp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    context.user_data['invite_build']['rsvp'] = update.message.text
    context.user_data['invite_build']['template'] = "Elegant"
    
    await database.save_invitation(uid, context.user_data['invite_build'])
    await update.message.reply_text("🎉 Details verified! Use the menu controls below to preview your generated digital card assets.", reply_markup=get_main_menu())
    return ConversationHandler.END

async def menu_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    if query.data == "menu_template":
        kb = [[InlineKeyboardButton("Elegant Theme", callback_data="tpl_Elegant")],
              [InlineKeyboardButton("Luxury Theme", callback_data="tpl_Luxury")],
              [InlineKeyboardButton("Minimal Style", callback_data="tpl_Minimal")],
              [InlineKeyboardButton("Dark Theme", callback_data="tpl_Dark Theme")],
              [InlineKeyboardButton("🔙 Menu", callback_data="go_home")]]
        await query.edit_message_text("🎨 *Choose your design profile style:*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        
    elif query.data.startswith("tpl_"):
        target_tpl = query.data.split("_")[1]
        data = await database.get_invitation(uid)
        if data:
            data['template'] = target_tpl
            await database.save_invitation(uid, data)
            await query.message.reply_text(f"✅ Design layout set to: `{target_tpl}`")
        else:
            await query.message.reply_text("❌ No active card configuration profile data found.")
            
    elif query.data in ("menu_preview", "menu_download"):
        data = await database.get_invitation(uid)
        if not data:
            await query.message.reply_text("❌ No data found. Please create an invitation profile first.")
            return
            
        path = invitation_generator.render_invitation_card(data, uid)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                await query.message.reply_document(document=f, filename="invitation.png")
            utils.clean_user_files(uid)
        else:
            await query.message.reply_text("❌ Render engine processing exception fault tracking.")
            
    elif query.data == "go_home":
        await query.edit_message_text("Tap a button below to start creating your invitation.", reply_markup=get_main_menu())
    elif query.data == "menu_help":
        await query.message.reply_text("❓ *Help Manual:* Tap 'Create Invitation', complete the conversational questionnaire wizard, and export high-resolution media instantly.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users, cards = await database.get_analytics()
    await update.message.reply_text(f"📊 *Production Metrics:*\n\nRegistered Ecosystem Accounts: `{users}`\nCompiled Graphic Renderings: `{cards}`", parse_mode="Markdown")

