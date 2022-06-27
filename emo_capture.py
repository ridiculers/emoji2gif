import win32gui
import win32ui
import win32con
import win32api
import matplotlib.pyplot as plt
import os
import imageio
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal


class Worker(QThread):
    signal_out = pyqtSignal(str)

    def __init__(self, plot_rect, amount_frames=50, frame_duration=0.05):
        super(Worker, self).__init__()
        self.rect = plot_rect
        self.amount_frames = amount_frames
        self.frame_duration = frame_duration

    def run(self) -> None:
        mouse_x, mouse_y = self.mouse_locate(self.rect)
        self.photo_capture()
        self.signal_out.emit('capture done')
        self.img_edit(mouse_x, mouse_y)
        self.img_gif()
        self.signal_out.emit('stop')

    def photo_capture(self):
        try:
            os.makedirs('./temporary_image_folder')
        except OSError as e:
            print(e)
            print('请注意文件夹 temporary_image_folder 是否已存在.')
        else:
            for num in range(self.amount_frames):
                hwndDC = win32gui.GetWindowDC(0)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                saveBitMap = win32ui.CreateBitmap()
                MoniterDev = win32api.EnumDisplayMonitors(None, None)
                w = MoniterDev[0][2][2]
                h = MoniterDev[0][2][3]
                saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
                saveDC.SelectObject(saveBitMap)
                saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
                saveBitMap.SaveBitmapFile(saveDC, './temporary_image_folder/{}.jpg'.format(num))

    @staticmethod
    def mouse_locate(plot_rect):
        if plot_rect:
            return (plot_rect[0], plot_rect[1]), (plot_rect[0] + plot_rect[2], plot_rect[1] + plot_rect[3])
        else:
            return None

    def img_edit(self, x=None, y=None):
        for num in range(self.amount_frames):
            img = plt.imread('./temporary_image_folder/{}.jpg'.format(num))
            img = img[x[1]:y[1], x[0]:y[0]]
            plt.imsave('./temporary_image_folder/{}.jpg'.format(num), img)

    def img_gif(self):
        file_path = os.listdir('./temporary_image_folder')
        img_list = []
        frame = []

        for file_name in file_path:
            if '.jpg' in file_name:
                img_list.append(file_name)
            else:
                continue
        img_list.sort(key=lambda x: int(x[:-4]))

        for img in img_list:
            frame.append(imageio.imread('./temporary_image_folder/{}'.format(img)))
        imageio.mimsave('./emo.gif', frame, 'GIF', duration=self.frame_duration)

        for img in img_list:
            os.remove('./temporary_image_folder/{}'.format(img))

        os.rmdir('./temporary_image_folder')
        print('Finished.Gif is at {}'.format(os.getcwd()))
