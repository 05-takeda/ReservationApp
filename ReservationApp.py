# 飲食店予約管理システム

from datetime import datetime
import sqlite3

# 使用する部屋のリスト
rooms = ['藤', '桜', '椿']

# データベースの初期化関数
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
    init_db() # データベースを初期化
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
        # 1-4以外が入力された場合
        else:
            print("無効な選択です。もう一度お試しください。")

# 日付の形式確認、当日以降のみ予約可能にする処理
def validate_date():
    while True:
        date = input("予約日を YYYYMMDD 形式で入力してください: ")
        if len(date) != 8:
            print("無効な形式です。YYYYMMDD 形式で正しい日付を入力してください。")
        try:
            # 入力された日付をパース
            input_date = datetime.strptime(date, "%Y%m%d").date()
            # 現在の日付を取得
            today = datetime.today().date()
            # 入力された日付が当日以降ならinput_dateを返す
            if input_date >= today:
                return input_date
            # 前日以前の日付が入力されたとき
            else:
                print(f"無効な日付です。 {today} 以降の日付を入力してください。")
        # 無効な形式での入力
        except ValueError:
            print("無効な入力です。YYYYMMDD 形式で正しい日付を入力してください。")

# 予約の作成
def make_reservation():
    # 予約情報の入力
    while True:
        # 日付の形式と当日以降か確認
        reservation_date = validate_date()
        room_input = input("部屋を選択してください（0: 藤、1: 桜、2: 椿）: ")
        try:
            room = int(room_input) # 数値として取得
            if room in [0, 1, 2]:
                conn = sqlite3.connect('reservations.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reservations WHERE date = ? AND room = ?", (reservation_date, room))
                # 予約の重複確認(同じ日付と部屋で予約があるか確認)
                if cursor.fetchone():
                    print(f"予約失敗: {reservation_date} に {rooms[room]} は既に予約されています。")
                # 重複なくループ終了した場合の処理
                else:
                    name = input("お客様の氏名を入力してください: ")
                    cursor.execute("INSERT INTO reservations (date, room, name) VALUES (?, ?, ?)", (reservation_date, room, name))
                    conn.commit()
                    print(f"予約完了: {reservation_date} - {rooms[room]} - {name} 様")
                    break
            # 0-2以外の数字が入力されたとき
            else:
                print("無効な番号です。0、1、2のいずれかを選択してください。")
        # 数字以外が入力されたとき
        except ValueError:
            print("無効な入力です。0、1、2いずれかの数字を入力してください。")
        finally:
            conn.close()

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
    # 予約がある場合
    else:
        print("現在の予約:")
        for reservation in reservations:
            date, room, name = reservation
            print(f"{date} - {rooms[room]} - {name} 様")

# 予約のキャンセル
def cancel_reservation():
    # キャンセル情報の入力
    while True:
        # 日付の形式と当日以降か確認
        reservation_date = validate_date()
        room_input = input("部屋を選択してください（0: 藤、1: 桜、2: 椿）: ") 
        try:
            room = int(room_input) # 数値として取得
            if room in [0, 1, 2]:
                conn = sqlite3.connect('reservations.db')
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM reservations WHERE date = ? AND room = ?", (reservation_date, room))
                result = cursor.fetchone()
                if result:
                    reservation_id, name = result
                    while True:
                        # クッションメッセージ
                        answer = input(f"{reservation_date} - {rooms[room]} - {name} 様の予約をキャンセルしますか？（Y: はい、N: いいえ）: ")
                        if answer.lower() == "y":
                            cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
                            conn.commit()
                            print(f"キャンセル完了: {reservation_date} - {rooms[room]} - {name} 様")
                            return # 関数の終了
                        elif answer.lower() == "n":
                            print("キャンセル処理が中止されました。")
                            return
                        else:
                            print("無効な入力です。Y、Nのいずれかを入力してください。")
                # 一致する予約がないとき
                else:
                    print(f"キャンセル失敗:予約が見つかりません。")
            # 0-2以外の数字が入力されたとき
            else:
                print("無効な番号です。0、1、2のいずれかを選択してください。")
        # 数字以外が入力されたとき
        except ValueError:
            print("無効な入力です。0、1、2いずれかの数字を入力してください。")
        finally:
            conn.close()

# メインの実行
main()