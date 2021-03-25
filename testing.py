import torch
from epiweeks import Week
import matplotlib.pyplot as plt
from modulesRNN.utils import Dataset
from seq2seqModels import encoder_decoder, two_encoder_decoder, inputAttention2ED, inputAttentionED
import modulesRNN.utils as utils
import pandas as pd

device = torch.device("cpu")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
dtype = torch.float64

# Introduce the path were the data is storage
data_path_dataset = './data/train_data_weekly_vEW202105.csv'
data_path_visual = './data/train_data_weekly_noscale_vEW202105.csv'
wk_ahead = 4
regions = ['X', 'CA', 'FL', 'GA', 'IL', 'LA', 'PA', 'TX', 'WA']
# regions = ['TX', 'PA', 'LA', 'IL', 'GA', 'FL']
weeks_strings = [str(x) for x in range(202010, 202054)] + [str(y) for y in range(202101, 202107)]
weeks = [Week.fromstring(y) for y in weeks_strings]
include_col = ['target_death', 'retail_and_recreation_percent_change_from_baseline',
               'grocery_and_pharmacy_percent_change_from_baseline', 'parks_percent_change_from_baseline',
               'transit_stations_percent_change_from_baseline', 'workplaces_percent_change_from_baseline',
               'residential_percent_change_from_baseline', 'positiveIncrease', 'negativeIncrease',
               'totalTestResultsIncrease', 'onVentilatorCurrently', 'inIcuCurrently', 'recovered',
               'hospitalizedIncrease', 'death_jhu_incidence', 'dex_a', 'apple_mobility', 'CLI Percent of Total Visits',
               'fb_survey_cli']
RNN_DIM = 128  # Change
n_signals = len(include_col) - 1
last_week_data = Week.fromstring('202106')

model_types = ('2ED', 'ED', 'Input2ED', 'InputED')
models = [

]

def plot_signals():
    pass


def testing():
    # Variables:
    n_week = 45
    wk_ahead = 4
    model_type = model_types[1]  # Change
    error_total = []
    predictions_total = []
    for region in regions:
        for n_week in range(20, 46):
            # for n_week in range(20, 49 - wk_ahead + 1):

            # region = 'X'
            week = weeks[n_week]  # Actual week +1
            path_model = './trainedModels/' + model_type + '/' + region + '_' + weeks_strings[n_week - 1] + '_0.pth'

            dataset_visual = Dataset(data_path_visual, last_week_data, region, include_col, wk_ahead)

            # Creating and loading model
            dataset_test = Dataset(data_path_dataset, week, region, include_col, wk_ahead)
            seqs, ys, mask_seq, mask_ys, allys = dataset_test.create_seqs(dataset_test.y.shape[0], RNN_DIM)
            seq_model = encoder_decoder.Seq2SeqModel(seqs.shape[1], seqs.shape[-1], RNN_DIM, wk_ahead)  # Change
            seq_model.load_state_dict(torch.load(path_model, map_location=torch.device(device)))
            # Testing the model
            seq_model.eval()
            predictions_no_scaled = seq_model(seqs, mask_seq, allys)  # Allys is for two encoder models
            predictions_tensor = dataset_test.scale_back_Y(predictions_no_scaled)
            predictions = predictions_tensor.detach().numpy()
            # Obtaining real values
            real_values = dataset_visual.y[n_week:n_week + wk_ahead]
            real_values_tensor = torch.tensor(real_values)
            # Calculating error
            mae = utils.mae_calc(predictions_tensor, real_values_tensor)
            mape = utils.mape_calc(predictions_tensor, real_values_tensor)
            mse = utils.mse_calc(predictions_tensor, real_values_tensor)
            rmse = utils.rmse_calc(predictions_tensor, real_values_tensor)

            error_total.append([mae, mape, mse, rmse])
            predictions_total.append(predictions)
            # Plotting an printing results
            x = [n for n in range(n_week+1, n_week + wk_ahead+1)]
            plt.plot(x, real_values, '-')
            plt.plot(x, predictions, ':')

            print(f'N:{n_week} MAE:{mae}, MAPE:{mape}, MSE:{mse}, RMSE:{rmse}')


        plt.show()

    a = 1


if __name__ == '__main__':
    testing()
