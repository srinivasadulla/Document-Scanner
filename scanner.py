import cv2
import numpy as np
import argparse
from transform import transform
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFilter
import imutils
import tkinter.font as font
import pytesseract
import os



class DocumentScanner:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1000x800+250+50')

        self.window_width = self.root.winfo_width()
        self.window_height = self.root.winfo_height()


        self.filepath = None
        self.label = Label(self.root, bg="red")

        self.my_font = font.Font(family='Helvetica', weight="bold", size=18)

        self.frame = Frame(self.root, bg='#80c1ff', bd=5)
        self.frame.place(relx=0.5, rely=0.02, width=800, height=60, anchor='n')

        self.frame2 = Frame(self.root, bg='#80c1ff', bd=5)
        self.frame2.place(relx=0.5, rely=0.11, width=150, height=50, anchor='n')

        self.entry = Entry(self.frame)
        self.entry.insert(0, 'Please select the Path')
        self.entry.place(relwidth=0.67, relheight=1)

        self.select_button = Button(self.frame, text='Select', command=self.getPath)
        self.select_button["font"] = self.my_font
        self.select_button.place(relx=0.69, relheight=1, relwidth=0.15)
        self.select_button_status = 0

        self.load_button = Button(self.frame, text='Load', command=self.loadImage)
        self.load_button["font"] = self.my_font
        self.load_button.place(relx=0.85, relheight=1, relwidth=0.15)
        self.load_button_status = 0

        self.scan_button = Button(self.frame2, text='Scan', fg="red", bg="green", command=lambda:self.scan_image(0))
        self.scan_button["font"] = self.my_font
        self.scan_button.place(relheight=1, relwidth=1)
        self.scan_button_status = 0

        self.ocr_button = Button(self.root, text='>>', fg="green", bg="light blue", anchor="center", command=self.ocr_transcript)
        self.ocr_button["font"] = font.Font(family='Helvetica', weight="bold", size=25)
        self.ocr_button.place(relheight=0.09, relwidth=0.055, relx=(self.window_width/2.1), rely=self.window_height/2)
        self.ocr_button_status = 0

        self.frame3 = Frame(self.root, bg='#80c1ff', bd=5)
        self.frame3.place(relx=0.25, rely=0.93, width=300, height=50, anchor='n')

        self.cw_image = Image.open("cw.png")
        self.cw_image = self.cw_image.resize((30, 30), Image.ANTIALIAS)
        self.cw_image = ImageTk.PhotoImage(self.cw_image)
        self.ccw_image = Image.open("ccw.png")
        self.ccw_image = self.ccw_image.resize((30, 30), Image.ANTIALIAS)
        self.ccw_image = ImageTk.PhotoImage(self.ccw_image) 

        self.cw_button = Button(self.frame3, text="hello", image=self.cw_image, anchor="center", command=self.cw_rotate)
        self.cw_button.place(relheight=1, relwidth=0.2, relx=0.01, rely=0)      

        self.ccw_button = Button(self.frame3, image=self.ccw_image, anchor="center", command=self.ccw_rotate)
        self.ccw_button.place(relheight=1, relwidth=0.2, relx=0.25, rely=0)

        self.save_button = Button(self.frame3, text="Save", anchor="center", command=self.save_image)
        self.save_button.place(relheight=1, relwidth=0.3, relx=0.65, rely=0)

        self.bw_button_status = 0

        self.canvas = Canvas(root, bg="black")

        self.canvas.place(relx=0.25, rely=0.18, relheight=0.75, relwidth= 0.45, anchor="n")

        self.canvas2 = Canvas(root, bg="white")

        self.canvas2.place(relx=0.75, rely=0.18, relheight=0.75, relwidth= 0.45, anchor="n")

        self.canvas.bind('<B1-Motion>', self.move)

        self.canvas.bind('<ButtonRelease-1>', self.release)
        

    def getPath(self):
        self.filepath = filedialog.askopenfilename(title="Select an Image", filetypes=(("image files", "*.png *.jpg"), ("all files", "*.*")))
        self.entry.delete(0, "end")
        self.entry.insert(0, self.filepath)
        if len(self.filepath) > 0:
            self.select_button_status = 1

    def loadImage(self):
        if self.select_button_status == 0:
            self.label.config(text="Please select image path before loading...")
            self.label.place(relx=0.15, rely=0.13)
            return
        self.label.place_forget()

        self.orig_image = Image.open(self.filepath)
        self.orig_width, self.orig_height = self.orig_image.size

        self.img_canvas_ratio = (0.98, 0.75)

        self.find_edges()
        self.canvas.delete("all")
        self.display(0)
        self.ocr_button.bind("<Configure>", self.handle_configure)
        self.load_button_status = 1
        self.scan_button_status = 0
        self.ocr_button_status = 0


    def find_edges(self):

        cv_image = np.array(self.orig_image) 
        # Convert RGB to BGR 
        cv_image = cv_image[:, :, ::-1].copy() 

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:
            
            c = max(contours, key=cv2.contourArea)

            p = cv2.arcLength(c, True)

            src = cv2.approxPolyDP(c, 0.02*p, True)
            self.src_pts = []

            for i in src:
                self.src_pts.append(tuple(i[0]))


    def display(self, flag):
        
        self.canvas_img_width = self.img_canvas_ratio[0] * self.canvas.winfo_width()

        self.canvas_img_height = self.img_canvas_ratio[1] * self.canvas.winfo_height()

        self.canvas_img_size_ratio = self.canvas_img_height / self.canvas_img_width
        
        self.resized_image = self.resize_image(self.orig_image)
        self.re_width =  self.resized_image.size[0]
        self.re_height = self.resized_image.size[1]
        self.reduction_ratio = self.re_height / self.orig_height

        self.resize_points()

        if flag==0:
            
            self.photo1= ImageTk.PhotoImage(self.resized_image)
            self.root.photo = self.photo1

            self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.photo1, anchor="center")

        self.lines = []
        self.circles = []

        pt1 = self.re_src_pts_c_f[0]
        pt2 = self.re_src_pts_c_f[1]
        pt3 = self.re_src_pts_c_f[2]
        pt4 = self.re_src_pts_c_f[3]

        self.lines.append(self.canvas.create_line(pt1[0], pt1[1], pt2[0], pt2[1], fill="red", width=5))
        self.lines.append(self.canvas.create_line(pt2[0], pt2[1], pt3[0], pt3[1], fill="red", width=5))
        self.lines.append(self.canvas.create_line(pt3[0], pt3[1], pt4[0], pt4[1], fill="red", width=5))
        self.lines.append(self.canvas.create_line(pt4[0], pt4[1], pt1[0], pt1[1], fill="red", width=5))

        self.circles.append(self.canvas.create_oval(pt1[0]-10, pt1[1]-10, pt1[0]+10, pt1[1]+10, fill="blue", outline="#DDD", width=4))
        self.circles.append(self.canvas.create_oval(pt2[0]-10, pt2[1]-10, pt2[0]+10, pt2[1]+10, fill="blue", outline="#DDD", width=4))
        self.circles.append(self.canvas.create_oval(pt3[0]-10, pt3[1]-10, pt3[0]+10, pt3[1]+10, fill="blue", outline="#DDD", width=4))
        self.circles.append(self.canvas.create_oval(pt4[0]-10, pt4[1]-10, pt4[0]+10, pt4[1]+10, fill="blue", outline="#DDD", width=4))



    def resize_image(self, img):
        img_width = img.size[0]
        img_height = img.size[1]

        if (img_width > self.canvas_img_width) or (img_height > self.canvas_img_height):
            if img_height/img_width > self.canvas_img_size_ratio:
                temp_h = self.canvas_img_height
                red_ratio = (temp_h / img_height)
                temp_w = img_width * red_ratio
            else:
                temp_w = self.canvas_img_width
                red_ratio = (temp_w / img_width)
                temp_h = img_height * red_ratio
        else:
            temp_h = img_height
            temp_w = img_width
        
        re_img = img.resize((int(temp_w), int(temp_h)), Image.ANTIALIAS)

        return re_img
        

    def resize_points(self):
        self.re_src_pts_c_f = []
        self.re_src_pts_i_f = []

        for pt in self.src_pts:
            self.re_src_pts_c_f.append((int(pt[0]*self.reduction_ratio)+((self.canvas.winfo_width() - self.re_width)/2), int(pt[1]*self.reduction_ratio)+((self.canvas.winfo_height() - self.re_height)/2)))
            self.re_src_pts_i_f.append((int(pt[0]*self.reduction_ratio), int(pt[1]*self.reduction_ratio)))

    
    def distance(self, pnt1, pnt2):
        return np.sqrt((pnt1[0]-pnt2[0])**2 + (pnt1[1]-pnt2[1])**2)

    
    def move(self, pointer):
        #This function is called for movement with mouse click
        pointer_pos = (pointer.x, pointer.y)
        for index, pt in enumerate(self.re_src_pts_c_f):
            dst = self.distance(pt, pointer_pos)
            if dst<25:
                
                zoom_window = self.crop(self.re_src_pts_i_f[index])
                tk_zoom_img = ImageTk.PhotoImage(zoom_window)
                root.photo = tk_zoom_img

                self.zoom_window_img = self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()*0.1, image=tk_zoom_img, anchor="center")
                self.zoom_center_line = []
                self.zoom_center_h_line = self.canvas.create_line(self.canvas.winfo_width()/2 - 10, self.canvas.winfo_height()*0.1, self.canvas.winfo_width()/2 + 10, self.canvas.winfo_height()*0.1, fill="black", width=2)
                self.zoom_center_v_line = self.canvas.create_line(self.canvas.winfo_width()/2, self.canvas.winfo_height()*0.1 - 10, self.canvas.winfo_width()/2, self.canvas.winfo_height()*0.1 + 10, fill="black", width=2)

                for i in range(4):
                    self.canvas.delete(self.lines[i])
                    self.canvas.delete(self.circles[i])
                
                #Update the new points of the document
                self.src_pts[index] = ((pointer.x - ((self.canvas.winfo_width() - self.re_width)/2))/ self.reduction_ratio, (pointer.y-(self.canvas.winfo_height() - self.re_height)/2) / self.reduction_ratio) 
                self.display(1)
                


    def release(self, pointer):
        self.canvas.delete(self.zoom_center_h_line)
        self.canvas.delete(self.zoom_center_v_line)
        self.canvas.delete(self.zoom_window_img)
                        
    
    def crop(self, cir_center):
        crop_square_size = int(self.canvas.winfo_height() * 0.05)
        zoom_image_radius = int(self.canvas.winfo_height() * 0.08)
        crop_image = self.resized_image.crop((cir_center[0]-crop_square_size, cir_center[1]-crop_square_size, cir_center[0]+crop_square_size, cir_center[1]+crop_square_size))
        zoom_image = crop_image.resize((zoom_image_radius*2, zoom_image_radius*2))
        circular_image = self.mask_circle_transparent(zoom_image, zoom_image_radius)
        return circular_image


    def mask_circle_transparent(self, pil_img, blur_radius):
        mask = Image.new("L", pil_img.size)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), (pil_img.size[0], pil_img.size[1])], fill="white")

        result = pil_img.copy()
        result.putalpha(mask)

        return result

    def scan_image(self, flag):
        if self.load_button_status == 0:
            self.label.config(text="Please load the image before scanning...")
            self.label.place(relx=0.15, rely=0.13)
            return

        self.label.place_forget()

        if flag == 0:
            if self.scan_button_status == 0:
                cv_image = np.array(self.orig_image) 
                # Convert RGB to BGR 
                cv_image = cv_image[:, :, ::-1].copy() 
                self.scanned_cv_image = transform(cv_image, np.array(self.src_pts, dtype="float32"))
                self.scanned_orig_image = self.scanned_cv_image.copy()
                self.scanned_pil_image = Image.fromarray(cv2.cvtColor(self.scanned_cv_image, cv2.COLOR_BGR2RGB))
            else:
                self.canvas.delete(self.scan_disp)
        
        self.canvas.delete("all")
        
        self.re_scanned_pil_image = self.resize_image(self.scanned_pil_image)
        self.photo2 = ImageTk.PhotoImage(self.re_scanned_pil_image)
        self.root.photo = self.photo2
        self.scan_disp = self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.photo2, anchor="center")
        self.scan_button_status = 1

        self.bw_button = Button(self.canvas, text='B/W', fg="red", bg="green", command=self.bw_filter)
        self.bw_button["font"] = font.Font(family='Helvetica', weight="bold", size=10)
        self.bw_button.place(height=50, width=50, relx=0.65, rely=0.9)

        self.color_button = Button(self.canvas, text='Color', fg="red", bg="green", command=self.color_filter)
        self.color_button["font"] = font.Font(family='Helvetica', weight="bold", size=10)
        self.color_button.place(height=50, width=50, relx=0.8, rely=0.9)
        self.scan_button_status = 1


    def bw_filter(self):
        self.scanned_cv_image = cv2.cvtColor(self.scanned_cv_image, cv2.COLOR_BGR2GRAY)
        self.scanned_cv_image = cv2.threshold(self.scanned_cv_image, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)[1]
        self.scanned_pil_image = Image.fromarray(self.scanned_cv_image)
        # self.temp_image = cv2.threshold(self.temp_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        # self.temp_image = cv2.filter2D(self.temp_image, -1, kernel)
        
        self.scan_image(0)

    def color_filter(self):
        self.scanned_cv_image = self.scanned_orig_image
        self.scanned_pil_image = Image.fromarray(cv2.cvtColor(self.scanned_cv_image, cv2.COLOR_BGR2RGB))
        self.scan_image(0)


    def cw_rotate(self):
        if self.load_button_status == 0:
            self.label.config(text="Please load the image before rotating...")
            self.label.place(relx=0.15, rely=0.13)
            return

        if self.scan_button_status == 1:
            self.label.config(text="Image cannot be rotated in after scanning...")
            self.label.place(relx=0.15, rely=0.13)
            return

        self.label.place_forget()
        self.orig_image = self.orig_image.rotate(-90, Image.NEAREST, expand = 1)
        self.orig_width, self.orig_height = self.orig_image.size
        corner_pts = []

        for i in range(4):
            corner_pts.append((self.orig_width - self.src_pts[i][1], self.src_pts[i][0]))

        self.src_pts = corner_pts

        self.canvas.delete("all")
        self.display(0)


    def ccw_rotate(self):
        if self.load_button_status == 0:
            self.label.config(text="Please load the image before rotating...")
            self.label.place(relx=0.15, rely=0.13)
            return

        if self.scan_button_status == 1:
            self.label.config(text="Image cannot be rotated in after scanning...")
            self.label.place(relx=0.15, rely=0.13)
            return

        self.orig_image = self.orig_image.rotate(90, Image.NEAREST, expand = 1)
        self.orig_width, self.orig_height = self.orig_image.size
        corner_pts = []

        for i in range(4):
            corner_pts.append((self.src_pts[i][1], self.orig_height - self.src_pts[i][0]))

        self.src_pts = corner_pts

        self.canvas.delete("all")
        self.display(0)


    def save_image(self):
        if self.scan_button_status == 0:
            self.label.config(text="Please scan the image before saving...")
            self.label.place(relx=0.15, rely=0.13)
            return

        if not os.path.exists("Output"):
            os.makedirs("Output")

        output_lst = os.listdir("./Output")
        num = 0
        if len(output_lst) > 0:
            for f in output_lst:
                if "scan_image_" in f:
                    if int(f[11:-4]) >= num:
                        num = int(f[11:-4]) + 1
        
        img_name = "./Output/scan_image_" + str(num) + ".jpg"
        cv2.imwrite(img_name, self.scanned_cv_image)


    def ocr_transcript(self):
        
        self.canvas2.delete("all")
        gray_im = cv2.cvtColor(self.scanned_orig_image, cv2.COLOR_BGR2GRAY)
        gray_im = cv2.threshold(gray_im, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        kernel2 = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        gray_im = cv2.filter2D(gray_im, -1, kernel2)
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray_im)
        text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        
        self.ocr_label = Text(self.canvas2)
        
        self.ocr_label.pack()
        self.ocr_label.insert(END, text)
        self.ocr_button_status = 1
        

    
    def handle_configure(self, window):

        self.canvas.delete("all")

        self.canvas_img_width = self.img_canvas_ratio[0] * self.canvas.winfo_width()

        self.canvas_img_height = self.img_canvas_ratio[1] * self.canvas.winfo_height()

        self.canvas_img_size_ratio = self.canvas_img_height / self.canvas_img_width
        
        if self.scan_button_status == 1:
            self.scan_image(1)
        else:
            self.display(0)





root = Tk()

DocumentScanner(root)
root.mainloop()


