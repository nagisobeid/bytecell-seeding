
 
class Mail:
    def __init__(self, sendr, recvr, port, password, file):
        self.sendr = sendr
        self.recvr = recvr
        self.port = port
        self.password = password
        self.file = file
        #self.body = body
        self.context = ssl.create_default_context()
        self.message = 0

    def checkType(self):
        message = MIMEMultipart()
        message["From"] = self.sendr
        message["To"] = self.recvr
        message["Subject"] = "BMPRICEDATA"
        #filename = self.file  # In same directory as script
        ctype, encoding = mimetypes.guess_type(self.file)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)
        if maintype == "text":
            fp = open(self.file)
            # Note: we should handle calculating the charset
            attachment = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "image":
            fp = open(self.file, "rb")
            attachment = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "audio":
            fp = open(self.file, "rb")
            attachment = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(self.file, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=self.file)
        message.attach(attachment)
        self.message = message
        #text = message.as_string()
    
    def send(self):
        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.sendr, self.password)
            server.sendmail(self.sendr, self.recvr, self.message.as_string())
        