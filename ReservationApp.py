# 飲食店予約管理システム

from datetime import datetime
import sqlite3

# 使用する部屋のリスト
rooms = ['藤', '桜', '椿']

# 予約を保存するデータベースの初期化
def init_db():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            room INTEGER NOT NULL,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# メイン
def main():
    # データベースを初期化
    init_db()
    while True:
        print("\n予約システムメニュー")
        print("1. 新規予約")
        print("2. 予約一覧の表示")
        print("3. 予約キャンセル")
        print("4. 終了")    
        cmd = input("選択してください (1/2/3/4): ")
        if cmd == '1':
            # 予約の作成
            make_reservation()    
        elif cmd == '2':
            # 予約の表示
            show_reservations()
        elif cmd == '3':
            # 予約のキャンセル
            cancel_reservation()
        elif cmd == '4':
            # システム終了
            print("システムを終了します。")
            break # ループを抜ける
        else:
            print("無効な選択です。もう一度お試しください。")

# 日付の形式確認、当日以降のみ予約可能にする処理
def validate_date(date):
    if len(date) != 8:
        print("無効な形式です。YYYYMMDD 形式で正しい日付を入力してください。")
        return False
    try:
        # 入力された日付をパース
        input_date = datetime.strptime(date, "%Y%m%d").date()
        # 現在の日付を取得
        today = datetime.today().date()
        # 入力された日付が当日以降ならTrueを返す
        if input_date >= today:
            return True
        else:
            print(f"無効な日付です。 {today} 以降の日付を入力してください。")
            return False
    except ValueError:
        print("無効な入力です。YYYYMMDD 形式で正しい日付を入力してください。")
        return False

# 予約の作成
def make_reservation():
    # 予約情報の入力
    date = input("予約日を YYYYMMDD 形式で入力してください: ")
    # 日付の形式と当日以降か確認
    if not validate_date(date):
        return # 関数の終了
    room_input = input("部屋を選択してください（0: 藤、1: 桜、2: 椿）: ")
    try:
        room = int(room_input) # 数値として取得
        if room in [0, 1, 2]:
            name = input("お客様の氏名を入力してください: ")
            conn = sqlite3.connect('reservations.db')
            cursor = conn.cursor()
            # 予約の重複確認(同じ日付と部屋で予約があるか確認)
            cursor.execute("SELECT * FROM reservations WHERE date = ? AND room = ?", (date, room))
            if cursor.fetchone():
                print(f"予約失敗: {date} に {rooms[room]} は既に予約されています。")
            else: # 重複なくループ終了した場合の処理
                cursor.execute("INSERT INTO reservations (date, room, name) VALUES (?, ?, ?)", (date, room, name))
                conn.commit()
                print(f"予約完了: {date} - {rooms[room]} - {name} 様")
            conn.close()
        else:
            print("無効な番号です。0、1、2のいずれかを選択してください。")
    except ValueError:
        print("無効な入力です。0、1、2いずれかの数字を入力してください。")

# 現在の予約一覧を表示
def show_reservations():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    # 予約を日付順で抽出
    cursor.execute("SELECT date, room, name FROM reservations ORDER BY date")
    reservations = cursor.fetchall()
    conn.close()
    # データベースが空のとき
    if not reservations:
        print("現在、予約はありません。")
    else:
        print("現在の予約:")
        for reservation in reservations:
            date, room, name = reservation
            print(f"{date} - {rooms[room]} - {name} 様")

# 予約のキャンセル
def cancel_reservation():
    date = input("キャンセルする予約日を YYYYMMDD 形式で入力してください: ")
    if not validate_date(date):
        return # 関数の終了
    room_input = input("キャンセルする部屋を選択してください（0: 藤、1: 桜、2: 椿）: ") 
    try:
        room = int(room_input)
        if room in [0, 1, 2]:
            conn = sqlite3.connect('reservations.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM reservations WHERE date = ? AND room = ?", (date, room))
            result = cursor.fetchone()
            if result:
                reservation_id, name = result
                # クッションメッセージ
                answer = input(f"{date} - {rooms[room]} - {name} 様の予約をキャンセルしますか？（Y: はい、N: いいえ）: ")
                if answer.lower() == "y":
                    cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
                    conn.commit()
                    print(f"キャンセル完了: {date} - {rooms[room]} - {name} 様")
                else:
                    print("キャンセル処理が中止されました。")
            else:
                print(f"キャンセル失敗: 予約が見つかりません。")
            conn.close()
        else:
            print("無効な番号です。0、1、2のいずれかを選択してください。")
    except ValueError:
        print("無効な入力です。0、1、2いずれかの数字を入力してください。")

# メインの実行
main()
