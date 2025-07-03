import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                             QFileDialog, QMessageBox, QStatusBar, QTabWidget, QFontDialog)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# 새 창이 가비지 컬렉션되는 것을 방지하기 위한 전역 리스트
open_windows = []

class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # --- 탭 위젯을 중앙 위젯으로 설정 ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_on_tab_change)
        self.setCentralWidget(self.tabs)

        # --- 메뉴바 생성 ---
        self.create_menu_bar()

        # --- 상태 표시줄 생성 ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # --- 창 설정 ---
        self.setGeometry(150, 150, 800, 600)
        
        self.setWindowIcon(QIcon('C:/Users/SBA/github/pyqt5_example/icon/edit.png'))
        
        # --- 초기 탭 생성 ---
        self.new_tab()

    def current_editor(self):
        """현재 활성화된 탭의 QTextEdit 위젯을 반환합니다."""
        return self.tabs.currentWidget()

    def update_status_bar(self):
        """현재 에디터의 커서 위치를 상태 표시줄에 업데이트합니다."""
        editor = self.current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.status_bar.showMessage(f"Line: {line}, Col: {col}")

    def update_title(self):
        """현재 탭의 상태에 따라 창과 탭의 제목을 업데이트합니다."""
        editor = self.current_editor()
        if not editor:
            self.setWindowTitle("Notepad-pyqt")
            return

        index = self.tabs.currentIndex()
        file_path = editor.property("file_path")
        title = os.path.basename(file_path) if file_path else "Untitled"
        
        if editor.document().isModified():
            title = f"*{title}"
        
        self.tabs.setTabText(index, os.path.basename(title).strip('*'))
        self.setWindowTitle(f"{title} - Notepad-pyqt")

    def update_on_tab_change(self, index):
        """탭이 변경될 때 제목과 상태 표시줄을 업데이트합니다."""
        self.update_title()
        self.update_status_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # --- 파일 메뉴 ---
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(QAction('New Tab', self, shortcut='Ctrl+T', triggered=self.new_tab))
        file_menu.addAction(QAction('New Window', self, shortcut='Ctrl+Shift+N', triggered=self.new_window))
        file_menu.addAction(QAction('Open...', self, shortcut='Ctrl+O', triggered=self.open_file))
        file_menu.addAction(QAction('Save', self, shortcut='Ctrl+S', triggered=self.save_file))
        file_menu.addAction(QAction('Save As...', self, shortcut='Ctrl+Shift+S', triggered=self.save_file_as))
        file_menu.addSeparator()
        file_menu.addAction(QAction('Exit', self, shortcut='Ctrl+Q', triggered=self.close))

        # --- 편집 메뉴 ---
        edit_menu = menu_bar.addMenu('&Edit')
        edit_menu.addAction(QAction('Undo', self, shortcut='Ctrl+Z', triggered=lambda: self.current_editor().undo()))
        edit_menu.addAction(QAction('Redo', self, shortcut='Ctrl+Y', triggered=lambda: self.current_editor().redo()))
        edit_menu.addSeparator()
        edit_menu.addAction(QAction('Cut', self, shortcut='Ctrl+X', triggered=lambda: self.current_editor().cut()))
        edit_menu.addAction(QAction('Copy', self, shortcut='Ctrl+C', triggered=lambda: self.current_editor().copy()))
        edit_menu.addAction(QAction('Paste', self, shortcut='Ctrl+V', triggered=lambda: self.current_editor().paste()))
        edit_menu.addSeparator()
        edit_menu.addAction(QAction('Select All', self, shortcut='Ctrl+A', triggered=lambda: self.current_editor().selectAll()))

        # --- 보기 메뉴 ---
        view_menu = menu_bar.addMenu('&View')
        zoom_menu = view_menu.addMenu('Zoom')
        zoom_menu.addAction(QAction('Zoom In', self, shortcut='Ctrl++', triggered=self.zoom_in))
        zoom_menu.addAction(QAction('Zoom Out', self, shortcut='Ctrl+-', triggered=self.zoom_out))
        zoom_menu.addAction(QAction('Restore Default Zoom', self, shortcut='Ctrl+0', triggered=self.restore_zoom))
        
        # --- 서식 메뉴 ---
        format_menu = menu_bar.addMenu('&Format')
        format_menu.addAction(QAction('Font...', self, triggered=self.choose_font))
        theme_menu = format_menu.addMenu('Theme')
        theme_menu.addAction(QAction('Light', self, triggered=self.set_light_theme))
        theme_menu.addAction(QAction('Dark', self, triggered=self.set_dark_theme))

    def new_tab(self, checked=False, file_path=None, content=''):
        """새 탭을 생성하고 텍스트 에디터를 추가합니다."""
        editor = QTextEdit()
        editor.cursorPositionChanged.connect(self.update_status_bar)
        editor.document().modificationChanged.connect(self.update_title)

        index = self.tabs.addTab(editor, "Untitled")
        self.tabs.setCurrentIndex(index)

        editor.setProperty("file_path", file_path)
        editor.setText(content)
        
        if file_path:
            self.load_file_content(index, file_path)
        
        self.update_title()

    def new_window(self):
        """새 메모장 창을 생성합니다."""
        new_win = Notepad()
        open_windows.append(new_win)
        new_win.show()

    def open_file(self):
        """파일 열기 대화상자를 통해 하나 이상의 파일을 새 탭으로 엽니다."""
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open File", "", 
                                                   "Text Files (*.txt);;All Files (*)", options=options)
        for file_path in file_paths:
            if file_path:
                # 파일이 이미 열려있는지 확인
                for i in range(self.tabs.count()):
                    if self.tabs.widget(i).property("file_path") == file_path:
                        self.tabs.setCurrentIndex(i)
                        break
                else: # for-else 구문: break가 실행되지 않았다면 새 탭으로 연다
                    self.new_tab(file_path=file_path)

    def load_file_content(self, tab_index, file_path):
        """지정된 탭에 파일 내용을 로드합니다."""
        editor = self.tabs.widget(tab_index)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                editor.setText(f.read())
            editor.setProperty("file_path", file_path)
            editor.document().setModified(False)
            self.update_title()
        except Exception as e:
            self.show_error_message(f"Error opening file: {e}")
            self.close_tab(tab_index)

    def save_file(self):
        """현재 탭의 내용을 저장합니다."""
        editor = self.current_editor()
        if not editor: return False
        
        file_path = editor.property("file_path")
        if not file_path:
            return self.save_file_as()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
            editor.document().setModified(False)
            self.update_title()
            return True
        except Exception as e:
            self.show_error_message(f"Error saving file: {e}")
            return False

    def save_file_as(self):
        """현재 탭의 내용을 다른 이름으로 저장합니다."""
        editor = self.current_editor()
        if not editor: return False

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "",
                                                   "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            editor.setProperty("file_path", file_path)
            return self.save_file()
        return False

    def zoom_in(self):
        """현재 텍스트 에디터의 내용을 확대합니다."""
        editor = self.current_editor()
        if editor: editor.zoomIn(2)

    def zoom_out(self):
        """현재 텍스트 에디터의 내용을 축소합니다."""
        editor = self.current_editor()
        if editor: editor.zoomOut(2)

    def restore_zoom(self):
        """현재 텍스트 에디터의 폰트 크기를 기본값으로 복원합니다."""
        editor = self.current_editor()
        if editor:
            # 기본 폰트 크기를 10pt로 가정
            font = editor.font()
            font.setPointSize(10)
            editor.setFont(font)

    def choose_font(self):
        """글꼴 선택 대화상자를 엽니다."""
        editor = self.current_editor()
        if editor:
            font, ok = QFontDialog.getFont(editor.currentFont(), self)
            if ok:
                editor.setCurrentFont(font)

    def set_light_theme(self):
        """밝은 테마를 적용합니다."""
        editor = self.current_editor()
        if editor:
            editor.setStyleSheet("background-color: white; color: black;")

    def set_dark_theme(self):
        """어두운 테마를 적용합니다."""
        editor = self.current_editor()
        if editor:
            editor.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")

    def close_tab(self, index):
        """지정된 인덱스의 탭을 닫습니다."""
        if not self.maybe_save_tab(index):
            return # 저장 취소 시 닫지 않음

        self.tabs.removeTab(index)
        
        # 모든 탭이 닫히면 창을 닫습니다.
        if self.tabs.count() == 0:
            self.close()

    def maybe_save_tab(self, index):
        """수정된 탭을 닫기 전에 저장할지 묻습니다."""
        editor = self.tabs.widget(index)
        if not editor.document().isModified():
            return True
        
        self.tabs.setCurrentIndex(index)
        
        ret = QMessageBox.warning(self, "Notepad",
                                  f"Do you want to save changes to {self.tabs.tabText(index)}?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if ret == QMessageBox.Save:
            return self.save_file()
        elif ret == QMessageBox.Cancel:
            return False
        return True

    def closeEvent(self, event):
        """창 닫기 이벤트를 처리합니다."""
        # 모든 탭을 순회하며 저장 여부 확인
        for i in range(self.tabs.count() - 1, -1, -1):
            if not self.maybe_save_tab(i):
                event.ignore() # 사용자가 취소하면 닫기 이벤트 무시
                return
        event.accept()

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def load_own_code(self):
        """프로그램 자신의 소스 코드를 첫 탭에 로드합니다."""
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                content = f.read()
            # 현재 탭에 내용 설정
            editor = self.current_editor()
            editor.setText(content)
            editor.setProperty("file_path", __file__)
            editor.document().setModified(False)
            self.update_title()
        except Exception as e:
            self.show_error_message(f"Error loading source code: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = Notepad()
    open_windows.append(main_win)
    # main_win.load_own_code() # 프로그램 시작 시 자신의 코드 로드
    main_win.show()
    sys.exit(app.exec_())