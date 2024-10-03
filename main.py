from sales_history_viewer import SalesHistoryViewer
from datetime import datetime
import sys
import requests
import pickle
import os
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QShortcut, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QLabel, QMessageBox, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QInputDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QFont

def is_valid_password(password):
    if ' ' in password or any(ord(char) > 127 for char in password):
        return False
    return True

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_user_data()

    def initUI(self):
        self.setWindowTitle('Giriş Formu')
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Kullanıcı adı')
        layout.addWidget(self.username)

        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Şifre')
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        hbox_checkbox = QHBoxLayout()
        self.remember = QCheckBox('Beni Hatırla', self)
        self.show_password = QCheckBox('Şifreyi göster', self)
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        hbox_checkbox.addWidget(self.remember)
        hbox_checkbox.addWidget(self.show_password)
        layout.addLayout(hbox_checkbox)

        hbox_buttons = QHBoxLayout()
        self.login_button = QPushButton('Giriş yap', self)
        self.register_button = QPushButton('Kayıt ol', self)
        hbox_buttons.addWidget(self.login_button)
        hbox_buttons.addWidget(self.register_button)
        layout.addLayout(hbox_buttons)

        self.setLayout(layout)

        self.register_button.clicked.connect(self.open_register_form)
        self.login_button.clicked.connect(self.login)

    def toggle_password_visibility(self, state):
        if state == 2:
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def open_register_form(self):
        self.register_form = RegisterForm()
        self.register_form.show()

    def login(self):
        username = self.username.text()
        password = self.password.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Hata', 'Lütfen kullanıcı adı ve şifre girin.')
            return

        if not is_valid_password(password):
            QMessageBox.warning(self, 'Hata', 'Şifre boşluk veya Türkçe karakter içermemelidir.')
            return
        
        response = requests.post('http://localhost/login.php', data={
            'username': username,
            'password': password
        })

        if response.text == 'success':
            QMessageBox.information(self, 'Başarılı', 'Giriş başarılı!')
            if self.remember.isChecked():
                self.save_user_data(username, password)
            self.open_main_menu()
        else:
            QMessageBox.warning(self, 'Hata', 'Giriş başarısız. Kullanıcı adı veya şifre hatalı.')

    def save_user_data(self, username, password):
        data = {'username': username, 'password': password}
        with open('data/user.pkl', 'wb') as f:
            pickle.dump(data, f)

    def load_user_data(self):
        if os.path.exists('data/user.pkl'):
            with open('data/user.pkl', 'rb') as f:
                data = pickle.load(f)
                self.username.setText(data['username'])
                self.password.setText(data['password'])
                self.remember.setChecked(True)

    def open_main_menu(self):
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close()


class RegisterForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Kayıt Formu')
        self.setGeometry(400, 300, 300, 300)

        layout = QVBoxLayout()

        self.fullname = QLineEdit(self)
        self.fullname.setPlaceholderText('Ad Soyad')
        layout.addWidget(self.fullname)

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Kullanıcı Adı')
        layout.addWidget(self.username)

        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Şifre')
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.password_confirm = QLineEdit(self)
        self.password_confirm.setPlaceholderText('Şifre tekrar')
        self.password_confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_confirm)

        self.contact = QLineEdit(self)
        self.contact.setPlaceholderText('İletişim numarası')
        layout.addWidget(self.contact)

        self.show_password = QCheckBox('Şifreyi göster', self)
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)

        self.register_button = QPushButton('Kayıt ol', self)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.register_button.clicked.connect(self.register)

    def toggle_password_visibility(self, state):
        if state == 2:
            self.password.setEchoMode(QLineEdit.Normal)
            self.password_confirm.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.password_confirm.setEchoMode(QLineEdit.Password)

    def register(self):
        if not all([self.fullname.text(), self.username.text(), self.password.text(), 
                    self.password_confirm.text(), self.contact.text()]):
            QMessageBox.warning(self, 'Hata', 'Lütfen tüm alanları doldurun.')
        elif self.password.text() != self.password_confirm.text():
            QMessageBox.warning(self, 'Hata', 'Şifreler eşleşmiyor.')
        elif not is_valid_password(self.password.text()):
            QMessageBox.warning(self, 'Hata', 'Şifre boşluk veya Türkçe karakter içermemelidir.')
        else:
            response = requests.post('http://localhost/register.php', data={
                'fullname': self.fullname.text(),
                'username': self.username.text(),
                'password': self.password.text(),
                'contact': self.contact.text()
            })

            if response.text == 'success':
                QMessageBox.information(self, 'Başarılı', 'Kayıt başarıyla tamamlandı.')
                self.close()
            else:
                QMessageBox.warning(self, 'Hata', 'Kayıt işlemi başarısız oldu. Lütfen tekrar deneyin.')

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ana Menü')
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.barcode_button = QPushButton('Barkod Okuyucu', self)
        self.barcode_button.clicked.connect(self.open_barcode_reader)
        layout.addWidget(self.barcode_button)

        self.ledger_button = QPushButton('Veresiye Defteri', self)
        layout.addWidget(self.ledger_button)

        self.setLayout(layout)

    def open_barcode_reader(self):
        self.barcode_reader = BarcodeReader()
        self.barcode_reader.show()
        self.close()

class BarcodeReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cart = {}
        self.load_products()
        self.load_order_history()


    def initUI(self):
        self.setWindowTitle('Barkod Okuyucu')
        self.showFullScreen()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.barcode_input = QLineEdit(self)
        self.barcode_input.setPlaceholderText('Barkod girin')
        self.barcode_input.returnPressed.connect(self.add_to_cart)
        layout.addWidget(self.barcode_input)

        button_layout = QHBoxLayout()
        self.sell_button = QPushButton('Satış Yap (F1)', self)
        self.remove_button = QPushButton('Ürün Sil (F8)', self)
        self.clear_button = QPushButton('Sepeti Boşalt (F9)', self)
        self.change_quantity_button = QPushButton('Adet Seç (F5)', self)

        self.view_history_button = QPushButton('Satış Geçmişini Görüntüle', self)
        self.view_history_button.clicked.connect(self.open_sales_history)
        self.view_history_button.setMinimumHeight(50)
        layout.addWidget(self.view_history_button)
        
        button_height = 50
        for button in [self.sell_button, self.remove_button, self.clear_button, self.change_quantity_button]:
            button.setMinimumHeight(button_height)
        
        button_layout.addWidget(self.sell_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.change_quantity_button)
        layout.addLayout(button_layout)

        self.cart_table = QTableWidget(self)
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(['Ürün Barkodu', 'Ürün Adı', 'Fiyatı', 'Adet'])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.cart_table)

        self.total_label = QLabel('Toplam: 0.00 TL', self)
        self.total_label.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(16)
        self.total_label.setFont(font)
        layout.addWidget(self.total_label)

        self.add_product_button = QPushButton('Ürün Ekle', self)
        self.add_product_button.clicked.connect(self.open_add_product)
        layout.addWidget(self.add_product_button, alignment=Qt.AlignRight)

        self.sell_button.clicked.connect(self.sell)
        self.remove_button.clicked.connect(self.remove_item)
        self.clear_button.clicked.connect(self.clear_cart)
        self.change_quantity_button.clicked.connect(self.change_quantity)

        QShortcut(QKeySequence("F1"), self, self.sell)
        QShortcut(QKeySequence("F8"), self, self.remove_item)
        QShortcut(QKeySequence("F9"), self, self.clear_cart)
        QShortcut(QKeySequence("F5"), self, self.change_quantity)

    
    def add_to_cart(self):
        barcode = self.barcode_input.text()
        if barcode in self.products:
            product = self.products[barcode]
            if barcode in self.cart:
                self.cart[barcode]['quantity'] += 1
                self.update_cart_table()
            else:
                self.cart[barcode] = {
                    'name': product['name'],
                    'price': product['sell_price'],
                    'quantity': 1
                }
                self.add_to_cart_table(barcode)
            self.update_total()
        else:
            QMessageBox.warning(self, 'Hata', 'Ürün bulunamadı!')
        self.barcode_input.clear()

    def add_to_cart_table(self, barcode):
        row_position = self.cart_table.rowCount()
        self.cart_table.insertRow(row_position)
        self.cart_table.setItem(row_position, 0, QTableWidgetItem(barcode))
        self.cart_table.setItem(row_position, 1, QTableWidgetItem(self.cart[barcode]['name']))
        self.cart_table.setItem(row_position, 2, QTableWidgetItem(str(self.cart[barcode]['price'])))
        self.cart_table.setItem(row_position, 3, QTableWidgetItem(str(self.cart[barcode]['quantity'])))

    def update_cart_table(self):
        self.cart_table.setRowCount(0)
        for barcode, item in self.cart.items():
            row_position = self.cart_table.rowCount()
            self.cart_table.insertRow(row_position)
            self.cart_table.setItem(row_position, 0, QTableWidgetItem(barcode))
            self.cart_table.setItem(row_position, 1, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row_position, 2, QTableWidgetItem(str(item['price'])))
            self.cart_table.setItem(row_position, 3, QTableWidgetItem(str(item['quantity'])))

    def update_total(self):
        total = sum(item['price'] * item['quantity'] for item in self.cart.values())
        self.total_label.setText(f'Toplam: {total:.2f} TL')

    def sell(self):
        if not self.cart:
            QMessageBox.warning(self, 'Hata', 'Sepet boş!')
            return
        
        total = sum(item['price'] * item['quantity'] for item in self.cart.values())
        sale_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sale_record = {
            'time': sale_time,
            'total': total,
            'items': [
                {
                    'barcode': barcode,
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': item['quantity']
                } for barcode, item in self.cart.items()
            ]
        }
        
        self.order_history.append(sale_record)
        self.save_order_history()
        
        QMessageBox.information(self, 'Başarılı', 'Satış tamamlandı!')
        self.clear_cart()

    def load_order_history(self):
        if os.path.exists('data/orderHistory.pkl'):
            with open('data/orderHistory.pkl', 'rb') as f:
                self.order_history = pickle.load(f)
        else:
            self.order_history = []

    def save_order_history(self):
        with open('data/orderHistory.pkl', 'wb') as f:
            pickle.dump(self.order_history, f)

    def open_sales_history(self):
        self.sales_history_viewer = SalesHistoryViewer(self.order_history)
        self.sales_history_viewer.show()

    def remove_item(self):
        current_row = self.cart_table.currentRow()
        if current_row >= 0:
            barcode = self.cart_table.item(current_row, 0).text()
            del self.cart[barcode]
            self.update_cart_table()
            self.update_total()

    def clear_cart(self):
        self.cart.clear()
        self.cart_table.setRowCount(0)
        self.update_total()

    def change_quantity(self):
        current_row = self.cart_table.currentRow()
        if current_row >= 0:
            barcode = self.cart_table.item(current_row, 0).text()
            quantity, ok = QInputDialog.getInt(self, "Adet Seç", "Yeni adet:", 
                                               self.cart[barcode]['quantity'], 1, 100)
            if ok:
                self.cart[barcode]['quantity'] = quantity
                self.update_cart_table()
                self.update_total()

    def load_products(self):
        if os.path.exists('data/products.pkl'):
            with open('data/products.pkl', 'rb') as f:
                self.products = pickle.load(f)
        else:
            self.products = {}

    def save_products(self):
        with open('data/products.pkl', 'wb') as f:
            pickle.dump(self.products, f)

    def open_add_product(self):
        self.add_product_form = AddProductForm(self)
        self.add_product_form.show()



class AddProductForm(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ürün Ekle')
        self.setGeometry(400, 300, 300, 200)

        layout = QVBoxLayout()

        self.barcode_input = QLineEdit(self)
        self.barcode_input.setPlaceholderText('Barkod')
        layout.addWidget(self.barcode_input)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Ürün Adı')
        layout.addWidget(self.name_input)

        self.buy_price_input = QLineEdit(self)
        self.buy_price_input.setPlaceholderText('Alış Fiyatı')
        layout.addWidget(self.buy_price_input)

        self.sell_price_input = QLineEdit(self)
        self.sell_price_input.setPlaceholderText('Satış Fiyatı')
        layout.addWidget(self.sell_price_input)

        self.save_button = QPushButton('Kaydet', self)
        self.save_button.clicked.connect(self.save_product)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_product(self):
        barcode = self.barcode_input.text()
        name = self.name_input.text()
        buy_price = float(self.buy_price_input.text())
        sell_price = float(self.sell_price_input.text())

        if not all([barcode, name, buy_price, sell_price]):
            QMessageBox.warning(self, 'Hata', 'Lütfen tüm alanları doldurun!')
            return

        self.parent.products[barcode] = {
            'name': name,
            'buy_price': buy_price,
            'sell_price': sell_price
        }
        self.parent.save_products()
        QMessageBox.information(self, 'Başarılı', 'Ürün kaydedildi!')
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_form = LoginForm()
    login_form.show()
    sys.exit(app.exec_())