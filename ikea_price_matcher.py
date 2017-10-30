#!/usr/bin/env python

import datetime
import urllib
import email.utils
import smtplib
import locale
from email.mime.text import MIMEText
from bs4 import BeautifulSoup, Comment

file_name = 'ikea_test.txt'
s = '|'
data_num = 5
price_tag_number = 6
url = 'http://www.ikea.com/fi/fi/catalog/products/'
locale.setlocale(locale.LC_ALL, '')
locale.setlocale(locale.LC_NUMERIC, "en_DK.UTF-8")
sender = 'ikeabot@example.org'
recipient = 'your_email@example.com'

def sendEmail(msg_string):
    msg = MIMEText(msg_string)
    msg['To'] = email.utils.formataddr(('Recipient', recipient))
    msg['From'] = email.utils.formataddr(('IKEA Price Watch Bot', sender))
    msg['Subject'] = 'Price matching for your ikea purchase.'

    server = smtplib.SMTP('localhost:25')
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()

def findPrice(name, a_number, p_price):
    print 'Searching price for %s' % name
    a_number = int(a_number)
    p_price = float(p_price)
    search_response = urllib.urlopen(url + str(a_number))
    search_result = search_response.read()
    soup = BeautifulSoup(search_result, 'html.parser')
    min_price = p_price
    res_str = ''
    for i in range(price_tag_number):
        search_id = 'price' + str(i + 1)
        price_tag = soup.find(id=search_id) 
        if price_tag != None:
            price_tag = price_tag.find_all(text=lambda t: not isinstance(t, Comment))
            for price_tag_item in price_tag:
                price_unicode = str(price_tag_item)
                price_unicode_str = unicode(price_unicode).strip('\r\n\t$ ')
                try:
                    price = locale.atof(price_unicode_str)
                    print 'Got a price %.2f' % price
                    if price < min_price:
                        min_price = price
                except ValueError:
                    print 'Has an empty price tag'
    if min_price != p_price:
        res_str = '%s has a lower price than your purchase! Purchase Price: %.2f Current Price %.2f' % (name, p_price, min_price)
        sendEmail(res_str)
    else:
        res_str = '%s has the same price as your purchase.' % name
    return res_str

def main():
    f = open(file_name, 'r') 
    top = f.readline()
    contents = [top]
    c_time = datetime.datetime.now()
    msg_string = ''
    for line in f:
        data_list = line.strip().split("|")
        p_date = datetime.datetime.strptime(data_list[3], '%Y-%m-%d %H:%M:%S')
        end_date = p_date + datetime.timedelta(days=90)
        res_str = ''
        if c_time < end_date:
            res_str = findPrice(data_list[0], data_list[1], data_list[2])

            last_check_date = c_time.strftime("%Y-%m-%d %H:%M:%S\n")
            if len(data_list) < data_num:
                data_list.append(last_check_date)
            else:
                data_list[data_num - 1] = last_check_date
            contents.append(s.join(data_list))
        else:
            res_str = '%s passed the price matching window and will be taken out from the program.' % data_list[0]
        msg_string += res_str + '\n'
    with open(file_name, 'w') as f:
        f.writelines(contents)

    print msg_string
    #sendEmail(msg_string)

if __name__ == '__main__':
    main()

