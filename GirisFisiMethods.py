from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
import pyodbc
from GirisFisiUi import Ui_Form
from database import connection_string
from datetime import datetime
class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton_urunekle.clicked.connect(self.urunEkle)  #urunekle butonu
        self.ui.pushButton_Ara.clicked.connect(self.Arama)            #arama butonu
        self.ui.pushButton_hepsinikaydet.clicked.connect(self.HepsiniKaydet)    #hepsinikaydet butonu
        self.satir = 0
        self.row = None


        connection = pyodbc.connect(connection_string)   #veritabanı bağlantısı
        cursor = connection.cursor()   #veritabanı bağlantısı

        self.new_fis_no = self.getNextFisNo(cursor)         #fisno
        self.ui.lineEdit_fisno.setText(self.new_fis_no)
        self.ui.lineEdit_fisno.setReadOnly(True)         #fisno sadece okuma
        self.currentDate = datetime.now().strftime("%Y-%m-%d")         #tarih ayarlama(database'e tarih bilgisini aktarmak icin)
    def urunEkle(self):  #urunekle methodu
        Miktar = self.ui.lineEdit_miktar.text()
        try:
            Miktar = float(Miktar)
            if self.row:  # self.row dolu mu kontrol et
                self.ui.tableWidget.insertRow(self.satir)
                for i, value in enumerate(self.row):                #tablewidget ' e veri eklemek icin
                    self.ui.tableWidget.setItem(self.satir, i, QTableWidgetItem(str(value)))
                self.ui.tableWidget.setItem(self.satir, 4, QTableWidgetItem(str(Miktar)))
                self.ui.tableWidget.setItem(self.satir, 5, QTableWidgetItem(str(Miktar * float(self.row[3]))))
                self.satir += 1
                self.ui.lineEdit_miktar.clear()    #miktar line'ini temizleme
                self.ui.lineEdit_stokkodu.clear() #stokkodu line'ini temizleme
            else:
                QMessageBox.warning(self, "Hata", "Önce bir stok kodu arayın.")
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir miktar girin.")

        self.ui.tableWidget_2.clearContents()     #tablewidget ekranını temizleme

    def HepsiniKaydet(self):
        try:
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()

            for row in range(self.ui.tableWidget.rowCount()):   # 2.tablewidget e veri eklemek icin
                StokKodu = self.ui.tableWidget.item(row, 0).text()
                StokAdi = self.ui.tableWidget.item(row, 1).text()
                Birim = self.ui.tableWidget.item(row, 2).text()
                BirimFiyat = float(self.ui.tableWidget.item(row, 3).text())
                Miktar = float(self.ui.tableWidget.item(row, 4).text())
                ToplamTutar = float(self.ui.tableWidget.item(row, 5).text())

                cursor.execute('''
                    INSERT INTO GirisFisi (FisNo, StokKodu, StokAdi, Birim, BirimFiyat, Miktar, ToplamTutar,Tarih)
                    VALUES (?, ?, ?, ?, ?, ?, ?,?)
                ''', (self.new_fis_no, StokKodu, StokAdi, Birim, BirimFiyat, Miktar, ToplamTutar,self.currentDate))

            connection.commit()

            print(f"Data saved to database with FisNo: {self.new_fis_no}")

            self.ui.tableWidget.clearContents()
            self.ui.tableWidget_2.clearContents()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget_2.setRowCount(0)
            self.satir = 0
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {e}")

        self.new_fis_no = self.getNextFisNo(cursor) #hepsinikaydetten sonra fisno yu guncellemek ıcın
        self.ui.lineEdit_fisno.setText(self.new_fis_no)
        self.ui.lineEdit_fisno.setReadOnly(True)
        connection.close()

    def Arama(self):
        StokKodu = self.ui.lineEdit_stokkodu.text()

        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM StokKarti WHERE stok_kodu = ?", (StokKodu,))
        self.row = cursor.fetchone()
        if self.row:
            self.ui.tableWidget_2.setRowCount(1)
            for i, value in enumerate(self.row):
                self.ui.tableWidget_2.setItem(0, i, QTableWidgetItem(str(value)))
        else:
            QMessageBox.warning(self, "Arama Sonucu", "Arama yapabilmek için stok kodu giriniz.")

    def getNextFisNo(self, cursor):
        cursor.execute('SELECT TOP 1 FisNo FROM GirisFisi ORDER BY FisNo DESC')
        last_fis = cursor.fetchone()
        if last_fis is None:
            return 'G001'
        last_fis_no = last_fis[0]
        last_number = int(last_fis_no[1:])
        new_number = last_number + 1
        new_fis_no = f'G{new_number:03d}'
        return new_fis_no

