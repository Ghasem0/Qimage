from PIL import Image
import os, math
from termcolor import colored


class Qimage:
    def __init__(self) -> None:
        self.SUPPORT_EXTENTIONS = '.jpg', '.png', '.jpeg', '.webp'
        self.count = 0
        self.comb_cont = 0

    def get_images_path(self, input_folder:str)-> list:
        folder_pathes =os.listdir(input_folder)
        folder_pathes.sort()
        images_path = []
        for path in folder_pathes :
            if path.lower().endswith(self.SUPPORT_EXTENTIONS):
                print(colored(str(path), "yellow"))
                images_path.append(os.path.join(input_folder, path))
        try:    
            if not images_path:
                raise FileNotFoundError(f"folder '{input_folder}' is empty!\nPlease make sure that folder is correct or not empty.")

            else :
                return images_path

        except Exception as e:
            print(colored(f'FileNotFoundError : {e}','magenta'))
            exit()

    def resize_hight(self, piece_height:int, height:int)->tuple:
        deficit = 1000 - (height % piece_height)
        piece_height -= math.ceil(deficit) 
        remainder = height % piece_height
        return piece_height, remainder

    def split_image(self, path:str, output_folder:str, piece_hight:int=8000)->None:
        img = Image.open(path)
        width, height = img.size
        riminder = height % piece_hight
        
        if 0 < riminder < 1000:
            piece_hight, riminder = self.resize_hight(piece_hight, height )

        piece_count = height // piece_hight
        
        for i in range(piece_count):
            top = i * piece_hight
            bottom = (i+1) * piece_hight
            piece = img.crop((0, top, width, bottom,))
            
            number = self.count + 1 if self.count >= 9 else f'0{self.count + 1}'
            out_path = os.path.join(output_folder, f'pic_{number}.png')
            self.count += 1

            piece.save(out_path, 'PNG')
            print(f"pic {number} saved!")

        if riminder > 0:
            top = piece_count * piece_hight
            bottom = height

            last_piece = img.crop((0, top, width, bottom,))

            number = self.count + 1 if self.count >= 9 else f'0{self.count + 1}'
            out_path = os.path.join(output_folder, f'pic_{number}.png')
            self.count += 1

            last_piece.save(out_path, 'PNG')
            print(f"pic {number} saved!")
            print(f'image {colored(str(os.path.splitext(os.path.basename(path))[0]), "green")} complete')

    def crop_images(self,images_path:list, output_folder:str, piece_hight:int=8000)->None:

        for fileName in images_path :
            self.split_image(fileName, output_folder, piece_hight)

        self.count = 0

    def combine_images(self, images_path:list, output_folder:str)->None:
        widths, heights = zip(*(Image.open(path).size for path in images_path))
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
        combined_image.save(os.path.join(output_folder, f"pic_{number}.png"), format='PNG')
        print(f"image pic_{number}saved!")
         
    def group_image_by_length(self, images_path:list, output_folder, min_len=8000):
        group_images:list = []
        sums:int = 0
        sent:bool = False
        self.comb_count = 0
        images_count = len(images_path)
        for ind, path in enumerate(images_path):
            img = Image.open(path)
            img_height = img.height
            img.close()

            if sums + img_height > min_len :
                sent = True

            sums += img_height

            group_images.append(path)
            
            if sent or ind == images_count -1 :
                print(sums)
                self.combine_images(group_images, output_folder)
                group_images = []
                sums, sent = 0, False

    def run(self)->None:
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