from dotenv import load_dotenv
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

load_dotenv() # Memuat variabel dari file .env
TOKEN = os.getenv("TOKEN")         # Mengambil nilai TOKEN dari .env

# Inisialisasi Updater dengan TOKEN
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

# Tambahkan handler dan logika lainnya

updater.start_polling()
updater.idle

# Set kartu domino dari [0|0] sampai [6|6]
DOMINO_SET = [(i, j) for i in range(7) for j in range(i, 7)]

# Distribusi kartu ke pemain
def distribute_tiles():
    tiles = random.sample(DOMINO_SET, 28)
    return [tiles[:7], tiles[7:14], tiles[14:21], tiles[21:]]

# Menampilkan kartu pemain
def display_tiles(tiles):
    return " ".join([f"[{x}|{y}]" for x, y in tiles])

# Memulai permainan
def start(update: Update, context: CallbackContext) -> None:
    context.user_data['players'] = distribute_tiles()
    context.user_data['board'] = []
    context.user_data['turn'] = 0
    player_tiles = context.user_data['players'][0]
    update.message.reply_text(f"Game dimulai! Kartu Anda: {display_tiles(player_tiles)}")
    update.message.reply_text("Ketik /play untuk memainkan giliran Anda.")

# Logika permainan
def play(update: Update, context: CallbackContext) -> None:
    turn = context.user_data['turn']
    players = context.user_data['players']
    board = context.user_data['board']

    player_tiles = players[turn]
    update.message.reply_text(f"Kartu Anda: {display_tiles(player_tiles)}")
    
    if board:
        board_str = display_tiles(board)
        update.message.reply_text(f"Kartu di papan: {board_str}")
    
    valid_tiles = [tile for tile in player_tiles if board and (board[0][0] in tile or board[-1][1] in tile) or not board]

    if valid_tiles:
        # Giliran pemain
        keyboard = [[InlineKeyboardButton(f"{x}|{y}", callback_data=f"{x}|{y}") for x, y in valid_tiles]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Pilih kartu yang ingin dimainkan:', reply_markup=reply_markup)
    else:
        update.message.reply_text("Tidak ada kartu yang bisa dimainkan, Anda melewatkan giliran.")
        pass_turn(update, context)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    choice = tuple(map(int, query.data.split('|')))
    player_tiles = context.user_data['players'][context.user_data['turn']]
    board = context.user_data['board']

    if choice in player_tiles:
        if not board or (board[0][0] in choice or board[-1][1] in choice):
            if board and board[0][0] in choice:
                board.insert(0, choice)
            else:
                board.append(choice)
            player_tiles.remove(choice)
            query.edit_message_text(f"Anda memainkan: {choice}")
            pass_turn(update, context)
        else:
            query.edit_message_text("Kartu tidak cocok dengan papan!")
    else:
        query.edit_message_text("Kartu tidak valid!")

def pass_turn(update: Update, context: CallbackContext) -> None:
    context.user_data['turn'] = (context.user_data['turn'] + 1) % 4
    update.message.reply_text("Giliran berikutnya.")
    play(update, context)

def main() -> None:
    updater = Updater("TOKEN_BOT_ANDA")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("play", play))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()