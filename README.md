# EasyChatRoom

## Before use

> Install python and python package

```cmd
pip install flask flask_socketio secrets datetime uuid
```

> Certificate application (make it by yourself)
>
> You can ignore it but it will be any risk to be monitor by your IT guys

> Modify the code to point to the correct certificate that you have applied.
>
> If you ignore step 2 You can ignore this step and common out the ssl_context=('server.crt', 'server.key')  # 指定证书

```python
# ./app.py
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',  # 允许所有IP访问
        port=WebPort,
        ssl_context=('server.crt', 'server.key')  # 指定证书
    )
```

> Request your colleague or friend to install the certificate that you have applied.
>
> You can ignore this step if you ignore the step3

## Running Instructions

> Run the bat file to get the app run 

```cmd
python app.py password123 10008
pause
```

password123:password of the chatroom 

10008：port of app run

user name can be whatever you want

