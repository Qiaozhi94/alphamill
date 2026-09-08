from freqtrade.freqai.prediction_models.LightGBMRegressor import LightGBMRegressor


class KronosFreqAIModel(LightGBMRegressor):
    """
    Project-local LightGBM regression model for FreqAI.

    The strategy defines the features and target. This class intentionally keeps
    the standard FreqAI LightGBM training flow so model parameters stay controlled
    from config_freqai.json.
    """

    pass
