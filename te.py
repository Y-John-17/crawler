import re
from lxml import html
etree = html.etree
import asyncio
from pyppeteer import launch
import time
import os
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

async def switch(pages, start_url,Info):
    start_time = time.time()
    #'headless': False如果想要浏览器隐藏更改False为True
    browser = await launch(options={'headless': False,                  # 设置无头浏览器
                                    'userDataDir': r'D:\temporary',     # 自定义用户目录
                                    'args': ['--no-sandbox',            # 无沙盒模式运行
                                        '--window-size=1440,900',       # 自定义屏占比，并在后面的setViewport参数中渲染
                                        '--disable-infobars'],          # 禁用浏览器正在被自动化的提示
                                    'dumpio': True,                     # 限制内存使用，防止页面卡住
                                    'fullPage': True,
                                    'waitUntil': 'networkidle2'})
    page = await browser.newPage()                                      # 创建一个新的浏览页面
    # 开启js
    await page.setJavaScriptEnabled(enabled=True)
    await page.setViewport({'width':1440,'height':900})                 # 渲染屏占比
    await page.setUserAgent(
        # 设置请求头伪装爬虫
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
    # js注入防止被页面让位自动化执行脚本的爬虫软件
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.goto(start_url,options={'waitUntil': 'networkidle2','fullPage':True})  # 前往目标网站
    await page.waitFor(2500);                                           # 设置等待加载，防止页面加载失败
    # 滑动js  动态加载
    await page.evaluate('''async () => {
                    await new
                Promise((resolve, reject) => {
                    var
                totalHeight = 0;
                var
                distance = 100;
                var
                timer = setInterval(() => {
                    var
                scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;
 
                if (totalHeight >= scrollHeight){
                clearInterval(timer);
                resolve();
                }
                }, 100);
                });
        }''')
    await asyncio.sleep(3)                                            # 设置等待加载，防止页面加载失败

    # 根据页数轮转爬取第61-i个商品
    if pages%2:
        num = 36
    else:
        num = 25
    # 返回目标商品url
    link = await page.Jeval('#J_goodsList > ul > li:nth-child({}) > div > div.p-img > a'.format(num),'el => el.href')
    print(link)

    ## 以下是信息爬取部分
    # 跳转函数，获取主页面下每个商品的url
    await page.goto(link)
    await page.waitFor(2500)
    Price = await page.Jeval('.itemInfo-wrap .summary-price-wrap .summary-price .p-price .price','el => el.innerText')
    Name = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(1)','el => el.title')
    wt = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(3)','el => el.title')
    Weight = re.sub('kg','',wt)
    Screen_color_gamut = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(5)','el => el.title')
    Type = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(6)','el => el.title')
    Thickness = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(8)','el => el.title')
    it3 = await page.Jx('//div[@data-tab="item"]/div[1]/ul[2]/li[contains(string(),"内存容量")]')
    for i in it3:
        Memory=await (await i.getProperty('title')).jsonValue()
    it4 = await page.Jx('//div[@data-tab="item"]/div[1]/ul[2]/li[contains(string(),"支持IPv6")]')
    for i in it4:
        IP=await (await i.getProperty('title')).jsonValue()
    it5 = await page.Jx('//div[@data-tab="item"]/div[1]/ul[2]/li[contains(string(),"颜色")]')
    for i in it5:
        Color=await (await i.getProperty('title')).jsonValue()
    Processor = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(19)','el => el.title')
    Screen_refresh_rate = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(17)','el => el.title')
    Graphics_card_model = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(20)','el => el.title')
    Screen_size = await page.Jeval('#detail > div.tab-con > div:nth-child(1) > div.p-parameter > ul.parameter2.p-parameter-list > li:nth-child(21)','el => el.title')
    it1= await page.Jx('//div[@data-tab="item"]/div[1]/ul[2]/li[contains(string(),"固态硬盘")]')
    for i in it1:
        SDD=await (await i.getProperty('title')).jsonValue()
    it2 = await page.Jx('//div[@data-tab="item"]/div[1]/ul[2]/li[contains(string(),"机械硬盘")]')
    for i in it2:
        HDD=await (await i.getProperty('title')).jsonValue()
    print(Price,Name,Weight,Screen_color_gamut,Type,Thickness,Memory,IP,Color,Processor,Screen_refresh_rate,Graphics_card_model,Screen_size,SDD,HDD)
    # 数据存储
    Info.append([Price,Name,Weight,Screen_color_gamut,Type,Thickness,Memory,IP,Color,Processor,Screen_refresh_rate,Graphics_card_model,Screen_size,SDD,HDD])
    # 点击评价按钮，爬取评论
    await page.click('#detail > div.tab-main.large > ul > li:nth-child(5)')
    await page.waitFor(3000)
    # 爬取好评率
    # rate = await page.Jeval('#comment > div.mc > div.comment-info.J-comment-info > div.comment-percent > div','el => el.innerText')
    # pprint(rate)
    # pprint(pages)
    # 点击好评
    await page.click('#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > ul > li:nth-child(5) > a')
    await page.waitFor(2500)
    c1 = await page.content()
    comm_1 = etree.HTML(c1)
    comment_1 = comm_1.xpath('//*[@id="comment-4"]/div/div[2]/p/text()')
    # 点击中评
    await page.click('#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > ul > li:nth-child(6) > a')
    await page.waitFor(2500)
    c2 = await page.content()
    comm_2 = etree.HTML(c2)
    comment_2 = comm_2.xpath('//*[@id="comment-5"]/div/div[2]/p/text()')
    # 点击差评
    await page.click('#comment > div.mc > div.J-comments-list.comments-list.ETab > div.tab-main.small > ul > li:nth-child(7) > a')
    await page.waitFor(2500)
    c3 = await page.content()
    comm_3 = etree.HTML(c3)
    comment_3 = comm_3.xpath('//*[@id="comment-6"]/div/div[2]/p/text()')
    await browser.close()                                               # 关闭浏览器
    print('爬取信息耗时：',time.time() - start_time )

    # 数据可视化(词云绘制)
    Comment = []
    for i in comment_1:
        Comment.append(i)
    for i in comment_2:
        Comment.append(i)
    for i in comment_3:
        Comment.append(i)
    print(Comment)
    text = []
    for i in Comment:
        t = re.sub('([^\u4e00-\u9fa5])', '', i)
        ty = jieba.lcut(t)
        for j in ty:
            text.append(j)
    print(text)
    words = Counter(text)
    print(words.most_common(10))
    wordscloud = WordCloud(
        background_color='white',  # 设置背景颜色 默认是black
        width = 900,
        height = 600,
        max_words = 100,  # 词云显示的最大词语数量
        font_path ='simhei.ttf',  # 设置字体 显示中文
        max_font_size = 99,  # 设置字体最大值
        min_font_size = 16,  # 设置子图最小值
        random_state = 50  # 设置随机生成状态，即多少种配色方案
    ).generate_from_frequencies(words)
    # 显示生成的词云图片
    fig = plt.figure()
    plt.imshow(wordscloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('{}.png'.format(pages))
def start():
    Info = []
    # 网页数量输入
    number = 2
    for pages in range(number):
        start_url = 'https://search.jd.com/Search?keyword=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&qrst=1&psort=3&suggest=1.def.0.SAK7%7CMIXTAG_SAK7R%2CSAK7_M_AM_L5381%2CSAK7_S_AM_R%2CSAK7_D_HSP_R%2CSAK7_SC_PD_R%2CSAK7_SM_PB_R%2CSAK7_SM_PRK_R%2CSAK7_SM_PRC_R%2CSAK7_SM_PRR_R%2CSAK7_SS_PM_R%7C&wq=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&shop=1&psort=3&pvid=9682685401bf42fa81d3d8fe09e1b0d7&page={0}&s={1}&click=0'.format(pages * 2 + 1, pages * 60 + 1)
        asyncio.get_event_loop().run_until_complete(switch(pages,start_url,Info))
    print(Info)
if __name__ == '__main__':
    start()