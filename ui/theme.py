"""Hoja de estilos (QSS) del tema oscuro forense."""

DARK_QSS = """
QWidget {
    background-color: #1e1e1e;
    color: #dcdcdc;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #1e1e1e;
}
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    top: -1px;
}
QTabBar::tab {
    background: #252526;
    color: #b0b0b0;
    padding: 6px 12px;
    border: 1px solid #3c3c3c;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #1e1e1e;
    color: #4ec9b0;
    border-bottom: 2px solid #4ec9b0;
}
QTabBar::tab:hover {
    color: #ffffff;
}
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: none;
    padding: 6px 12px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:disabled {
    background-color: #3c3c3c;
    color: #777777;
}
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {
    background-color: #252526;
    color: #dcdcdc;
    border: 1px solid #3c3c3c;
    border-radius: 3px;
    padding: 3px;
    selection-background-color: #264f78;
}
QTableWidget, QTreeWidget {
    background-color: #1e1e1e;
    alternate-background-color: #252526;
    gridline-color: #3c3c3c;
    selection-background-color: #264f78;
    selection-color: #ffffff;
}
QHeaderView::section {
    background-color: #252526;
    color: #4ec9b0;
    padding: 4px;
    border: 1px solid #3c3c3c;
}
QProgressBar {
    border: 1px solid #3c3c3c;
    border-radius: 3px;
    background-color: #252526;
    text-align: center;
    color: #dcdcdc;
}
QProgressBar::chunk {
    background-color: #0e639c;
}
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
}
QMenu {
    background-color: #252526;
    border: 1px solid #3c3c3c;
}
QMenu::item:selected {
    background-color: #0e639c;
}
QScrollBar:vertical {
    background: #1e1e1e;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #3c3c3c;
    border-radius: 6px;
}
"""
