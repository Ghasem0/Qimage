from PIL import Image
import os, math
from termcolor import colored
import shutil
import os



class Qimage:
    def __init__(self) -> None:
        self.SUPPORT_EXTENTIONS = ('.jpg', '.png', '.jpeg', '.webp',)
        self.DIRECTORIES = ('comb_in', 'comb_out', 'crop_in', 'crop_out', 'catch',)
        self.DEFUALT_PIECE_HEIGHT = 8000
        self.MIN_HEIGHT_COMBINE = 16000
        self.count = 0
        self.comb_count = 0

    def dir_exist(self, directory_list):
        '''insure requirement directories exist.'''
        for directory in directory_list:
            os.makedirs(directory, exist_ok=True) #insure directoies exist

    def get_img_size(self, path:str)->int:
        '''get width, height of image'''
        with Image.open(path) as img:
            width, height = img.size
            return width, height

    def get_images_path(self, input_folder:str)-> list:
        '''get all images path from folder'''
        folder_pathes =sorted(os.listdir(input_folder))
        images_path = []
        for path in folder_pathes :
            if path.lower().endswith(self.SUPPORT_EXTENTIONS):
                print(colored(str(path), "yellow"))
                images_path.append(os.path.join(input_folder, path))
        try:    
            if not images_path:
                raise FileNotFoundError(f"folder '{input_folder}' is empty!\nPlease make sure that folder is correct or not empty.")

            else :
                return images_path.copy()

        except Exception as e:
            print(colored(f'FileNotFoundError : {e}','magenta'))
            exit()

    def resize_hight(self, piece_height:int, height:int)->tuple:
        '''if last image is smaller than 1000px, reset other images height to last image become 1000px or more'''
        deficit = 1000 - (height % piece_height)
        piece_height -= math.ceil(deficit) 
        remainder = height % piece_height
        return piece_height, remainder

    def split_image(self, path:str, output_folder:str, resize_height=True, piece_hight=None)->tuple:
        '''crop an image by 8000px height'''
        if piece_hight == None:
            piece_hight = self.DEFUALT_PIECE_HEIGHT

        with Image.open(path) as img :
            width, height = img.size
            remainder = height % piece_hight
            
            if 0 < remainder < 1000 and resize_height: # if last image smaller than 1000px
                piece_hight, remainder = self.resize_hight(piece_hight, height )

            piece_count = height // piece_hight
            
            img_new_path=[] # created images path for return
            for i in range(piece_count):
                top = i * piece_hight
                bottom = (i+1) * piece_hight
                piece = img.crop((0, top, width, bottom,))
                
                number = self.count + 1 if self.count >= 9 else f'0{self.count + 1}'
                out_path = os.path.join(output_folder, f'pic_{number}.png')
                img_new_path.append(out_path)
                self.count += 1

                piece.save(out_path, 'PNG')
                print(f"pic {number} saved!")

            if remainder > 0:
                top = piece_count * piece_hight
                bottom = height

                last_piece = img.crop((0, top, width, bottom,))

                number = self.count + 1 if self.count >= 9 else f'0{self.count + 1}'
                out_path = os.path.join(output_folder, f'pic_{number}.png')
                self.count += 1

                last_piece.save(out_path, 'PNG')
                print(f"pic {number} saved!")
                print(f'crop image {colored(str(os.path.splitext(os.path.basename(path))[0]), "green")} complete')
            
            return img_new_path

    def crop_images(self,images_path:list, output_folder:str, piece_hight=None)->None:
        '''crop a list or tuple of images'''
        if piece_hight == None:
            piece_hight = self.DEFUALT_PIECE_HEIGHT

        for fileName in images_path :
            self.split_image(fileName, output_folder, piece_hight)

        self.count = 0

    def combine_images(self, images_path:list, output_folder:str)->str:
        '''combine a list of images together verticaly'''
        widths, heights = zip(*(self.get_img_size(path) for path in images_path))
        output_height = sum(heights)
        width = max(widths)
        combined_image = Image.new("RGB", (width, output_height))
        
        y_cut = 0
        for path in images_path:
            img = Image.open(path)
            combined_image.paste(img, (0, y_cut))
            y_cut += img.height
            img.close()

        number = self.comb_count + 1 if self.comb_count >= 9 else f'0{self.comb_count + 1}'
        self.comb_count += 1 
        path = os.path.join(output_folder, f"comb_{number}.png")
        combined_image.save(path, format='PNG')
        print(f"image comb_{number} saved!")
        return path
      
    def group_image_by_length(self, images_path:list, output_folder, min_len=None):
        '''grouping images base on minimum-length and send for combine'''
        if min_len==None :
            min_len = self.MIN_HEIGHT_COMBINE

        group_images:list = []
        sums:int = 0
        catch_img =[]
        sent:bool = False
        self.comb_count = 0
        images_count = len(images_path)

        for ind, path in enumerate(images_path):
            img_height = self.get_img_size(path)[1]

            if sums + img_height > min_len : # if img > 8000px saved
                sent = True

            sums += img_height

            group_images.append(path)
            
            if sent or ind == images_count -1 : # end of list if height < 8000
                comb_path = self.combine_images(group_images, "catch") # combine images and save in catch folder
                if catch_img:
                    os.remove(catch_img[0])
                    self.count -= 1
                croped_imgs = self.split_image(comb_path, "catch", resize_height=False) # splite comb_img and save them in catch  folder
                for path in croped_imgs:
                    shutil.move(path, output_folder)

                os.remove(comb_path) 
                catch_img = self.get_images_path("catch") 
                sent = False

                if catch_img: # add catch img if exist
                    group_images = catch_img.copy()
                    sums = self.get_img_size(group_images[0])[1]
                else :
                    group_images = []
                    sums= 0

        if group_images:
            shutil.move(group_images[0], "comb_out")        

    def run(self)->None:
        self.dir_exist(self.DIRECTORIES) #insure required director exist

        command = input('setting(set) / crop(cr) / combine(cm) : ').strip().lower()
        match command :
            case "cr":
                path = input("process on 'crop_in' folder (y) or Enter path : ")
                folder_path = path if path != 'y' else "crop_in"
                images_path = self.get_images_path(folder_path)
                self.crop_images(images_path, "crop_out")

            case "cm":
                path = input("process on 'comb_in' folder (y) or Enter path : ")
                folder_path = path if path != 'y' else "comb_in"
                images_path = self.get_images_path(folder_path)
                self.group_image_by_length(images_path, "comb_out")

if __name__ == "__main__":
    qimg = Qimage()
    qimg.run()