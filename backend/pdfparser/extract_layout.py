import os
import sys
import pdf2image
from pdf2image import convert_from_path
import layoutparser as lp


def callmodel(conf_threshold):
    model = lp.EfficientDetLayoutModel("lp://PubLayNet/tf_efficientdet_d0/config")
    model.DEFAULT_OUTPUT_CONFIDENCE_THRESHOLD = conf_threshold #0.7
    return model

def convert_pdf2image(datasets_path):
    list_pdf = os.listdir(datasets_path)
    images_dic = {}
    for pdf in list_pdf:
        name_pdf =  pdf[:-4]
        images = convert_from_path(datasets_path+"/"+pdf)
        images_dic[name_pdf] = images 
    return images_dic

def extract_layout_pdf(images_dic, model, name_pdf):
    for img in images_dic[name_pdf]:
        layout = model.detect(img)
        lp.draw_box(img, layout, box_width=3, show_element_id=True)
        figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
        table_blocks = lp.Layout([b for b in layout if b.type=='Table'])

    
if __name__ ==  '__main__':
    datasets_path = "datasets/D4G-season-10/PDF/pdf"#/Users/karinepetrus/Desktop/projectDataForGood/datasets/D4G-season-10/PDF/pdf"#sys.argv[0] 
    model = callmodel(conf_threshold=0.7)
    images_dic = convert_pdf2image(datasets_path)
    #example name pdf
    name_pdf = '10.1101-2020.03.26.010397'
    img_predict_list = []
    figures_dic = {}
    tables_dic= {}
    for img in images_dic[name_pdf]:
        layout = model.detect(img)
        img = lp.draw_box(img, layout, box_width=3, show_element_id=True)
        img_predict_list.append(img)
        figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
        table_blocks = lp.Layout([b for b in layout if b.type=='Table'])
        figures_dic[name_pdf] = figure_blocks
        tables_dic[name_pdf] = table_blocks