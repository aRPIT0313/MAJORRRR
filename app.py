from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/scrape-stock', methods=['GET'])
def scrape_stock_data():
    # Get ticker symbol from query parameter
    ticker = request.args.get('ticker')
    
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400

    # Screener URL
    screener_url = f'https://www.screener.in/company/{ticker}/consolidated/'
    # Google Finance URL
    google_url = f'https://www.google.com/finance/quote/{ticker}:NSE'

    try:
        # Scraping from Screener
        screener_response = requests.get(screener_url)
        screener_soup = BeautifulSoup(screener_response.content, 'html.parser')

        comp_name = screener_soup.find(class_='margin-0 show-from-tablet-landscape').text if screener_soup.find(class_='margin-0 show-from-tablet-landscape') else 'Not available'
        
        # Attempt to get multiple data points safely
        values = screener_soup.find_all(class_='nowrap value')
        cap = "".join(values[0].text.strip().split()) if len(values) > 0 else 'Not available'
        current_p = "".join(values[1].text.strip().split()) if len(values) > 1 else 'Not available'
        highlow = "".join(values[2].text.strip().split()) if len(values) > 2 else 'Not available'
        pe = "".join(values[3].text.strip().split()) if len(values) > 3 else 'Not available'
        book_value = "".join(values[4].text.strip().split()) if len(values) > 4 else 'Not available'
        dividend = "".join(values[5].text.strip().split()) if len(values) > 5 else 'Not available'
        roce = "".join(values[6].text.strip().split()) if len(values) > 6 else 'Not available'
        roe = "".join(values[7].text.strip().split()) if len(values) > 7 else 'Not available'
        face_value = "".join(values[8].text.strip().split()) if len(values) > 8 else 'Not available'

        # Scraping from Google Finance
        google_response = requests.get(google_url)
        google_soup = BeautifulSoup(google_response.content, 'html.parser')

        # Extracting financial data from Google Finance
        day_range = google_soup.find_all(class_='P6K39c')[1].text.strip() if len(google_soup.find_all(class_='P6K39c')) > 1 else 'Not available'
        year_range = google_soup.find_all(class_='P6K39c')[2].text.strip() if len(google_soup.find_all(class_='P6K39c')) > 2 else 'Not available'
        primary_exchange = google_soup.find_all(class_='P6K39c')[7].text.strip() if len(google_soup.find_all(class_='P6K39c')) > 7 else 'Not available'
        
        g_eu_values = google_soup.find_all(class_='gEUVJe')
        revenue_c = g_eu_values[0].text.strip() if len(g_eu_values) > 0 else 'Not available'
        opt_ex_c = g_eu_values[1].text.strip() if len(g_eu_values) > 1 else 'Not available'
        net_i_c = g_eu_values[2].text.strip() if len(g_eu_values) > 2 else 'Not available'
        net_p_m = g_eu_values[3].text.strip() if len(g_eu_values) > 3 else 'Not available'
        earning_p_share = g_eu_values[4].text.strip() if len(g_eu_values) > 4 else 'Not available'
        ebitda = g_eu_values[5].text.strip() if len(g_eu_values) > 5 else 'Not available'
        
        about = google_soup.find_all(class_='bLLb2d')[0].text.strip() if google_soup.find_all(class_='bLLb2d') else 'Not available'
        
        logo = google_soup.find_all(class_='PdOqHc')[0].text[4:].strip().split('•')[0].strip().lower() if google_soup.find_all(class_='PdOqHc') else 'Not available'

        # Return all scraped data as JSON
        return jsonify({
            'ticker': ticker,
            'screener_data': {
                'company_name': comp_name,
                'Market_Cap': cap,
                'Current_Price': current_p,
                'highlow': highlow,
                'PE_ratio': pe,
                'Book_value': book_value,
                'Dividend': dividend,
                'roce': roce,
                'roe': roe,
                'Face_Value': face_value
            },
            'google_finance_data': {
                'day_range': day_range,
                'year_range': year_range,
                'primary_exchange': primary_exchange,
                'revenue': revenue_c,
                'operating_expense': opt_ex_c,
                'net_income': net_i_c,
                'net_profit_margin': net_p_m,
                'earnings_per_share': earning_p_share,
                'ebitda': ebitda,
                'logo': logo,
                'about': about
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)