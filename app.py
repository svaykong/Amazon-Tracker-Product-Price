import os
from dotenv import load_dotenv, find_dotenv
import requests
from bs4 import BeautifulSoup
import smtplib

# Kindle E-readers
url = 'https://www.amazon.com/Kindle-Paperwhite-Essentials-Bundle-including/dp/B09FC14SY5/ref=sr_1_3?keywords=Kindle%2BE-readers&pd_rd_r=fb27294a-06af-494d-8fdd-4a14cf1c53f9&pd_rd_w=AJ6SA&pd_rd_wg=mRyW3&pf_rd_p=b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&pf_rd_r=8QVR67FV6JKP80K3R1MG&qid=1651369269&sr=8-3&th=1#tech'
header = {
    "Accept-Language" : "en-US,en;q=0.9",
    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
}


def check_response_status_code(status_code):
    if status_code == 200:
        return True 
    else:
        raise Exception('The response status code not success: {}'.format(status_code))


def saveLogFile(dirName='logs/', fileName=None, mode='w', content=''):
    if fileName == None:
        raise Exception('You must provide fileName')

    # if fileName:
    #     split = fileName.split('.')
    #     if split[1] != 'txt':
    #         raise Exception('fileName must be a text file: {}'.format(fileName))
        
    with open(dirName + fileName, mode) as fs:
        fs.write(content)


def sendEmail(sender_email=None, receive_email=None, password=None, message=None):
    if not (sender_email or receive_email or message):
        raise Exception('Message info is incorrect, please check again')
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    login_res = server.login(sender_email, password)
    print('logoin res: {}'.format(login_res))

    status = login_res[1].decode('utf-8')
    if status.index('Accepted'):
        print('login success')
        print('type message: {}'.format(type(message)))
        print('message to be sent: ' + message)
        server.sendmail(sender_email, receive_email, message)
        print('Email has sent to: {}'.format(receive_email))
        server.quit()


if __name__ == '__main__':
    try :
        load_dotenv(find_dotenv())

        SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
        RECEIVE_EMAIL = os.environ.get('RECEIVE_EMAIL')
        PASSWORD = os.environ.get('PASSWORD')

        pass
        # go to amazon offical website and check the above product:
        response = requests.get(url, headers=header)
        if check_response_status_code(response.status_code):
            # specific parser ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml")
            # getting the content from BeautifulSoup
            soup = BeautifulSoup(response.content, "lxml");

            # save content into a text file
            saveLogFile(fileName='product1.txt', content=soup.prettify())
            # save content into a html file
            saveLogFile(fileName='product1.html', content=soup.prettify())
            
            # getting product title
            product_title = soup.find(id="productTitle")
            print('product title dom content: {}'.format(product_title))

            if product_title:
                print('product title text: {}'.format(product_title.get_text().strip()))
                product_title = product_title.get_text().strip()
            else:
                raise Exception("Product title id maybe change plz check with a site again")
            
            # getting product price
            product_price = soup.find("span", class_="a-price a-text-price a-size-base")
            print("product price dom content: {}".format(product_price))

            if product_price:
                product_price = product_price.find("span", class_="a-offscreen")
                print('product price text: {}'.format(product_price.get_text().strip()))

                product_price = product_price.get_text().strip()
                product_price = float(product_price.split('$')[1])
                # print(product_price)
            # else:
            #     raise Exception("Product price span class maybe change plz check with a site again")

            # getting product bundle price
            product_bundle_price = soup.find("span", class_="a-price a-text-price a-size-medium apexPriceToPay")
            print("product bundle price dom content: {}".format(product_bundle_price))

            if product_bundle_price:
                product_bundle_price = product_bundle_price.find("span", class_="a-offscreen")
                print('product bundle rice text: {}'.format(product_bundle_price.get_text().strip()))

                product_bundle_price = product_bundle_price.get_text().strip()
                product_bundle_price = float(product_bundle_price.split('$')[1])
                # print(product_bundle_price)
            else:
                raise Exception("Product bundle price span class maybe change plz check with a site again")

            # set tracker price
            tracker_price = 130

            product_info = {}
            product_info['title'] = product_title
            if product_price:
                product_info['price'] = product_price
                product_info['bundle'] = product_bundle_price
            else:
                product_info['price'] = product_bundle_price

            # product_info["bundle"] = 129
            print(product_info)

            text, message = ('',) * 2
            subject = 'Amazon Tracker Product Price Alert'
            if product_info["bundle"] and product_info["bundle"] <= tracker_price:
                text  = 'The product is in your decision price \n'
                text += 'Let\'s check it out. \n'
                text += 'Product: ' + product_info["title"] + '\n'
                text += 'Price: $' + str(product_info["bundle"]) + '\n'
                text += 'Website: ' + url

                message = 'Subject: {}\n\n{}'.format(subject, text)

                sendEmail(SENDER_EMAIL, RECEIVE_EMAIL, PASSWORD ,message)

            elif product_info["price"] and product_info["price"] <= tracker_price:
                text  = 'The product is in your decision price \n'
                text += 'Let\'s check it out. \n'
                text += 'Product: ' + product_info["title"] + '\n'
                text += 'Price: $' + str(product_info["price"]) + '\n'
                text += 'Website: ' + url

                message = 'Subject: {}\n\n{}'.format(subject, text)
                
                sendEmail(SENDER_EMAIL, RECEIVE_EMAIL, PASSWORD ,message)

    except Exception as exception:
        print('exception: {}'.format(exception))
        





