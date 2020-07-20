from lxml import etree
import time
import re


def tojson():
    xml_file = open('one.html', encoding='utf-8').read()

    cnt = ''.join(re.findall(r'content":"(.*?)"}', xml_file, re.S) or '').replace('<br>', '').replace('\xa0',
                                                                                                      '').replace(
        '<br />', '').replace('&nbsp;', '').replace('</strong>', '').replace('<strong>', '')
    if '<iframe' in cnt:
        cnt = ''.join(re.findall(r'(.*?)<iframe', cnt, re.S) or '')
    if '<div' in cnt:
        cnt = ''.join(re.findall(r'(.*?)<div', cnt, re.S)[0] or '')
    if 'allow=' in cnt:
        cnt = ''.join(re.findall(r'(.*?)allow=', cnt, re.S)[0] or '')
    print(cnt)

    # text_tree = etree.HTML(xml_file)
    # trs = text_tree.xpath('//div[@class=" news-list"]')
    # cont = ''
    # cont += ''.join(text_tree.xpath('//*[@id="articleBody"]/section[2]/p/text()') or '')
    # cont += ''.join(text_tree.xpath('//*[@id="articleBody"]/section[2]/div[3]/span//text()') or '')
    # print(''.join(text_tree.xpath('//*[@id="articleBody"]/section/p//text()') or ''))
    # for tr in trs:
    #     detail = dict()
    #     href_url = ''.join(tr.xpath('div/a/@href') or '')
    #     if href_url == '':
    #         continue
    #     detail['url'] = href_url
    #     print(detail)


def toxml():
    xml_file = open('one.html', encoding='utf-8').read()
    text_tree = etree.HTML(xml_file)
    trs_hot = text_tree.xpath('//*[@id="form1"]/div[7]/div[6]/div[1]/div[2]/div')  # hot
    trs = text_tree.xpath('//*[@id="body_body_myNewsList_upList"]/div')
    for tr_hot in trs_hot:
        detail = dict()
        href_url = ''.join(tr_hot.xpath('div[2]/a/@href') or '')
        if href_url == '':
            continue
        detail['url'] = href_url
        print(detail)
    for tr in trs:
        detail = dict()
        href_url = ''.join(tr.xpath('div[3]/a/@href') or '')
        if href_url == '':
            continue
        detail['url'] = href_url
        print(detail)


def two():
    xml_file = open('two.html', encoding='utf-8').read()
    text_tree = etree.HTML(xml_file)
    trs = text_tree.xpath('//*[@id="Zoom"]//text()')
    print(trs)


toxml()
