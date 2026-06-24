from flask import Flask, request
from bs4 import BeautifulSoup
import cloudscraper
from datetime import datetime

app = Flask(__name__)

def scrape_football_data(target_date):
    url = f"https://www.forebet.com/en/football-predictions/predictions-1x2/{target_date}"
    
    # সাধারণ requests এর বদলে cloudscraper ব্যবহার করা হচ্ছে
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    try:
        response = scraper.get(url, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = []
            
            match_rows = soup.find_all('div', class_='rcnt')
            
            for row in match_rows:
                try:
                    home_team = row.find('div', class_='homeTeam').text.strip()
                    away_team = row.find('div', class_='awayTeam').text.strip()
                    prediction = row.find('div', class_='predict').text.strip()
                    probability = row.find('div', class_='prob').text.strip()
                    
                    matches.append({
                        "home": home_team,
                        "away": away_team,
                        "prediction": prediction,
                        "probability": probability 
                    })
                except AttributeError:
                    continue
                    
            return matches, None
        else:
            return None, f"Forebet সার্ভার ব্লক করেছে (Status: {response.status_code})"
    except Exception as e:
        return None, f"স্ক্র্যাপিং এরর: {str(e)}"

@app.route('/')
def home():
    selected_date = request.args.get('date')
    if not selected_date:
        selected_date = datetime.now().strftime("%Y-%m-%d")
        
    match_data, error = scrape_football_data(selected_date)
    
    html_content = f"<h2>ফুটবল প্রেডিকশন স্ক্র্যাপার ({selected_date})</h2>"
    
    if error:
        html_content += f"<p style='color:red;'><strong>⚠️ সমস্যা হয়েছে:</strong> {error}</p>"
        html_content += "<p style='color:red;'>অ্যান্টি-বট সিকিউরিটির কারণে ক্লাউড সার্ভার থেকে ডেটা আনা যাচ্ছে না। সবচেয়ে ভালো হয় কোডটি আপনার নিজের কম্পিউটারে রান করলে।</p>"
    else:
        html_content += "<ul>"
        if match_data and len(match_data) > 0:
            for item in match_data:
                home_team = item['home']
                away_team = item['away']
                prediction = item['prediction']
                prob = item['probability']
                
                pred_msg = ""
                if prediction == '1': pred_msg = f"{home_team} জিতবে"
                elif prediction == '2': pred_msg = f"{away_team} জিতবে"
                elif prediction == 'X': pred_msg = "ম্যাচ ড্র হবে"
                else: pred_msg = prediction
                
                html_content += f"<li>🏆 <strong>{home_team} VS {away_team}</strong><br>"
                html_content += f"💡 <strong>প্রেডিকশন:</strong> <span style='color: #007BFF;'>{pred_msg}</span> | "
                html_content += f"📊 <strong>সম্ভাবনা:</strong> {prob}</li><br>"
        else:
            html_content += "<li>এই তারিখে কোনো ডেটা স্ক্র্যাপ করা যায়নি।</li>"
        html_content += "</ul>"
        
    html_content += """
    <hr>
    <h3>অন্য তারিখের ডেটা স্ক্র্যাপ করুন:</h3>
    <form action="/" method="get">
        <input type="date" name="date" required>
        <button type="submit">ডেটা আনুন</button>
    </form>
    """
    
    return html_content

if __name__ == "__main__":
    app.run(debug=True)
