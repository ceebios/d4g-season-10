import argparse
import os
import functools
import json
from glob import glob
import pubmed_parser as pp
import transformers
import models_pipeline as mp
import copy

models_list = ['pegasus', 'distilbartcnn66', 'distilbartcnn126', 'bartlargecnn', "mt5multilingual"]


def call_and_load_model(model_name:str):
    """Instead of loading every model available, this functions loads only the selected model
    based on the model name given.

    :param model_name: Model's name
    :type model_name: str
    :return: The TransformersSummarizationModel loaded
    :rtype: TransformersSummarizationModel()
    """

    if model_name == "pegasus":
        model = mp.TransformersSummarizationModel(name_model_gz="google/pegasus-xsum",
                                                  tokenizer_instance=transformers.PegasusTokenizer,
                                                  model_instance=transformers.PegasusForConditionalGeneration)

    elif model_name == "distilbartcnn66":
        model = mp.TransformersSummarizationModel(name_model_gz="sshleifer/distilbart-cnn-6-6",
                                                  tokenizer_instance=transformers.BartTokenizer,
                                                  model_instance=transformers.BartForConditionalGeneration)

    elif model_name == "distilbartcnn126":
        model = mp.TransformersSummarizationModel(name_model_gz="sshleifer/distilbart-cnn-12-6",
                                                  tokenizer_instance=transformers.BartTokenizer,
                                                  model_instance=transformers.BartForConditionalGeneration)

    elif model_name == "bartlargecnn":
        model = mp.TransformersSummarizationModel(name_model_gz="facebook/bart-large-cnn",
                                                  tokenizer_instance=transformers.BartTokenizer,
                                                  model_instance=transformers.BartForConditionalGeneration)

    elif model_name == "mt5multilingual":
        model = mp.TransformersSummarizationModel(name_model_gz="csebuetnlp/mT5_multilingual_XLSum",
                                                  tokenizer_instance=transformers.AutoTokenizer,
                                                  model_instance=transformers.AutoModelForSeq2SeqLM)
    else:
        model = '' # Not really useful because there is already a check on model's name but to be sure

    return model



def make_dataset(path_files:str) -> list:
    """Build dataset with meta data, each element is a paragraph of one figures with these metadata

    :param path_files: The folder of xml file
    :type path_files: str
    :return: The dataset of paragraph element with metadata
    :rtype: list[dict]
    """
    all_articles_figures = []
    for path_file in path_files:
        aggregator_figure_information = pp.parse_pubmed_caption(path_file)
        figures = [
            {
                "fig_id": fig_info["fig_id"],
                "fig_label":fig_info["fig_label"],
                "fig_caption":fig_info["fig_caption"],
            }
            for fig_info in aggregator_figure_information
        ]
        dict_paragraph = pp.parse_pubmed_paragraph(
            path_file, all_paragraph=True)
        meta = pp.parse_pubmed_xml(path_file)
        for figure in figures:
            figure["paragraph_link"] = []
            figure["paragraph_ref"] = []
            figure['doi'] = meta['doi']
            for idx, paragh in enumerate(dict_paragraph):
                if figure['fig_id'] in paragh["reference_ids"]:
                    figure["paragraph_link"].append(paragh["text"])
                    figure["paragraph_ref"].append((idx, paragh["section"]))

        all_articles_figures += figures
    return all_articles_figures


def feature_engineering(all_figures_pargraph:list) -> list:
    """Design dataset to keep only the trained values

    :param all_figures_pargraph: The dataset of paragraph element with metadata
    :type all_figures_pargraph: list[dict]
    :return: The list of paragraphs in one str of each figure concerned
    :rtype: list[str]
    """
    return [
        functools.reduce(lambda x, y: x+y, fig["paragraph_link"])
        for fig in all_figures_pargraph
    ]


def add_information(result:list, dataset:list, model_name:str) -> list:
    """Add meta information of output models

    :param result: List output of model
    :type result: list[str]
    :param dataset: Dataset with metadata
    :type dataset: list[dict]
    :param model_name: Name of model chosen
    :type model_name: str
    :return: Dataset with metadata and output model
    :rtype: list[dict]
    """

    for res_fig, fig in zip(result, dataset):
        fig["resultat"] = res_fig
        fig["model_chosen"] = model_name

    return dataset


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--path_input", default="./xml", help="Path of xml file")
    parser.add_argument("--path_output", default="./result.json",
                        help="Path of file output")
    parser.add_argument("--model_name", default="all",
                        help=f"Use 'all' to use all models otherwise use these following names: { '; '.join(models_list) }")
    args = parser.parse_args()
    xml_files = glob(args.path_input+"/*.xml")

    if len(xml_files) < 1:
        raise FileExistsError(
            f"ERROR: No file found with this path {args.path_input}"
        )

    dataset_with_meta = make_dataset(xml_files)
    dataset = feature_engineering(dataset_with_meta)

    if not args.model_name in list(models_list) and args.model_name != 'all':
        raise KeyError(
            f"ERROR: Not models with this name, but we have:{' '.join(models_list)}"
        )

    if args.model_name == "all":
        choose_models = models_list
    else:
        choose_models = args.model_name if type(args.model_name)==list else [args.model_name]
    
    result_to_write = []
    for m_name in choose_models:
        print('Model used : {}'.format(m_name))
        model = call_and_load_model(m_name)
        result = model.make_outputs(dataset)
        result_to_write.append(
            copy.deepcopy(      # Need to deepcopy the json here otherwise it will replace the other one each time
                add_information(result, dataset_with_meta, model_name=m_name)
            )
        )

    with open(args.path_output, "w") as f:
        json.dump(result_to_write, f)
    
    print("END: File stored !")