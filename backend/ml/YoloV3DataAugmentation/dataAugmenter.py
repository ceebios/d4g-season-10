#
# Created on Tue Apr 19 2022
#
# Data4Good - Ceebios 10
# Contact: Evan Dufraisse,  edufraisse@gmail.com
#

import argparse
from ast import arg
from PIL import Image
import numpy as np
import random
import os
import re
from tqdm.auto import tqdm

class ImageComposer:
    '''
    ImageComposer takes images from the data folder and add them to different templates
    
    CAUTION: We assume a certain structure of the image data folder such that each image is located following the structure:
    >> [folder]/[class name]/[subclass name]/<image_name>.(jpg|png|gif)
    '''
    def __init__(self, folder, path_output_folder, base_square_resolution=100, subclass = False):
        self.templates = {
            1:[(1,1)],
            2:[(1,2)],
            3:[(1,3)],
            4:[(1,4),(2,2)],
            6:[(2,3)]
        } # Available templates of images
        self.base_square_resolution = base_square_resolution # max(width,height) of each image will be resized to less than base_square_resolution pixels
        self.folder = folder
        self.all_images_paths = None
        self.all_images_subclass_paths = None
        self.subclass = subclass
        #self.output_folder = output_folder
        
    def _get_random_template_shape(self, templates = None):
        """Returns a random template with random permutation from self.templates

        Args:
            templates (dict, optional): To supply one's own templates. Defaults to None.

        Returns:
            list: tuple of the template ratio
        """
        
        if templates is None:
            templates = self.templates
            
        template_blocs = templates[random.choice(list(templates.keys()))]
        template_shape = list(random.choice(template_blocs))
        random.shuffle(template_shape)
        return template_shape

    def _create_template(self,template_shape, base_square_resolution = None):
        """From a template ratio and the max resolution of each image, returns an PIL Image instance.

        Args:
            template_shape (list): template shape ratio
            base_square_resolution (int, optional): Number of pixels max(width, height) of an image should not exceed. Defaults to None.

        Returns:
            Image: returns new Image instance
        """
        
        if base_square_resolution is None:
            base_square_resolution = self.base_square_resolution
            
        return Image.new('RGB', (template_shape[0]*base_square_resolution, template_shape[1]*base_square_resolution), color=(255,255,255))

    def _get_all_images_paths(self,folder = None, formats = ["jpg", "png", "gif"]):
        """From the supplied folder, iterates to find all the images complying with accepted formats.

        Args:
            folder (str, optional): path of root folder containing images. Defaults to None.
            formats (list, optional): Accepted format as images. Defaults to ["jpg", "png", "gif"].

        Returns:
            dict: All complying images absolute paths in a dictionnary whose key .
        """
        
        if not(self.all_images_paths is None):
            return self.all_images_paths
        
        if folder is None:
            folder = self.folder

        classes = sorted([f for f in os.listdir(folder) if not("." in f)])
            
        pattern = re.compile(".*("+str("|".join(formats))+")")
        images_class = {}
        for class_ in classes:
            class_folder = os.path.join(folder,class_)
            images_class[class_] = {}
            for path, folders, files in os.walk(class_folder):
                if len(folders) == 0:
                    sub_class = os.path.basename(path)
                    images_class[class_][sub_class] = [os.path.join(path,file) for file in files if not(pattern.match(file.lower()) is None)]
        self.all_images_paths = images_class

        return self.all_images_paths
    
    def _random_sample_image(self, subclass = None):
        """Randomly samples an image path from a class or a subclass

        Args:
            subclass (bool): sample from subclass

        Returns:
            tuple[str,int]: tuple containing chosen image and class/subclass index
        """
        if subclass is None:
            subclass = self.subclass
        
        if self.all_images_paths is None:
            self._get_all_images_paths()
        
        if subclass:
            if self.all_images_subclass_paths is None:
                self.all_images_subclass_paths = {}
                for sub in self.all_images_paths.values():
                    for subclass_name, paths in sub.items():
                        self.all_images_subclass_paths[subclass_name] = paths
            subclasses = sorted(list(self.all_images_subclass_paths.keys()))
            index_class = np.random.randint(len(subclasses))
            paths = self.all_images_subclass_paths[subclasses[index_class]]
            
            return (random.choice(paths), index_class)
        
        else:
            classes = sorted(list(self.all_images_paths.keys()))
            index_class = np.random.randint(len(classes))
            paths = [p for sublist in self.all_images_paths[classes[index_class]].values() for p in sublist]
            
            return (random.choice(paths), index_class)
        
    def get_centers(self, base_square_resolution = None, template_shape = (2,3), margin = 0):
        """Returns the centers of the images on the template considering template shape and margin

        Args:
            base_square_resolution (int, optional): maximum resolution of images. Defaults to None.
            template_shape (tuple, optional): template shape. Defaults to (2,3).
            margin (int, optional): margin between borders and images. Defaults to 0.

        Returns:
            tuple[float, list]: tuple with corrected resolution integrating margin and list of centers
        """
        if base_square_resolution is None:
            base_square_resolution = self.base_square_resolution
        centers = []
        base_square_res_corrected = ((base_square_resolution*template_shape[0] - (template_shape[0] + 1)*margin))//template_shape[0]
        for i in range(template_shape[0]):
            for j in range(template_shape[1]):
                centers.append(((i+1)*margin + (2*i)*base_square_res_corrected//2, (j+1)*margin + (2*j)*base_square_res_corrected//2))
        return base_square_res_corrected, centers


    def create_random_composed_image(self, base_square_resolution = None, subclass=False, margin=0):
        """Create random augmented images

        Args:
            base_square_resolution (int, optional): max resolution images. Defaults to None.
            subclass (bool, optional): sample from subclass folders. Defaults to False.
            margin (int, optional): size of margin in pixels. Defaults to 0.

        Returns:
            tuple[Image, list[int]]: (Augmented Image, indices of present classes)
        """
        
        if base_square_resolution is None:
            base_square_resolution = self.base_square_resolution
        
        template_shape = self._get_random_template_shape()
        n_images = template_shape[0]*template_shape[1]
        template = self._create_template(template_shape, base_square_resolution)
        
        if self.all_images_paths is None:
            self._get_all_images_paths()
        
        if subclass:
            n_classes = sum([len(i.values()) for i in self.all_images_paths.values()])
        else:
            n_classes = len(self.all_images_paths.keys())
            
        composition = []
        images = []
        
        for _ in range(n_images):
            image_path, index_class = self._random_sample_image(subclass)
            composition.append(index_class)
            images.append(Image.open(image_path))
            
        
        # Resize images
        
        base_square_res_corrected, centers = self.get_centers(base_square_resolution = base_square_resolution, template_shape = template_shape, margin = margin)
        sizes = []
        yolo_entries = []
        for idx, image in enumerate(images):
            width, height = image.size
            ratio = width/height
            if width > height:
                new_size = (int(base_square_res_corrected), int(base_square_res_corrected/ratio))
            else:
                new_size = (int(base_square_res_corrected*ratio), int(base_square_res_corrected))
            sizes.append(new_size)
            image = image.resize(new_size)
            yolo_entries.append((str(composition[idx]), str(centers[idx][0]/template.size[0]), str(centers[idx][1]/template.size[1]), str(new_size[0]/template.size[0]), str(new_size[1]/template.size[1])))
            
            template.paste(image, centers[idx])
        return template, yolo_entries #, images, centers, sizes


def generate_augmented_dataset(n_images, path_input_folder, path_output_folder, base_square_resolution, subclass):
    """Main function to generate dataset

    Args:
        n_images (int): number of images to generate
        path_input_folder (str): folder of input images
        path_output_folder (str): folder of output images
        base_square_resolution (int): max(width,height) resolution of images
    """
    
    path_output_images= os.path.join(path_output_folder,"augmented_images")
    os.mkdir(path_output_images)
    path_output_labels = os.path.join(path_output_folder, "labels")
    os.mkdir(path_output_labels)
    composer = ImageComposer(path_input_folder, path_output_folder=path_output_folder)
    for k in tqdm(range(n_images)):
        template, yolo_entries = composer.create_random_composed_image(base_square_resolution=400, margin=20)
        template.save(os.path.join(path_output_folder, f"{k}.jpg"))
        print(yolo_entries)
        with open(os.path.join(path_output_folder, f"{k}.txt"), "w", encoding="utf-8") as f:
            for elem in yolo_entries:
                f.write(f'{" ".join(elem)}\n')
    



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser("Data Augmenter for YoloV3")

    parser.add_argument("--n_images", "-n", type=int, help="number of images to generate")
    parser.add_argument("--path_input_folder", "-d", type=str, help="path to the root folder containing the images")
    parser.add_argument("--path_output_folder", "-o", type=str, help="path to output folder where to put YoloV3 dataset")
    parser.add_argument("--base_square_resolution", type=int , default=100)
    parser.add_argument("--subclass", action="store_true")

    args = parser.parse_args()

    generate_augmented_dataset(args.n_images, args.path_input_folder, args.path_output_folder, args.base_square_resolution, args.subclass)