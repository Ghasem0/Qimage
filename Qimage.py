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

    def valid_number(self, num)->str:
        '''this sure numbers that smaller than 10 startswith 0 '''
        return  str(num + 1) if num >= 9 else f'0{ num + 1}'

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
                # print(colored(str(path), "yellow"))
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
                
                number = self.valid_number(self.count)
                out_path = os.path.join(output_folder, f'pic_{number}.png')
                img_new_path.append(out_path)
                self.count += 1

                piece.save(out_path, 'PNG')
                print(f"splite : pic {number} saved!")

            if remainder > 0:
                top = piece_count * piece_hight
                bottom = height

                last_piece = img.crop((0, top, width, bottom,))

                number = self.valid_number(self.count)
                out_path = os.path.join(output_folder, f'pic_{number}.png')
                self.count += 1

                last_piece.save(out_path, 'PNG')
                print(f"splite : pic {number} saved!")
                print(f'splite image {colored(str(os.path.splitext(os.path.basename(path))[0]), "green")} complete')
            
            return img_new_path

    def split_images(self, images_path:list, output_folder:str, piece_hight=None)->None:
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

        number = self.valid_number(self.comb_count)
        self.comb_count += 1 
        path = os.path.join(output_folder, f"comb_{number}.png")
        combined_image.save(path, format='PNG')
        print(f"combine : image comb_{number} saved!")
        return path
      
    def group_image_by_length(self, images_path:list, output_folder, min_len=None):
        '''grouping images base on minimum-length and send for combine'''
        if min_len==None :
            min_len = self.MIN_HEIGHT_COMBINE

        current_group_images:list = []
        total_height:int = 0
        remaining_images = []
        is_group_ready_to_process:bool = False
        self.comb_count = 0
        images_count = len(images_path)

        for index, image_path in enumerate(images_path):
            img_height = self.get_img_size(image_path)[1]

            if total_height + img_height > min_len : # if img > 8000px saved
                is_group_ready_to_process = True

            total_height += img_height

            current_group_images.append(image_path)
            
            if is_group_ready_to_process or index == images_count -1 : # end of list if height < 8000
                combined_img_path = self.combine_images(current_group_images, "catch") # combine images and save in catch folder
                
                if remaining_images: # remove remainder-photo from catch folder
                    os.remove(remaining_images[0])
                    self.count -= 1

                splitted_img_path = self.split_image(combined_img_path, "catch", resize_height=False) # splite comb_img and save them in catch  folder
                for image_path in splitted_img_path: # move full images to output-folder
                    shutil.move(image_path, output_folder)

                os.remove(combined_img_path) # remove main image that combined

                remaining_images = self.get_images_path("catch") 
                is_group_ready_to_process = False

                if remaining_images: # add remainder-img path if made in split-image func
                    current_group_images = remaining_images.copy()
                    total_height = self.get_img_size(current_group_images[0])[1]
                else :
                    current_group_images = []
                    total_height= 0

        if current_group_images: # add if there are images that smaler than min-len and not added 
            shutil.move(current_group_images[0], "comb_out")        

    def run(self)->None:
        self.dir_exist(self.DIRECTORIES) #insure required director exist

        command = input('setting(set) / crop(cr) / combine(cm) : ').strip().lower()
        match command :
            case "cr":
                path = input("process on 'crop_in' folder (y) or Enter path : ")
                folder_path = path if path != 'y' else "crop_in"
                images_path = self.get_images_path(folder_path)
                self.split_images(images_path, "crop_out")

            case "cm":
                path = input("process on 'comb_in' folder (y) or Enter path : ")
                folder_path = path if path != 'y' else "comb_in"
                images_path = self.get_images_path(folder_path)
                self.group_image_by_length(images_path, "comb_out")

if __name__ == "__main__":
    qimg = Qimage()
    qimg.run()