import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt

DB_NAME = "todo_list.db"

class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("할 일 체크 앱 (To-Do List)")
        self.resize(400, 600)

        self.conn = sqlite3.connect(DB_NAME)
        self.create_table()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 입력창과 추가 버튼
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("할 일을 입력하세요")
        input_layout.addWidget(self.todo_input)
        self.add_button = QPushButton("추가")
        self.add_button.clicked.connect(self.add_todo)
        input_layout.addWidget(self.add_button)
        self.layout.addLayout(input_layout)

        # 할 일 목록
        self.todo_list = QListWidget()
        self.layout.addWidget(self.todo_list)

        # 버튼들 (삭제, HTML 내보내기)
        btn_layout = QHBoxLayout()
        self.delete_button = QPushButton("선택 항목 삭제")
        self.delete_button.clicked.connect(self.delete_todo)
        btn_layout.addWidget(self.delete_button)

        self.export_button = QPushButton("HTML로 내보내기")
        self.export_button.clicked.connect(self.export_html)
        btn_layout.addWidget(self.export_button)

        self.layout.addLayout(btn_layout)

        self.load_todos()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                checked INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.conn.commit()

    def load_todos(self):
        self.todo_list.clear()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, content, checked FROM todos")
        rows = cursor.fetchall()
        for todo_id, content, checked in rows:
            item = QListWidgetItem(content)
            item.setData(Qt.UserRole, todo_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            self.todo_list.addItem(item)
        self.todo_list.itemChanged.connect(self.update_checked)

    def add_todo(self):
        content = self.todo_input.text().strip()
        if not content:
            QMessageBox.warning(self, "경고", "할 일을 입력하세요!")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO todos (content, checked) VALUES (?, 0)", (content,))
        self.conn.commit()

        self.todo_input.clear()
        self.load_todos()

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
            self.load_todos()

    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "HTML로 내보내기", "", "HTML Files (*.html)")
        if not path:
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT content, checked FROM todos")
        todos = cursor.fetchall()

        html_content = """
        <html>
        <head><meta charset="UTF-8"><title>할 일 목록</title></head>
        <body>
        <h1>할 일 목록</h1>
        <ul>
        """
        for content, checked in todos:
            status = "✔️" if checked else "❌"
            html_content += f"<li>{status} {content}</li>\n"
        html_content += """
        </ul>
        </body>
        </html>
        """

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
            QMessageBox.information(self, "완료", f"HTML 파일로 저장했습니다:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"파일 저장 실패:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec_())
