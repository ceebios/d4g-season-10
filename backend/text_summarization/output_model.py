import argparse
import os
import functools
import json
from glob import glob
import pubmed_parser as pp
import models_pipeline as mp

models = {
    "pegasus": mp.model_pegasus
}


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
    :param model_name: Name of model choosed
    :type model_name: str
    :return: Dataset with metadata and output model
    :rtype: list[dict]
    """

    for res_fig, fig in zip(result, dataset):
        fig["resultat"] = res_fig
        fig["model_choosed"] = model_name

    return dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_input", default="./xml", help="Path of xml file")
    parser.add_argument("path_output", default="./result.json",
                        help="Path of file output")
    parser.add_argument("model", default="all",
                        help="Use all for use all algorithme otherwise use the these names: \n- 'pegasus'\n- 'other'")
    args = parser.parse_args()
    xml_files = glob(args.path_input+"/*.xml")

    if len(xml_files) < 1:
        raise FileExistsError(
            f"ERROR: No file found with this path {args.path_input}"
        )

    dataset_with_meta = make_dataset(xml_files)
    dataset = feature_engineering(dataset_with_meta)

    if not args.model in list(models.keys()):
        raise KeyError(
            f"ERROR: Not models with this name, but we have:{models.keys()}"
        )

    if args.model == "all":
        choose_models = models.keys() 
    else:
        choose_models = args.model if type(args.model)==list else [args.model] 
    
    result = []
    for m_name in choose_models:
        model = models[m_name]
        model = model()
        result = model.make_outputs(dataset)
        result.append(add_information(result, dataset_with_meta, model_name = m_name))

    with open(args.path_output, "w") as f:
        json.dump(result, f)
    
    print("END: File stored !")