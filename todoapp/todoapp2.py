import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QCalendarWidget, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QDate

DB_NAME = "todo_calendar.db"

class DailyToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("월별 할 일 체크 앱 (Daily To-Do List)")
        self.resize(700, 500)

        self.conn = sqlite3.connect(DB_NAME)
        self.create_table()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # 달력 위젯 (왼쪽)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.load_todos_for_date)
        self.layout.addWidget(self.calendar, 1)

        # 할 일 관리 영역 (오른쪽)
        right_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("할 일을 입력하세요")
        input_layout.addWidget(self.todo_input)
        self.add_button = QPushButton("추가")
        self.add_button.clicked.connect(self.add_todo)
        input_layout.addWidget(self.add_button)

        right_layout.addLayout(input_layout)

        self.todo_list = QListWidget()
        self.todo_list.itemChanged.connect(self.update_checked)
        right_layout.addWidget(self.todo_list, 1)

        self.delete_button = QPushButton("선택 항목 삭제")
        self.delete_button.clicked.connect(self.delete_todo)
        right_layout.addWidget(self.delete_button)

        self.layout.addLayout(right_layout, 2)

        # 오늘 날짜의 할 일 로드
        self.load_todos_for_date()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                content TEXT NOT NULL,
                checked INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()

    def get_selected_date_str(self):
        date = self.calendar.selectedDate()
        return date.toString("yyyy-MM-dd")

    def load_todos_for_date(self):
        date_str = self.get_selected_date_str()
        self.todo_list.clear()

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, content, checked FROM todos WHERE date=? ORDER BY id", (date_str,))
        rows = cursor.fetchall()
        for todo_id, content, checked in rows:
            item = QListWidgetItem(content)
            item.setData(Qt.UserRole, todo_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            self.todo_list.addItem(item)

    def add_todo(self):
        content = self.todo_input.text().strip()
        if not content:
            QMessageBox.warning(self, "경고", "할 일을 입력하세요!")
            return

        date_str = self.get_selected_date_str()
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO todos (date, content, checked) VALUES (?, ?, 0)", (date_str, content))
            self.conn.commit()
            print(f"저장 완료: {date_str} - {content}")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"DB 저장 실패:\n{e}")
            print(f"DB 저장 실패: {e}")
            return

        self.todo_input.clear()
        self.load_todos_for_date()


    def update_checked(self, item):
        todo_id = item.data(Qt.UserRole)
        checked = 1 if item.checkState() == Qt.Checked else 0
        cursor = self.conn.cursor()
        cursor.execute("UPDATE todos SET checked=? WHERE id=?", (checked, todo_id))
        self.conn.commit()

    def delete_todo(self):
        selected_items = self.todo_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "정보", "삭제할 항목을 선택하세요.")
            return

        reply = QMessageBox.question(
            self, "확인", f"{len(selected_items)}개의 항목을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            for item in selected_items:
                todo_id = item.data(Qt.UserRole)
                cursor.execute("DELETE FROM todos WHERE id=?", (todo_id,))
            self.conn.commit()
            self.load_todos_for_date()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DailyToDoApp()
    window.show()
    sys.exit(app.exec_())
