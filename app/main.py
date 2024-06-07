# Uncomment this to pass the first stage
import socket
import threading
import sys
import gzip
def verifyEncodind(encodeDico,texte):
    print (encodeDico)
    if encodeList := encodeDico.get("Accept-Encoding", None):
        print(encodeList)
        if "gzip" in encodeList:
            print('true')
            body = gzip.compress(texte)
            print(body)
            res = f'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(body)} \r\n\r\n'.encode()+ body
            print("send1")
        else:
            print("false")
            res = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(texte)} \r\n\r\n{texte}'.encode()
            print("send2")
        return res
    else:
        res = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(texte)} \r\n\r\n{texte}'.encode()
        print("send3")
        return res
def getFile(dir,file):
    try:
        with open(f"/{dir}/{file}", "r") as f:
            body = f.read()
            res = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
        return res
    except Exception as e:
        res = f"HTTP/1.1 404 Not Found\r\n\r\n".encode()
        return res
def postFile(dir,file,req_data):
    try:
        with open(f"/{dir}/{file}", "w") as f:
            body = req_data[-1]           
            f.write(body)                        
        res = f"HTTP/1.1 201 Created\r\n\r\n".encode()
        return res
    except Exception as e:
        print(e)
        res = f"HTTP/1.1 404 Not Found\r\n\r\n".encode()
        return res

def c_handler(conn):
    with conn :
        data = conn.recv(1024).decode()
        if not data :
            return
        request_data = data.split("\r\n")
        print (request_data)
        method = request_data[0].split(" ")[0]
        path= request_data[0].split(" ")[1]
        if path == "/":
            response =b"HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            string = path.split("/echo/")[1]
            if  not request_data[2] == "":
                encoding =request_data[2].split(" :")            
                key, values = ",".join(map(str, encoding)).split(": ", 1)
                values_list = [value.strip() for value in values.split(",")]
                encode_dict = {key: values_list}
                response = verifyEncodind(encode_dict,string.encode())     
            else:
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string)} \r\n\r\n{string}'.encode()
        elif path == '/user-agent':
            user_agent = request_data[2].split(" ")[1]
            print(user_agent)
            response =f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
        elif path.startswith("/files"):
            filename = path.split("files/")[1]
            if len(sys.argv) > 1:
                directory =sys.argv[2]
            else:
                directory = ""
            if method == "GET":
                response = getFile(directory,filename)
            if method == "POST" :
                response = postFile(directory,filename,request_data)
        else:
            response =b"HTTP/1.1 404 Not Found\r\n\r\n"
        conn.send(response)
def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, _ = server_socket.accept()  # wait for client
        threading.Thread(target=c_handler, args=(client,)).start()
   
if __name__ == "__main__":
    main()
