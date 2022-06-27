import sys
import os
import getopt
from PyQt5.QtGui import QMovie
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRect
from emo_capture import Worker


class Pushbutton(QPushButton):

    def __init__(self, text=None, color=None, parent=None):
        super(Pushbutton, self).__init__(parent)
        self.setWindowOpacity(1)
        self.setText(text)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(
            'font-size:20px;color:{};background-color: rgb(255,255,255);border:none;padding:4px 8px'.format(color))
        self.hide()
        self.resize(36, 28)


class Drawing(QWidget):

    def __init__(self, parent=None):
        super(Drawing, self).__init__(parent)
        self.desktop = QApplication.desktop()
        self.screen_rect = self.desktop.screenGeometry()
        self.resize(self.screen_rect.width(), self.screen_rect.height())
        self.setWindowOpacity(0.6)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color:rgb(10,10,10)")
        self.rect = None
        self.bt1 = Pushbutton(text='√', color='green', parent=self)
        self.bt2 = Pushbutton(text='×', color='red', parent=self)
        self.worker = None
        self.bt1.clicked.connect(self.worker_create)
        self.bt2.clicked.connect(self.close)
        self.child_widget, self.child_label = self.gif_widget()

    def worker_create(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.worker = Worker(self.rect, amount_frames, frame_duration)
        self.worker.signal_out.connect(self.signal_handle)
        self.child_label.move(self.rect[0] + int(self.rect[2] / 2 - 100), self.rect[1] + int(self.rect[3] / 2) - 100)
        self.worker.start()

    def gif_widget(self):
        child = QWidget()
        child.setWindowFlags(Qt.FramelessWindowHint)
        child.setAttribute(Qt.WA_TranslucentBackground, True)
        child.resize(self.screen_rect.width(), self.screen_rect.height())
        label = QLabel(child)
        gif = QMovie('./loading.gif')
        label.setMovie(gif)
        gif.start()
        return child, label

    def signal_handle(self, string):
        if string == 'capture done':
            self.setAttribute(Qt.WA_TranslucentBackground, False)
            self.child_widget.show()
        if string == 'stop':
            self.child_widget.close()
            self.close()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.rect:
            rect = QRect(self.rect[0], self.rect[1], self.rect[2], self.rect[3])
            qp.fillRect(rect, QColor(255, 255, 255, 255))
            self.draw_rect(qp)
        qp.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def draw_rect(self, qp):
        pen = QPen(Qt.green, 2)
        qp.setPen(pen)
        qp.drawRect(*self.rect)

    def mousePressEvent(self, event):
        self.rect = (event.x(), event.y(), 0, 0)
        self.bt1.hide()
        self.bt2.hide()

    def mouseReleaseEvent(self, event):
        self.bt1.move(event.x() - self.bt1.width(), event.y())
        self.bt2.move(event.x() - 2 * self.bt1.width(), event.y())
        self.bt1.show()
        self.bt2.show()

    def mouseMoveEvent(self, event):
        start_x, start_y = self.rect[0:2]
        self.rect = (start_x, start_y, event.x() - start_x, event.y() - start_y)
        self.update()


if __name__ == '__main__':

    current_path = os.path.dirname(__file__)
    print(current_path)
    os.chdir(current_path)

    system_argv = sys.argv
    app = QApplication(system_argv)
    amount_frames = 50
    frame_duration = 0.05
    need_help = False
    opts, args = getopt.getopt(system_argv[1:], 'hf:d:', ['help', 'amount_frames=', 'frame_duration='])
    for opt, arg in opts:
        if opt == "-h" or opt == '--help':
            print('You can try \'python ./capture_ui.py\',')
            print('then the default value of amount_frames is 50,')
            print('and the default value of frame_duration is 0.05.')
            print('Or you can also try:')
            print('\'python ./capture_ui.py -f 20 -d 0.04\'')
            print('or')
            print('\'python ./capture_ui.py --amount_frames=20 --frame_duration=0.1\'')
            need_help = True
            break
        elif opt == '-f' or opt == '--amount_frames':
            amount_frames = int(arg)
        elif opt == '-d' or opt == '--frame_duration':
            frame_duration = float(arg)
    if not need_help:
        demo = Drawing()
        demo.show()
        sys.exit(app.exec_())
