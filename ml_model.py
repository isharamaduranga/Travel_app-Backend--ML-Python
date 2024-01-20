# ml_model.py

from transformers import pipeline


class TransformersPipelineException(Exception):
    pass


def predict_score(text):
    try:
        pipe = pipeline("text-classification", model="lewtun/xlm-roberta-base-finetuned-marc")
        preds = pipe(text)[0]
        return round(preds["score"], 5)
    except Exception as e:
        raise TransformersPipelineException(f"Error in ML model pipeline: {str(e)}")
