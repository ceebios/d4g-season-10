import os
import numpy as np
import cv2
from pdf2image import convert_from_path
from PIL import Image
import layoutparser as lp
import pytesseract

def callmodel(conf_threshold):
  model = lp.EfficientDetLayoutModel("lp://PubLayNet/tf_efficientdet_d0/config")
  model.DEFAULT_OUTPUT_CONFIDENCE_THRESHOLD = conf_threshold #0.7
  return model

def convert_pdf2image(datasets_path, batch_img):
  list_pdf = os.listdir(datasets_path)
  #list_pdf = filter(lambda f: f.endswith(('.pdf','.PDF')), list_pdf)
  images_dic = {}
  for pdf in list_pdf[(batch_img-1)*10:batch_img*10]:
      name_pdf =  pdf[:-4]
      images = convert_from_path(datasets_path+"/"+pdf, dpi=400)
      images_dic[name_pdf] = images 
  return images_dic

def retrieve_txt(img, name_pdf, page, datasets_path):
  img_th = img #cv2.threshold(img,127,255,cv2.THRESH_BINARY)
  custom_config = r'-l eng --oem 1 --psm 11' 
  print(type(img))
  text = pytesseract.image_to_string(img_th,config=custom_config)
  print(text)
  with open(datasets_path+'/txt/'+name_pdf+ 'page_' +str(page)+'.txt', 'w') as f:
    f.write(text)
  return text

def _preprocess_img(legend_img, size=130):
    img = cv2.cvtColor(legend_img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img,127,255,cv2.THRESH_BINARY) 
    return img

def retrieve_legend_txt(legend_figures, name_pdf, page, datasets_path,fig_id):
    custom_config = r'-l eng --oem 1 --psm 11' 
    text_legend = []
    print("retrieve legend txt")
    print(type(legend_figures))
    try:
        img = _preprocess_img(legend_figures, size=130)
        img = Image.fromarray(np.uint8(legend_figures))
        text = pytesseract.image_to_string(img,config=custom_config)
        print(text)
        with open(datasets_path+'/txt/'+name_pdf+ 'page_' +str(page)+'figure'+str(fig_id)+'legend.txt', 'w') as f:
            f.write(text)
        text_legend.append(text) 
    except:
        print("no legend")
    return text_legend

def main():
    datasets_path = '/home/kpetrus/D4G-season-10'
    list_pdf = os.listdir(datasets_path)
    img_predict_list = []
    figures_dic = {}
    tables_dic= {}
    model = callmodel(0.95)
    for batch_img_id in range(9):
        images_dic = convert_pdf2image(datasets_path+'/PDF',batch_img=batch_img_id)
        print(images_dic.keys())
        for pdf_id, name_pdf in enumerate(images_dic.keys()):
            for page, img in enumerate(images_dic[name_pdf]):
                layout = model.detect(img)
                img_c = np.array(img.copy())
                img = lp.draw_box(img, layout, box_width=3, show_element_id=True)
                text = retrieve_txt(img, name_pdf, page, datasets_path)
                img_predict_list.append(img)
                figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
                table_blocks = lp.Layout([b for b in layout if b.type=='Table'])
                figures_dic["page" + str(page) + "name" + name_pdf] = figure_blocks
                tables_dic["page" + str(page) + "name" + name_pdf] = table_blocks
                for tab_id, tabl in enumerate(table_blocks):
                    img_tables = img_c[int(tabl.block.y_1-10):int(tabl.block.y_2+10),int(tabl.block.x_1-10):int(tabl.block.x_2+10)]
                #print(datasets_pdf + "/Extraction_by_Pdf/" +name_pdf +"_table_"+str(tab_id)+".png")
                try:
                    cv2.imwrite(datasets_path+"/cropped/" +name_pdf +"_table_"+str(tab_id)+".png",img_tables)
                except:
                    print(name_pdf)
                for fig_id, fig in enumerate(figure_blocks):
                    legend_figures = img_c[int(fig.block.y_2):,:]
                    text_legend = retrieve_legend_txt(legend_figures, name_pdf, page, datasets_path,fig_id)
                    print(text_legend)
                    img_figures = img_c[int(fig.block.y_1-15):int(fig.block.y_2+15),int(fig.block.x_1):int(fig.block.x_2+15)]
                #print(datasets_pdf + "/Extraction_by_Pdf/"+name_pdf +"_figure_"+str(fig_id)+".png")
                try:
                    cv2.imwrite(datasets_path +"/cropped/" + name_pdf + 'page_' + str(page) + "_figure_"+str(fig_id)+".png",img_figures)
                    cv2.imwrite(datasets_path +"/cropped/" + name_pdf + 'page_' + str(page) + "legend_figure_"+str(fig_id)+".png",legend_figures)
                    cv2.imwrite(datasets_path +"/cropped/legend/" + name_pdf + 'page_' + str(page) + "legend_figure_"+str(fig_id)+".png",legend_figures)
                except:
                    print(name_pdf)
if __name__ == '__main__':
    main()