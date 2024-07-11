import wx
import os
from datetime import datetime

class ImageComparer(wx.Frame):
    def __init__(self, parent, basePath, filenames):
        super(ImageComparer, self).__init__(parent, title='变化检测标注审查V1')
        self.SetBackgroundColour(wx.Colour(192, 192, 192))  # 确保窗口的背景色已经设置为白色
        self.filenames = filenames
        self.basePath = basePath
        self.checkPath = os.path.join(basePath, 'check')
        self.screenshotPath = os.path.join(basePath, 'screenshot')
        os.makedirs(self.screenshotPath, exist_ok=True)
        os.makedirs(self.checkPath, exist_ok=True)
        self.progress_file = os.path.join(self.checkPath, 'progress.txt')  # 保存进度的文件名
        self.error_logPath = os.path.join(self.checkPath, 'error_log.txt') # 错误日志文件
        self.index = 0
        self.delected = {}
        self.InitUI()

    def CaptureScreen(self, event=None):
            # 获取窗口的显示区域大小
            screenshot_size = self.GetClientSize()
            
            # 创建一个wx.Bitmap对象
            screenshot = wx.Bitmap(screenshot_size.width, screenshot_size.height)
            
            # 创建wx.MemoryDC，用于绘制截图
            mem_dc = wx.MemoryDC()
            mem_dc.SelectObject(screenshot)

            # 创建wx.ClientDC，用于获取当前窗口的客户区
            client_dc = wx.ClientDC(self)
            
            # 将当前窗口的客户区绘制到mem_dc上
            mem_dc.Blit(0, 0, screenshot_size.width, screenshot_size.height, client_dc, 0, 0)
            
            # 取消选择wx.Bitmap，以便可以保存它
            mem_dc.SelectObject(wx.NullBitmap)
            
            # 定义截图的文件名和路径
            screenshot_filename = self.filenames[self.index]
            screenshot_path = os.path.join(self.screenshotPath, screenshot_filename)
            
            # 保存截图
            screenshot.SaveFile(screenshot_path, wx.BITMAP_TYPE_PNG)
            
            # 显示保存成功的提示
            wx.MessageBox(f'截图已保存到: {screenshot_path}', 'Save Success', wx.OK | wx.ICON_INFORMATION)

    def SaveProgress(self):
            # 将当前索引保存到文件
            with open(self.progress_file, 'w') as f:
                f.write(str(self.index))

    def LoadProgress(self):
        # 尝试读取进度文件
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                try:
                    self.index = int(f.read().strip())
                except ValueError:
                    self.index = 0  # 如果读取失败，重置索引为0
        else:
            self.index = 0  # 如果进度文件不存在，重置索引为0

    def OnClose(self, event):
        # 在窗口关闭事件中保存进度
        self.SaveProgress()
        self.Destroy()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 创建三个StaticBitmap用于显示图像
        self.bitmap_a = wx.StaticBitmap(panel, wx.ID_ANY)
        self.bitmap_b = wx.StaticBitmap(panel, wx.ID_ANY)
        self.bitmap_label = wx.StaticBitmap(panel, wx.ID_ANY)
        self.bitmap_infer = wx.StaticBitmap(panel, wx.ID_ANY)

        # 创建一个水平BoxSizer用于放置三个StaticBitmap
        hbox_images = wx.BoxSizer(wx.HORIZONTAL)
        hbox_images.Add(self.bitmap_a, 1, wx.ALL | wx.EXPAND, 5)
        hbox_images.Add(self.bitmap_b, 1, wx.ALL | wx.EXPAND, 5)
        hbox_images.Add(self.bitmap_label, 1, wx.ALL | wx.EXPAND, 5)
        hbox_images.Add(self.bitmap_infer, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox_images, 1, wx.EXPAND)  # 添加图像布局到垂直布局

        # 创建进度显示文本控件
        self.progress_text = wx.StaticText(panel, label="进度: 0/0", style=wx.ALIGN_LEFT)
        vbox.Add(self.progress_text, 0, wx.ALIGN_CENTER|wx.ALL, 5)  # 添加进度文本到布局

        # 创建第一个水平BoxSizer用于放置“上一个”和“下一个”按钮
        hbox_nav = wx.BoxSizer(wx.HORIZONTAL)
        btn_prev = wx.Button(panel, label='上一组')
        btn_prev.Bind(wx.EVT_BUTTON, self.OnPrev)
        hbox_nav.Add(btn_prev, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        btn_next = wx.Button(panel, label='下一组')
        btn_next.Bind(wx.EVT_BUTTON, self.OnNext)
        hbox_nav.Add(btn_next, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        vbox.Add(hbox_nav, 0, wx.ALIGN_CENTER|wx.ALL, 5)  # 添加导航按钮布局到垂直布局

        # 创建第二个水平BoxSizer用于放置“记录错误”和“复制picid”按钮
        hbox_actions = wx.BoxSizer(wx.HORIZONTAL)
        btn_error = wx.Button(panel, label='记录错误')
        btn_error.Bind(wx.EVT_BUTTON, self.OnRecordError)
        hbox_actions.Add(btn_error, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        btn_copy = wx.Button(panel, label='复制picid')
        btn_copy.Bind(wx.EVT_BUTTON, self.OnCopyFilename)
        hbox_actions.Add(btn_copy, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        # 创建保存截图按钮
        btn_save = wx.Button(panel, label='保存整个显示区域')
        btn_save.Bind(wx.EVT_BUTTON, self.CaptureScreen)
        hbox_actions.Add(btn_save, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        vbox.Add(hbox_actions, 0, wx.ALIGN_CENTER|wx.ALL, 5)  # 添加动作按钮布局到垂直布局

        

        panel.SetSizer(vbox)
        self.SetSize((1100, 400))

        # 显示第一组图像
        self.ShowCurrentSet()

    def ShowCurrentSet(self):
        # 更新进度文本控件
        total_files = len(self.filenames)
        self.progress_text.SetLabel(f"进度: {self.index + 1}/{total_files}")
        # 加载并显示当前索引的图像
        for bitmap, folder in zip([self.bitmap_a, self.bitmap_b, self.bitmap_label, self.bitmap_infer],
                                   ['A', 'B', 'Label', 'Infer']):
            filename = self.filenames[self.index]
            image_path = f'{self.basePath}/{folder}/{filename}'
            image = wx.Image(image_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            bitmap.SetBitmap(image)

    def OnNext(self, event):
        if self.index < len(self.filenames) - 1:
            self.index += 1
            self.ShowCurrentSet()
    
    # 新增：事件处理函数，用于回退到上一组图像
    def OnPrev(self, event):
        if self.index > 0:  # 确保索引不会变成负数
            self.index -= 1
            self.ShowCurrentSet()  # 显示上一组图像
    
    def OnRecordError(self, event):
            # 获取当前文件名
            filename = self.filenames[self.index]

            # 创建一个弹窗询问用户是否确认记录错误
            message = ''
            dlg = wx.MessageDialog(self, message, '确认错误', wx.YES_NO | wx.ICON_QUESTION)
            
            # 显示弹窗并获取用户响应
            if filename in self.delected:
                # 已经删除过了
                wx.MessageBox('不能重复记录', 'Cancelled', wx.OK | wx.ICON_INFORMATION)
            elif dlg.ShowModal() == wx.ID_YES:
                # 获取当前时间，并格式化输出
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 用户点击了"是"，记录错误
                
                with open(self.error_logPath, 'a') as f:
                    f.write(f"{now} {filename}\n")
                self.delected[filename] = 1
                wx.MessageBox(f'{filename}', 'Error Recorded', wx.OK | wx.ICON_INFORMATION)
            else:
                # 用户点击了"否"，不记录错误
                wx.MessageBox('用户取消', 'Cancelled', wx.OK | wx.ICON_INFORMATION)
            
            # 关闭弹窗
            dlg.Destroy()

    def OnCopyFilename(self, event):
        # 获取当前文件名
        filename = self.filenames[self.index]
        # 将文件名复制到剪贴板
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(filename))
            wx.TheClipboard.Close()
            wx.MessageBox(f'picid已复制到系统剪切板: {filename}', 'Copy Success', wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App(False)
    # basePath = '/Users/zgf/Desktop/数据集/png/GC/验证用/GC107_21_108_23_png'
    # # filenames是核心
    # filenames = os.listdir(basePath+'/A')  # 替换为实际的文件名列表
    # ex = ImageComparer(None, basePath, filenames)
    # ex.Show()
    # app.MainLoop()
    # 创建一个对话框让用户输入基础路径
    with wx.TextEntryDialog(None, "请输入路径:", "设置ABlabel路径") as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            basePath = dlg.GetValue()
            # 检查路径是否存在
            if os.path.exists(basePath):
                # 假设文件夹结构是 basePath/A, basePath/B, basePath/Label
                filenames = os.listdir(os.path.join(basePath, 'A'))  # 替换为实际的文件名列表
                ex = ImageComparer(None, basePath, filenames)
                ex.LoadProgress()  # 加载进度
                ex.ShowCurrentSet()  # 显示当前的图像组
                ex.Bind(wx.EVT_CLOSE, ex.OnClose)  # 绑定关闭事件
                ex.Show()

                app.MainLoop()
            else:
                wx.MessageBox("指定的路径不存在", "Error", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("未指定路径程序退出", "Application Exit", wx.OK | wx.ICON_INFORMATION)