from PIL import Image
import os, math
from termcolor import colored


class Qimage:
    def __init__(self) -> None:
        self.SUPPORT_EXTENTIONS = '.jpg', '.png', '.jpeg'
        self.count = 0

    def get_images(self, input_folder):
        folder_pathes =os.listdir(input_folder)
        folder_pathes.sort()
        images_path = []
        for path in folder_pathes :
            if path.lower().endswith(self.SUPPORT_EXTENTIONS):
                print(colored(str(path), "yellow"))
                images_path.append(os.path.join(input_folder, path))
            
        return images_path

    def resize_hight(self, piece_height, height):
        pieces_count =  height // piece_height
        deficit = 1000 - (height % piece_height)
        piece_height -= math.ceil(deficit) 
        remainder = height % piece_height
        return piece_height, remainder

    def split_image(self, path, output_folder, piece_hight=8000):
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

            out_path = os.path.join(output_folder, f'pic_{self.count + 1}.png')
            self.count += 1

            piece.save(out_path, 'PNG')
            print(f"pic {self.count} saved!")

        if riminder > 0:
            top = piece_count * piece_hight
            bottom = height

            last_piece = img.crop((0, top, width, bottom,))

            out_path = os.path.join(output_folder, f'pic_{self.count + 1}.png')
            self.count += 1

            last_piece.save(out_path, 'PNG')
            print(f"pic {self.count} saved!")
            print(f'image {colored(str(os.path.splitext(os.path.basename(os.path.splitext(path)[0]))[0]), "green")} complete')

    def crop_on_folder(self, input_folder, output_folder, piece_hight=8000):

        os.makedirs(output_folder, exist_ok=True)

        
        for fileName in self.get_images(input_folder):
            self.split_image(fileName, output_folder, piece_hight)

    def combine_on_folder(self, input_folder, output_folder):
        images_path:tuple = self.get_images(input_folder)
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

        combined_image.save(os.path.join(output_folder, "combined.png"), format='PNG')
        print("image saved!")
         
    def run(self):
        command = input('setting(set) / crop(cr) / combine(cm) : ')
        match command :
            case "cr":
                folder_path = input("process on 'crop_in' folder (y) or Enter path : ")
                self.crop_on_folder(folder_path if folder_path!='y' else 'crop_in', "crop_out")

            case "cm":
                folder_path = input("process on 'comb_in' folder (y) or Enter path : ")
                self.combine_on_folder(folder_path if folder_path !='y' else "comb_in", "comb_out")

if __name__ == "__main__":
    qimg = Qimage()
    qimg.run()