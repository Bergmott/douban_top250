import urllib.request as req
import urllib.parse#解析器

#获取一个get请求
# response = req.urlopen("http://www.baidu.com")#获取网页数据并保存在response中
# print(response.read().decode('utf-8'))#对获取到的网页源码机型utf-8解码，使得换行符和中文等符号可以正常显示


#获取一个post请求  
#httpbin.org可以作为测试网址
# import urllib.parse#解析器
# data=bytes(urllib.parse.urlencode({"hello":"world"}),encoding='utf-8')
# response =req.urlopen("http://httpbin.org/post",data=data)#封装数据，模拟用户真实登录时使用post请求
# print(response.read().decode('utf-8'))

#超时处理
# try:
#     response=req.urlopen("http://httpbin.org/get",timeout=0.01)
#     print(response.read().decode('utf-8'))
# except urllib.error.URLError as e:
#     print("time out!")

#http error 418：表示被发现是爬虫，即我是一个茶壶。
#response.status状态码      
#response.getheaders()头部信息


url="https://www.douban.com"
headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56"
    }

request=req.Request(url=url,headers=headers)
response=req.urlopen(request)
print(response.read().decode("utf-8"))