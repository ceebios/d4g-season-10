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


def make_dataset(path_files):
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


def feature_engineering(all_figures):
    return [
        functools.reduce(lambda x, y: x+y, fig["paragraph_link"])
        for fig in all_figures
    ]


def add_information(result, dataset):
    for res_fig, fig in zip(result, dataset):
        fig["resultat"] = res_fig
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
            f"No file found with this path {args.path_input}"
        )

    dataset_with_meta = make_dataset(xml_files)
    dataset = feature_engineering([dataset_with_meta[0]])

    if not args.model in list(models.keys()):
        raise KeyError(
            f"Not models with this name, but we have:{models.keys()}"
        )

    model = models[args.model]
    model = model()
    result = model.make_outputs(dataset)

    result = add_information(result, dataset_with_meta)

    with open(args.path_output, "w") as f:
        json.dump(result, f)
    print("File stored !")
