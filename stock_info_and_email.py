from turtle import down
import yfinance as yf
import json
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

def send_email_with_data(contents, subject = "DAILY EMAIL FUTURES", sender_email = config.email, receiver_email = ["koriv.tt7@gmail.com"]):
    receiver_email = ",".join(receiver_email)

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    body = "This is an email with a Tesla Fleet Information\n"

    body += str(contents)

    print("SENDING EMAIL WITH THE FOLLOWING")
    print(body)

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    text = message.as_string()
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, config.password)
        server.sendmail(sender_email, receiver_email, text)

def get_ticker_info(name="SPY", tail=5):
    '''
    This gets the ticker information for a given name. Just gathers the Open, Close, and Volume for the last 5 days. 
    You can tailor it to whatever you want, but just because we're trying to figure out what the sentiment for the
    next day of trading is, I don't think it's entirely necessary. 
    '''
    df = yf.download(name)  
    ret = df.tail(tail)
    average = [] # compiling a list of the percent change during the day
    vol_list = [] #compiling a list of all of the volume differences to compare row by row
    vol_change_list = [] # compiling a list of the volume changes between days
    for index, row in ret.iterrows():
        _open, _close, _vol = row['Open'], row['Close'], row['Volume']
        perc_change = (1 - _open/_close)*100
        vol_change = None
        if vol_list != []:
            vol_change = (1- (vol_list[-1]/ _vol))*100
            vol_change_list.append(vol_change)
        else:
            vol_change_list.append("NaN")
        vol_list.append(_vol)
        average.append(perc_change)
        
        print(_open, _close, f"{'%.3f'%(perc_change)}%", vol_change)
    ret["Percent_Change"] = average
    ret["Volume_Change"] = vol_change_list
    print(f'average change for {name}: {sum(average)/len(average)}')
    return ret

def prev_day_and_week_stats(name, dataframe):
    '''
    This is just compiling the stats using a dataframe. I'm operating under the assumption
    that Positive Volume and Positive %Change == Good trading day for name.
    Positive Volume and Negative %Change == Bad Trading, sell off
    Negative Volume and Positive %Change == People scared to get in, but overall good trading
    Negative Volume and Negative %Change == Unsure, essentially stagnant, but could potentially turn around
    ... so on and so forth. A truth table needs to be created, but I'm just formatting everything
    in html to put in an email. 
    '''
    ret_str = ''
    last = dataframe.tail(1)
    direction = None
    for index, row in last.iterrows():
        if row['Percent_Change'] > 0:
            ret_str += f"{name} increased by {'%.3f'%(row['Percent_Change'])}% on {index} with {'%.3f'%(row['Volume_Change'])}%.\n"
            if row['Percent_Change'] > 0.5:
                if row['Volume_Change'] > 0:
                    ret_str += f"Volume is positive, expect {name} to trade well.\n"
                    direction = True
                else:
                    ret_str += f"Volume is negative, expect small movements in daily spot.\n"
                    direction = True
            else:
                if row['Volume_Change'] > 0:
                    ret_str += f"Volume is positive, however percent change is less than 50 bps. Be cautious of trading and daily moves of {name}. Stagnant or declining growth.\n"
                    direction = False
                else:
                    ret_str += f"Volume is negative, expect small movements in daily spot. Stagnant or slightly declining growth.\n"
                    direction = False
        else:
            ret_str += f"{name} decreased by {'%.3f'%(row['Percent_Change'])}% on {index} with {'%.3f'%(row['Volume_Change'])}%.\n"
            if row['Percent_Change'] < -0.5:
                if row['Volume_Change'] > 0:
                    ret_str += f"Likely a sell off, expect {name} spot to decline in price rapidly due to positive volume and percent change more than -50bps.\n"
                    direction = False
                else:
                    ret_str += f"Volume is negative, expect small movements in daily spot.\n"
                    direction = False
            else:
                if row['Volume_Change'] > 0:
                    ret_str += f"{name} to potentially resist previous day low or stay stagnant.\n"
                    direction = True
                else:
                    ret_str += f"Volume is negative, expect small movements in daily spot or potential price improvement.\n"
                    direction = True
    return ret_str, direction
            



def main():
    def_list = ["ES=F", "YM=F", "NQ=F"]

    html = ''
    prediction_bool_ls = [] # what do we think the general direction is going to be for given indictators
    
    for name in def_list:
        html += f"{str(yf.Ticker(name).info['shortName'])} Daily Information\n"
        df = get_ticker_info(name)
        pred_str, dir = prev_day_and_week_stats(name, df)
        html += pred_str + '\n'
        html += str(df)
        html += "\n\n"
        prediction_bool_ls.append(dir) 
    
    true = prediction_bool_ls.count(True)
    false = prediction_bool_ls.count(False)
    subj = None
    if true > false:
        subj = "Positive Market Direction"
    else:
        subj = "Negative Market Direction"
    
    send_email_with_data(contents=html, subject=f"Futures Email Volume Based Market Prediction: {subj}")
    # print(html, prediction_bool_ls)
    

# print(json.dumps(spy.info, sort_keys=False, indent=4))

if __name__ == "__main__":
    # print(str(yf.Ticker("ES=F").info['longName']))
    # exit()
    main()