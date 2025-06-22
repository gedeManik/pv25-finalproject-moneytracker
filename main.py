import sys
import sqlite3
import csv
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate

class MoneyTracker(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("design.ui", self)

        self.conn = sqlite3.connect("money.db")
        self.create_table()

        self.statusbar.showMessage("I Gede Manik Ariyasa | F1D022046")
        self.dateEdit.setDate(QDate.currentDate())

        # Tombol dan menu
        self.pushButtonAdd.clicked.connect(self.add_entry)
        self.actionExport_CSV.triggered.connect(self.export_csv)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionClose.triggered.connect(QtWidgets.qApp.quit)

        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e6f5e6;
            }
            QGroupBox {
                border: 1px solid #a6d8a8;
                background-color: #f4fff4;
                font-weight: bold;
                margin-top: 10px;
            }
            QLabel {
                color: #2e7d32;
            }
            QPushButton {
                background-color: #81c784;
                color: white;
                padding: 6px;
                border-radius: 5px;
                font-weight: bold;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #eafaea;
            }
        """)

        # Tabel
        self.tableWidget.setAlternatingRowColors(True)
        self.resize(900, 600)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.load_data()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS money (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount TEXT,
                type TEXT,
                notes TEXT
            )
        """)
        self.conn.commit()

    def add_entry(self):
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        category = self.comboBoxCategory.currentText()
        amount = self.lineEditAmount.text().strip()
        type_ = self.comboBoxType.currentText()
        notes = self.textEditNotes.toPlainText().strip()

        if not amount:
            QMessageBox.warning(self, "Validation Error", "Amount cannot be empty.")
            return

        self.conn.execute(
            "INSERT INTO money (date, category, amount, type, notes) VALUES (?, ?, ?, ?, ?)",
            (date, category, amount, type_, notes)
        )
        self.conn.commit()

        self.load_data()
        self.clear_form()

    def load_data(self):
        self.tableWidget.setRowCount(0)
        cursor = self.conn.execute("SELECT date, category, amount, type, notes FROM money ORDER BY date DESC")
        for row_num, row_data in enumerate(cursor):
            self.tableWidget.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                if col_num == 2:  # Format kolom Amount
                    display_data = self.format_rupiah(data)
                else:
                    display_data = str(data)
                self.tableWidget.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(display_data))

    def clear_form(self):
        self.dateEdit.setDate(QDate.currentDate())
        self.comboBoxCategory.setCurrentIndex(0)
        self.lineEditAmount.clear()
        self.comboBoxType.setCurrentIndex(0)
        self.textEditNotes.clear()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"

        cursor = self.conn.execute("SELECT date, category, amount, type, notes FROM money ORDER BY date DESC")
        with open(path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Amount", "Type", "Notes"])
            writer.writerows(cursor)

        QMessageBox.information(self, "Export Complete", f"CSV exported to:\n{path}")

    def show_about(self):
        QMessageBox.information(
            self,
            "About Money Tracker",
            "💰 Money Tracker\n\nAplikasi pencatat pemasukan & pengeluaran.\nFitur: SQLite, format rupiah, export CSV.\n\nI Gede Manik Ariyasa\nF1D022046"
        )

    def format_rupiah(self, number):
        try:
            num = int(number)
            return f"Rp. {num:,}".replace(",", ".")
        except ValueError:
            return number

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MoneyTracker()
    window.show()
    sys.exit(app.exec_())
