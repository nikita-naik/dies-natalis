import pandas as pd
from datetime import date
import random
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailTemplate:
    email = """\
    <html>
    <body style="color: black";>
    <section class="box" style='border: 0.2rem dotted grey; margin: auto; width: 80%; padding: 5%; font-family: "Trebuchet MS";'>
      <div class="header" style="text-align: center; color: black; font-size: 1.5rem; font-weight:normal;">
        <h1 style="color: black;">happy birthday, $nickname!</h1>
        <p>you're one year closer to death </p>
        <div class="message" style="text-align: justify; color: black; font-size: 1rem; font-weight:normal; padding: 2.5%;">
        <h4>I'm Nik circa January 2021, and I’m writing to you to circumvent future Nik’s absentmindedness in the very likely event that she forgets today. this email message serves as both birthday wish and reminder.<br><br>and so happy cake day, friend. I hope for you the very best of days and a lifetime to match. often I reminisce about the day we met at $meeting_place and all the time we have spent $regular_activity. one of my favourites was the time we $favourite_hang. that was something! $reminder always make me think of you.<br><br>now you may think it's silly to automate a birthday message to your friends. might I remind you, though, that you too have been plenty silly? remember the time you $silly_thing? yeah, me too.<br><br>all this to say... I have thoroughly enjoyed our shenangians and I'm grateful to have you around, amico mio. let us go on.<br><br>over to you, future Nik. bring it home.<br><br>N</h4>  
        </div>
        <div class="footnote" style="text-align: center; color: grey; font-size: 0.75rem; font-style:italic;">
        <h5>Your feedback is valuable to us! Email bugs@nikitanaik.com with any comments or questions you might have. JK — don't really. It's not like anybody cares about personal development around here.</h5>
        </div>
      </div> 
    </section>
    </body>
    </html>
    """

    @staticmethod
    def get_body(nickname, meeting_place, regular_activity, favourite_hang, reminder, silly_thing):
        t = Template(EmailTemplate.email)
        return t.substitute(nickname=nickname, meeting_place=meeting_place, regular_activity=regular_activity,
                            favourite_hang=favourite_hang, reminder=reminder, silly_thing=silly_thing)


def read_df(filepath, date_col, rename_dict=None, keep_cols=None, date_format='%d/%m/%Y'):
    df = pd.read_csv(filepath)

    if rename_dict is not None:
        df.rename(rename_dict, axis=1, inplace=True)

    if keep_cols is not None:
        df.drop([col for col in df.columns if col not in keep_cols], axis=1, inplace=True)

    df[date_col] = pd.to_datetime(df[date_col], format=date_format)
    df['month'] = pd.DatetimeIndex(df[date_col]).month
    df['day'] = pd.DatetimeIndex(df[date_col]).day
    df = df[(df['month'] == date.today().month) & (df['day'] == date.today().day)]
    df.drop(['month', 'day'], axis=1, inplace=True)

    return df


def create_dicts(df):
    list_of_dicts = []
    for row in range(len(df)):
        keys = df.columns.tolist()
        values = df.iloc[row, :].values.tolist()
        list_of_dicts.append({keys[i]: values[i] for i in range(len(keys))})

    return list_of_dicts


def send_email(server, port, sender_email, sender_password, list_of_dicts, cc = None):
    connection = smtplib.SMTP(server, port)
    connection.ehlo()
    connection.starttls()
    connection.login(sender_email, sender_password)

    for friend in list_of_dicts:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "it's your birthday, or something"
        msg['From'] = 'Nikita Naik'
        msg['To'] = friend.get('email_address')

        msg.attach(MIMEText(EmailTemplate.get_body(friend.get('nickname'), friend.get('meeting_place'),
                                                   friend.get('regular_activity'), friend.get('favourite_hang'),
                                                   friend.get('reminder'), friend.get('silly_thing')), 'html'))

        connection.sendmail(sender_email, friend.get('email_address'), msg.as_string())

    connection.quit()


if __name__ == '__main__':

    # read birthdays .csv as dataframe and retain rows where birthday is today's date
    diebus = read_df('diebus.csv', 'birthday')

    # convert dataframe to a list of dictionaries
    diebus_dict = create_dicts(diebus)

    # send email(s) by looping over all dictionaries if list is not empty (password is a placeholder)
    if diebus_dict:
        send_email('smtp.gmail.com', 587, 'friendships@nikitanaik.com', password, diebus_dict, 'niknaik97@gmail.com')
