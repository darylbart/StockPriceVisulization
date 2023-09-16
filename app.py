from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

def fetch_stock_data(ticker, start_date, end_date):
    # Fetch stock data
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def plot_stock_data(stock_data, ticker, show_volume=True, moving_average=None):
    plt.figure(figsize=(12, 6))

    # Plot closing prices
    plt.plot(stock_data['Close'], label='Closing Price', color='blue')

    # Plot moving average if provided
    if moving_average:
        ma = stock_data['Close'].rolling(window=moving_average).mean()
        plt.plot(ma, label=f'{moving_average}-Day Moving Avg', color='red')

    plt.title('Stock Price for {}'.format(ticker))
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')

    # Plot volume if selected
    if show_volume:
        plt.bar(stock_data.index, stock_data['Volume'], color='gray', alpha=0.5, label='Volume')
        plt.ylabel('Volume')

    plt.legend()
    plt.grid()

    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image to base64
    img_uri = base64.b64encode(image_png).decode()
    return img_uri

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        show_volume = 'show_volume' in request.form
        moving_average = int(request.form['moving_average']) if 'moving_average' in request.form else None

        # Fetch stock data
        stock_data = fetch_stock_data(ticker, start_date, end_date)

        # Plot the stock data and get the image URI
        img_uri = plot_stock_data(stock_data, ticker, show_volume, moving_average)

        return render_template('index.html', img_uri=img_uri)

    return render_template('index.html', img_uri=None)

if __name__ == "__main__":
    app.run(debug=True)
