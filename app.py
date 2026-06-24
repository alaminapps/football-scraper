from flask import Flask, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# ওয়েব স্ক্র্যাপিং ফাংশন
def scrape_football_data(target_date):
    # Forebet ওয়েবসাইটের প্রেডিকশন পেজের URL
    url = f"https://www.forebet.com/en/football-predictions/predictions-1x2/{target_date}"
    
    # ওয়েবসাইট যেন বুঝতে না পারে যে এটি একটি বট, তাই ইউজারের ব্রাউজারের মতো Header পাঠানো হচ্ছে
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # রিকোয়েস্ট সফল হলে (Status 200) স্ক্র্যাপিং শুরু হবে
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = []
            
            # Forebet-এর HTML স্ট্রাকচার থেকে ম্যাচের সারিগুলো (Rows) খোঁজা
            # ওয়েবসাইট তাদের ডিজাইন পরিবর্তন করলে এই ক্লাসগুলোর নাম আপডেট করতে হতে পারে
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
                        "prediction": prediction,  # 1 (Home Win), X (Draw), 2 (Away Win)
                        "probability": probability # জেতার সম্ভাবনা %
                    })
                except AttributeError:
                    # কোনো ডেটা মিসিং থাকলে সেই সারিটি বাদ দিয়ে পরেরটিতে যাবে
                    continue
                    
            return matches, None
        else:
            return None, f"ওয়েবসাইট অ্যাক্সেস করা যাচ্ছে না (Status: {response.status_code})"
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
        html_content += "<p style='color:red;'>PythonAnywhere-এর ফ্রি অ্যাকাউন্টে সাধারণ ওয়েবসাইট স্ক্র্যাপ করা ব্লক করা থাকতে পারে।</p>"
    else:
        html_content += "<ul>"
        if match_data and len(match_data) > 0:
            for item in match_data:
                home_team = item['home']
                away_team = item['away']
                prediction = item['prediction']
                prob = item['probability']
                
                # প্রেডিকশন অনুযায়ী মেসেজ সেট করা
                pred_msg = ""
                if prediction == '1': pred_msg = f"{home_team} জিতবে"
                elif prediction == '2': pred_msg = f"{away_team} জিতবে"
                elif prediction == 'X': pred_msg = "ম্যাচ ড্র হবে"
                else: pred_msg = prediction
                
                html_content += f"<li>🏆 <strong>{home_team} VS {away_team}</strong><br>"
                html_content += f"💡 <strong>প্রেডিকশন:</strong> <span style='color: #007BFF;'>{pred_msg}</span> | "
                html_content += f"📊 <strong>সম্ভাবনা:</strong> {prob}</li><br>"
        else:
            html_content += "<li>এই তারিখে কোনো ডেটা স্ক্র্যাপ করা যায়নি। সম্ভবত আজ কোনো ম্যাচ নেই অথবা ওয়েবসাইটের ডিজাইন আপডেট হয়েছে।</li>"
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