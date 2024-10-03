from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt

class SalesHistoryViewer(QWidget):
    def __init__(self, order_history):
        super().__init__()
        self.order_history = order_history
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Satış Geçmişi')
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Satış Zamanı', 'Toplam Tutar'])
        self.tree.header().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tree)

        self.populate_tree()

        self.setLayout(layout)

    def populate_tree(self):
        for sale in reversed(self.order_history):
            root = QTreeWidgetItem(self.tree)
            root.setText(0, sale['time'])
            root.setText(1, f"{sale['total']:.2f} TL")

            for item in sale['items']:
                child = QTreeWidgetItem(root)
                child.setText(0, f"{item['name']} (x{item['quantity']})")
                child.setText(1, f"{item['price'] * item['quantity']:.2f} TL")

        self.tree.expandAll()