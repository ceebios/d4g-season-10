Model aimed at measuring the similarity between two paper abstracts.

Training notebook is based on the arxiv dataset from kaggle, channeling more than 1.7M articles abstracts
link : https://www.kaggle.com/datasets/Cornell-University/arxiv?select=arxiv-metadata-oai-snapshot.json

Inference notebook can be used either as a demo, or for embedding inference

Algorithm description :
- model is trained to predict a cosine similarity between pairs of abstract crop, predicting zero for a mismatch, one for a match
- cosine similarity is computed as scalar product of two normalized vector, followed by a min max scaler to get score between zero and one
- backbone of the model is a roberta-base, with weights pretrained with sequence length of 64, 128, 256 and 512 token (512 is longer than any abstract)
- final embedding dimension is 512