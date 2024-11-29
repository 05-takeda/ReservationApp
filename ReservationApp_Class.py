from datetime import datetime
import sqlite3

# クラス: データベース管理
class DatabaseManager:
    def __init__(self, db_name='reservations.db'):
        self.db_name = db_name
        try:
            self.init_db()
        except sqlite3.Error as e:
            print(f"データベース初期化エラー: {e}")

    def init_db(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # 予約テーブルの作成
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        room_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        FOREIGN KEY (room_id) REFERENCES rooms (id)
                    )
                """)
                # 部屋テーブルの作成
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )
                """)
                # デフォルトの部屋を登録
                cursor.execute("INSERT OR IGNORE INTO rooms (name) VALUES (?)", ("藤",))
                cursor.execute("INSERT OR IGNORE INTO rooms (name) VALUES (?)", ("桜",))
                cursor.execute("INSERT OR IGNORE INTO rooms (name) VALUES (?)", ("椿",))
        except sqlite3.Error as e:
            print(f"テーブル作成エラー: {e}")

    def execute_query(self, query, params=(), fetch=False):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
        except sqlite3.Error as e:
            print(f"データベースクエリエラー: {e}")
            return None

# クラス: 予約管理
class ReservationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_rooms(self):
        """部屋リストをデータベースから取得"""
        rooms = self.db_manager.execute_query("SELECT id, name FROM rooms", fetch=True)
        if rooms:
            return {room_id: name for room_id, name in rooms}
        else:
            print("部屋データが存在しません。管理者に連絡してください。")
            return {}

    def validate_date(self):
        while True:
            date = input("予約日を YYYYMMDD 形式で入力してください: ")
            if len(date) != 8:
                print("無効な形式です。YYYYMMDD 形式で正しい日付を入力してください。")
                continue
            try:
                input_date = datetime.strptime(date, "%Y%m%d").date()
                today = datetime.today().date()
                if input_date >= today:
                    return input_date
                else:
                    print(f"無効な日付です。 {today} 以降の日付を入力してください。")
            except ValueError as e:
                print(f"日付入力エラー: {e}")
                print("無効な入力です。YYYYMMDD 形式で正しい日付を入力してください。")

    def make_reservation(self):
        rooms = self.get_rooms()
        if not rooms:
            return
        reservation_date = self.validate_date()
        while True:
            print("部屋を選択してください:")
            for room_id, room_name in rooms.items():
                print(f"{room_id}: {room_name}")
            room_input = input("部屋番号を入力してください: ")
            try:
                room_id = int(room_input)
                if room_id in rooms:
                    existing = self.db_manager.execute_query(
                        "SELECT * FROM reservations WHERE date = ? AND room_id = ?",
                        (reservation_date, room_id),
                        fetch=True
                    )
                    if existing:
                        print(f"予約失敗: {reservation_date} に {rooms[room_id]} は既に予約されています。")
                    else:
                        name = input("お客様の氏名を入力してください: ")
                        self.db_manager.execute_query(
                            "INSERT INTO reservations (date, room_id, name) VALUES (?, ?, ?)",
                            (reservation_date, room_id, name)
                        )
                        print(f"予約完了: {reservation_date} - {rooms[room_id]} - {name} 様")
                        return
                else:
                    print("無効な部屋番号です。リストにある番号を入力してください。")
            except ValueError as e:
                print(f"部屋入力エラー: {e}")
                print("無効な入力です。数字を入力してください。")

    def show_reservations(self):
        rooms = self.get_rooms()
        if not rooms:
            return
        reservations = self.db_manager.execute_query(
            "SELECT date, room_id, name FROM reservations ORDER BY date",
            fetch=True
        )
        if not reservations:
            print("現在、予約はありません。")
        else:
            print("現在の予約:")
            for date, room_id, name in reservations:
                print(f"{date} - {rooms.get(room_id, '不明な部屋')} - {name} 様")

    def cancel_reservation(self):
        rooms = self.get_rooms()
        if not rooms:
            return
        reservation_date = self.validate_date()
        while True:
            print("部屋を選択してください:")
            for room_id, room_name in rooms.items():
                print(f"{room_id}: {room_name}")
            room_input = input("部屋番号を入力してください: ")
            try:
                room_id = int(room_input)
                if room_id in rooms:
                    reservation = self.db_manager.execute_query(
                        "SELECT id, name FROM reservations WHERE date = ? AND room_id = ?",
                        (reservation_date, room_id),
                        fetch=True
                    )
                    if reservation:
                        reservation_id, name = reservation[0]
                        answer = input(f"{reservation_date} - {rooms[room_id]} - {name} 様の予約をキャンセルしますか？（Y: はい、N: いいえ）: ")
                        if answer.lower() == "y":
                            self.db_manager.execute_query(
                                "DELETE FROM reservations WHERE id = ?",
                                (reservation_id,)
                            )
                            print(f"キャンセル完了: {reservation_date} - {rooms[room_id]} - {name} 様")
                            return
                        elif answer.lower() == "n":
                            print("キャンセル処理が中止されました。")
                            return
                        else:
                            print("無効な入力です。「Y」または「N」を入力してください。")
                    else:
                        print("予約が見つかりません。")
                        return
                else:
                    print("無効な部屋番号です。リストにある番号を入力してください。")
            except ValueError as e:
                print(f"部屋入力エラー: {e}")
                print("無効な入力です。数字を入力してください。")

# クラス: アプリケーション
class ReservationApp:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.reservation_manager = ReservationManager(self.db_manager)

    def run(self):
        while True:
            print("\n予約システムメニュー")
            print("1. 新規予約")
            print("2. 予約一覧の表示")
            print("3. 予約キャンセル")
            print("4. 終了")
            cmd = input("選択してください (1/2/3/4): ")
            if cmd == '1':
                self.reservation_manager.make_reservation()
            elif cmd == '2':
                self.reservation_manager.show_reservations()
            elif cmd == '3':
                self.reservation_manager.cancel_reservation()
            elif cmd == '4':
                print("システムを終了します。")
                break
            else:
                print("無効な選択です。もう一度お試しください。")

# メインの実行
if __name__ == "__main__":
    app = ReservationApp()
    app.run()
