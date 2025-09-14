import os
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    ConversationHandler
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
SEARCH, API_SETUP = range(2)

# Your bot token from BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Single API configuration
API_URL = os.environ.get("API_URL", "https://your-universal-api.com/search")
API_KEY = os.environ.get("API_KEY", "YOUR_API_KEY_HERE")

class DataSearchBot:
    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        welcome_text = (
            "👋 Welcome to *Smarty Sunny Bot*\n\n"
            "🔍 Send your target number/email (e.g. +91********** or email@example.com)\n"
            "_I will search for leaked data if available._\n\n"
            "🔴 *Credit by Smart Sunny*"
        )
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = """
🤖 **Bot Commands:**

/start - Start the bot
/help - Show this help message
/search - Start a new search
/setapi - Configure API key
/cancel - Cancel the current operation

🔍 **Search Examples:**
- `example@gmail.com` - Search by email
- `+79001234567` - Search by phone number
- `127.0.0.1` - Search by IP address
- `Petrov Ivan` - Search by name
- `O999МУ777` - Search by car number

📝 **Note:** You can also perform composite searches.
        """
        await update.message.reply_text(help_text)

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the search conversation."""
        await update.message.reply_text(
            "🔍 What would you like to search for?\n\n"
            "You can search for:\n"
            "• Emails (example@gmail.com)\n"
            "• Phone numbers (+79001234567)\n"
            "• IP addresses (127.0.0.1)\n"
            "• Names (Petrov Ivan)\n"
            "• Vehicle info (O999МУ777)\n\n"
            "Just type your search query:"
        )
        
        return SEARCH

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all incoming messages that are not commands."""
        user_input = update.message.text
        
        # Show typing action to indicate processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Call the universal API
        result = await self.call_universal_api(user_input)
        
        # Send the result
        await update.message.reply_text(result)

    async def perform_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Perform the search using the universal API."""
        user_input = update.message.text
        
        # Show typing action to indicate processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Call the universal API
        result = await self.call_universal_api(user_input)
        
        # Send the result
        await update.message.reply_text(result)
        
        return ConversationHandler.END

    async def call_universal_api(self, query):
        """Call the universal API with the search query."""
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return "❌ API not configured. Please set up your API key using /setapi command."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "types": ["email", "phone", "name", "ip", "vehicle", "username", "password"]
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self.format_api_response(data, query)
            elif response.status_code == 401:
                return "❌ Invalid API key. Please check your API configuration using /setapi."
            elif response.status_code == 402:
                return "❌ API quota exceeded. Please upgrade your plan."
            else:
                return f"❌ API error: {response.status_code}. Please try again later."
                
        except requests.exceptions.Timeout:
            return "❌ Request timeout. The API is taking too long to respond."
        except requests.exceptions.ConnectionError:
            return "❌ Connection error. Please check your internet connection."
        except Exception as e:
            logger.error(f"API call error: {e}")
            return "❌ An error occurred while processing your request. Please try again later."

    def format_api_response(self, data, query):
        """Format the API response into a user-friendly message."""
        results = data.get("results", [])
        
        if not results:
            return f"🔍 No results found for: {query}"
        
        response_text = f"🔍 Search Results for: {query}\n\n"
        
        for result in results:
            result_type = result.get("type", "Unknown")
            value = result.get("value", "N/A")
            details = result.get("details", {})
            
            response_text += f"📋 Type: {result_type.upper()}\n"
            response_text += f"🔎 Value: {value}\n"
            
            # Add details based on result type
            if result_type == "email":
                response_text += f"📧 Email: {value}\n"
                response_text += f"📈 Breaches: {details.get('breaches', 'N/A')}\n"
                response_text += f"⚠️ Suspicious: {details.get('suspicious', 'N/A')}\n"
            elif result_type == "phone":
                response_text += f"📱 Phone: {value}\n"
                response_text += f"🏢 Carrier: {details.get('carrier', 'N/A')}\n"
                response_text += f"🌍 Region: {details.get('region', 'N/A')}\n"
            elif result_type == "ip":
                response_text += f"📍 IP: {value}\n"
                response_text += f"🌍 Country: {details.get('country', 'N/A')}\n"
                response_text += f"🏙️ City: {details.get('city', 'N/A')}\n"
                response_text += f"🏢 ISP: {details.get('isp', 'N/A')}\n"
            elif result_type == "name":
                response_text += f"👤 Name: {value}\n"
                response_text += f"📊 Profiles: {details.get('profiles', 'N/A')}\n"
                response_text += f"🔗 Social Media: {details.get('social_media', 'N/A')}\n"
            elif result_type == "vehicle":
                response_text += f"🚗 Vehicle: {value}\n"
                response_text += f"🏭 Make: {details.get('make', 'N/A')}\n"
                response_text += f"🎨 Model: {details.get('model', 'N/A')}\n"
                response_text += f"📅 Year: {details.get('year', 'N/A')}\n"
            
            response_text += "─" * 30 + "\n\n"
        
        # Add summary and credit
        response_text += f"📊 Summary: Found {len(results)} results across different data types.\n\n"
        response_text += "🔴 *Credit by Smart Sunny*"
        
        return response_text

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the current operation."""
        await update.message.reply_text(
            "Operation cancelled.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def setup_api(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the API setup conversation."""
        await update.message.reply_text(
            "Please enter your Universal API key:\n\n"
            "Format: YOUR_API_KEY\n\n"
            "You can get this key from your API provider."
        )
        return API_SETUP

    async def save_api_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save the provided API key."""
        api_key = update.message.text.strip()
        
        if not api_key:
            await update.message.reply_text("❌ Invalid API key. Please try again with /setapi.")
            return ConversationHandler.END
        
        self.api_key = api_key
        logger.info(f"Updated API key: {api_key[:10]}...")
        
        await update.message.reply_text(
            "✅ API key updated successfully!\n\n"
            "You can now use the search features with your universal API."
        )
        return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Initialize our bot class
    bot = DataSearchBot()
    
    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("search", bot.search)],
        states={
            SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.perform_search)],
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)],
    )
    
    # Add API setup conversation handler
    api_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setapi", bot.setup_api)],
        states={
            API_SETUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.save_api_key)],
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(conv_handler)
    application.add_handler(api_conv_handler)
    
    # Add handler for regular messages (non-commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
